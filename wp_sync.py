#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워드프레스(verdex.kr) → 정적 사이트 콘텐츠 동기화

대표님은 지금까지 하시던 대로 wp-admin 에서 글을 쓰시면 됩니다.
이 스크립트가 REST API 로 글을 받아와 content/wp-posts.json 에 저장하고,
대표이미지를 images/wp/ 에 내려받습니다. 그 다음 build.py 가 그 JSON 을 읽어
우리 디자인으로 뉴스룸과 글 페이지를 찍어냅니다.

    python3 wp_sync.py              # 전체 동기화
    python3 wp_sync.py --no-images  # 이미지 빼고 글만
    python3 wp_sync.py --limit 5    # 최신 5개만 (테스트용)

워드프레스 쪽에 설치할 플러그인은 없습니다. REST API 는 기본 기능입니다.
"""
import argparse, json, pathlib, re, sys, urllib.parse, urllib.request

WP_BASE = "https://www.verdex.kr"
ROOT    = pathlib.Path(__file__).resolve().parent
OUT     = ROOT / "content" / "wp-posts.json"
IMG_DIR = ROOT / "images" / "wp"
UA      = {"User-Agent": "verdex-static-build/1.0"}

# 워드프레스 카테고리 → 뉴스룸 필터 (전체/미디어보도/보도자료/칼럼)
CAT_MAP = {
    "탄소중립강좌": ("column", "칼럼"),
    "소식":        ("press",  "보도자료"),
    "언론보도":     ("media",  "미디어보도"),
}
CAT_DEFAULT = ("press", "보도자료")

# 저작권 — 미디어보도(외부 언론사 기사)는 전문을 절대 가져오지 않습니다.
# 제목·출처·날짜와 원문 링크만 저장하고, 본문은 비워 둡니다.
NO_FULLTEXT = {"media"}

# 본문에서 통째로 지울 것들 (Visual Composer 찌꺼기·스크립트·빈 껍데기)
DROP_BLOCKS = re.compile(
    r"<(script|style|iframe|noscript)\b.*?</\1>", re.S | re.I)
DROP_SHORTCODE = re.compile(r"\[/?vc_[^\]]*\]|\[/?et_pb_[^\]]*\]")
KEEP_TAGS = {"p","br","strong","b","em","i","u","h2","h3","h4","ul","ol","li",
             "blockquote","a","img","figure","figcaption","table","thead","tbody",
             "tr","th","td","hr","sup","sub"}


def api(path, **params):
    """REST API 호출 — 페이지네이션을 알아서 돌면서 전부 모아 옵니다."""
    out, page = [], 1
    while True:
        params["page"] = page
        url = f"{WP_BASE}/wp-json/wp/v2/{path}?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            total_pages = int(r.headers.get("X-WP-TotalPages") or 1)
            batch = json.load(r)
        out += batch
        if page >= total_pages or not batch:
            return out
        page += 1


def strip_tags(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def clean_html(html):
    """워드프레스 본문을 우리 .body-text 스타일이 먹는 순수 HTML 로 정리."""
    h = DROP_BLOCKS.sub("", html or "")
    h = DROP_SHORTCODE.sub("", h)
    h = re.sub(r"<!--.*?-->", "", h, flags=re.S)
    # 허용하지 않는 태그는 껍데기만 벗김 (안쪽 글은 살림)
    def unwrap(m):
        tag = m.group(2).lower()
        return m.group(0) if tag in KEEP_TAGS else ""
    h = re.sub(r"<(/?)([a-zA-Z0-9]+)[^>]*>", unwrap, h)
    # 인라인 style / class / id 제거 — 우리 CSS 가 책임집니다
    h = re.sub(r'\s(style|class|id|width|height|srcset|sizes|loading|data-[\w-]+)="[^"]*"', "", h)
    h = re.sub(r"(<p>\s*(&nbsp;)?\s*</p>)+", "", h)
    return re.sub(r"\n{3,}", "\n\n", h).strip()


def first_external_link(html):
    """미디어보도 글에서 언론사 원문 URL 을 찾아냅니다."""
    for m in re.finditer(r'href="(https?://[^"]+)"', html or ""):
        u = m.group(1)
        if "verdex.kr" not in u:
            return u
    return None


def download(url, session_seen):
    """대표이미지를 images/wp/ 로 내려받고 사이트 기준 상대경로를 돌려줍니다."""
    if not url:
        return None, None
    name = re.sub(r"[^\w.-]", "_", urllib.parse.unquote(url.rsplit("/", 1)[-1]))
    dest = IMG_DIR / name
    rel = f"images/wp/{name}"
    if name in session_seen or dest.exists():
        return rel, dest
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.write_bytes(r.read())
        session_seen.add(name)
        return rel, dest
    except Exception as e:
        print(f"  ! 이미지 실패 {url} — {e}")
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-images", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print(f"워드프레스에서 글을 가져옵니다 — {WP_BASE}")
    try:
        raw = api("posts", per_page=100, _embed=1, orderby="date", order="desc",
                  status="publish")
    except Exception as e:
        print(f"\n가져오기 실패: {e}")
        print("네트워크가 막혀 있거나 REST API 가 꺼져 있습니다.")
        print(f"브라우저로 {WP_BASE}/wp-json/wp/v2/posts 가 열리는지 확인해 보세요.")
        sys.exit(1)

    if args.limit:
        raw = raw[: args.limit]
    print(f"글 {len(raw)}개")

    seen, posts = set(), []
    for p in raw:
        emb = p.get("_embedded", {})
        names = [t.get("name") for g in emb.get("wp:term", []) for t in g
                 if t.get("taxonomy") == "category"]
        cat, label = CAT_DEFAULT
        for n in names:
            if n in CAT_MAP:
                cat, label = CAT_MAP[n]
                break
        img_rel, img_alt = None, ""
        media = emb.get("wp:featuredmedia") or []
        if media and not args.no_images:
            img_rel, _ = download(media[0].get("source_url"), seen)
            img_alt = strip_tags(media[0].get("alt_text") or p["title"]["rendered"])
        content = p["content"]["rendered"]
        external = first_external_link(content) if cat in NO_FULLTEXT else None
        posts.append({
            "id":       p["id"],
            "date":     p["date"][:10],
            "title":    strip_tags(p["title"]["rendered"]),
            "excerpt":  strip_tags(p["excerpt"]["rendered"])[:200],
            "cat":      cat,
            "cat_label": label,
            "wp_cats":  names,
            "wp_link":  p["link"],
            "image":    img_rel,
            "image_alt": img_alt,
            # 미디어보도는 본문을 저장하지 않습니다 (언론사 저작권)
            "html":     "" if cat in NO_FULLTEXT else clean_html(content),
            "external_url": external or (p["link"] if cat in NO_FULLTEXT else None),
        })
        mark = " ↗외부링크" if cat in NO_FULLTEXT else ""
        print(f"  · {p['date'][:10]}  [{label}]{mark} {posts[-1]['title'][:48]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n저장 → {OUT.relative_to(ROOT)}  ({len(posts)}개)")
    print("이어서:  python3 build.py")


if __name__ == "__main__":
    main()
