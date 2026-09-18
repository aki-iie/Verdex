#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verdex AI 사이트 v3 빌드 스크립트
  shell/   공통 껍데기 (site.css · header.html · footer.html · site.js · 홈 전용 파일)
  src/     페이지별 본문 (목업에서 추출한 콘텐츠 — 여기를 고치면 됨) + pages.json (제목·서브탭 메타)
  images/  사진
  site/    ← 생성 결과 (완성 HTML 42개 + index.html)

사용법:  python3 build.py
"""
import json, os, re, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SHELL, SRC, OUT = ROOT/"shell", ROOT/"src", ROOT/"site"
OUT.mkdir(exist_ok=True)

css    = (SHELL/"site.css").read_text(encoding="utf-8")
homecss= (SHELL/"home.css").read_text(encoding="utf-8")
header = (SHELL/"header.html").read_text(encoding="utf-8")
footer = (SHELL/"footer.html").read_text(encoding="utf-8")
js     = (SHELL/"site.js").read_text(encoding="utf-8")
pages  = json.load(open(SRC/"pages.json", encoding="utf-8"))
homejs = (SHELL/"home.js").read_text(encoding="utf-8")

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@400;500;700;800;900'
         '&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">\n'
         '<link rel="icon" href="images/brand/verdex-favicon.svg" type="image/svg+xml">\n'
         '<link rel="icon" href="images/brand/favicon-32.png" sizes="32x32">\n'
         '<link rel="apple-touch-icon" href="images/brand/apple-touch-icon.png">')

# ── 페이지 메타: 히어로 타입 · 메뉴 섹션 · 사진 자리 라벨 ─────────────────
PHOTO = {  # 사진형 히어로 (사진이 들어오면 images/ 에 넣고 photo 키에 파일명)
 "about-overview.html":   dict(sec="about",    label="사진 영역: 대표/팀 현장 컷 또는 오피스"),
 "about-leadership.html": dict(sec="about",    label="사진 영역: 대표 현장 컷 (와이드)"),
 "about-history.html":    dict(sec="about",    label="사진 영역: 설립 초기 사진 또는 현장"),
 "location.html":         dict(sec="about",    label="사진 영역: 사옥 외관 또는 왕십리 전경"),
 "business-overview.html":dict(sec="business", label="사진 영역: 5개 사업을 아우르는 대표 컷"),
 "service-impact-assessment.html": dict(sec="business", label="사진 영역: 위성사진·데이터 분석 화면"),
 "service-carbon-neutrality.html": dict(sec="business", label="사진 영역: 정부·지자체 협업 회의"),
 "service-esg.html":               dict(sec="business", label="사진 영역: ESG 보고서·사무실"),
 "service-smart-energy.html":      dict(sec="business", label="사진 영역: 공장·산업 설비"),
 "service-circular-economy.html":  dict(sec="business", label="사진 영역: 재활용·순환 공정"),
 "careers.html":          dict(sec="careers",  label="사진 영역: 팀 작업 장면"),
}
SEC = {"news":"news","columns-other":"news","column-":"news","press-":"news",
       "resources":"resources","resource-":"resources","contact":"contact","faq":"contact",
       "privacy":"", "terms":""}
def section_of(f):
    if f in PHOTO: return PHOTO[f]["sec"]
    for k,v in SEC.items():
        if f.startswith(k): return v
    return ""

# ── 히어로 조립 ────────────────────────────────────────────────────────────
def subtabs_html(tabs):
    if not tabs: return ""
    ACT = ' class="active"'
    return '<div class="subtabs">' + "".join(
        f'<a href="{h}"{ACT if act else ""}>{t}</a>' for h,act,t in tabs) + "</div>"

def hero_photo(f, m):
    p = PHOTO[f]
    photo = p.get("photo")
    img = f'<img class="bg" src="images/{photo}" alt="" style="opacity:1">' if photo else ""
    slot = "" if photo else f'<div class="slot">{p["label"]}</div>'
    eyebrow = f'<div class="eyebrow">{m["eyebrow"]}</div>' if m["eyebrow"] else ""
    lede = f'<p class="lede">{m["lede"]}</p>' if m["lede"] else ""
    return f'''<section class="phero" data-theme="dark">
  {img}<div class="veil"></div>{slot}
  <div class="wrap">
    {eyebrow}
    <h1>{m["h1"]}</h1>
    {lede}
    {subtabs_html(m["subtabs"])}
  </div>
</section>'''

def hero_band(f, m):
    top = ""
    if m["crumb"]:   top = f'<div class="crumb">{m["crumb"]}</div>'
    elif m["eyebrow"]: top = f'<div class="eyebrow">{m["eyebrow"]}</div>'
    lede = f'<p class="lede">{m["lede"]}</p>' if m["lede"] else ""
    by   = f'<div class="byline">{m["byline"]}</div>' if m["byline"] else ""
    upd  = f'<div class="updated">{m["updated"]}</div>' if m["updated"] else ""
    return f'''<section class="bhero" data-theme="dark">
  <div class="wrap">
    {top}
    <h1>{m["h1"]}</h1>
    {lede}{by}{upd}
    {subtabs_html(m["subtabs"])}
  </div>
</section>'''

def hero_subbar(f, m):
    """개요 페이지: 사진 히어로 대신 로고 바로 밑에 붙는 섹션 탭 바"""
    return f'''<div class="subbar">
  <div class="wrap">
    <span class="sb-title">{SEC_LABEL.get(section_of(f), "")}</span>
    {subtabs_html(m["subtabs"])}
  </div>
</div>'''

SUBBAR = {"about-overview.html", "about-leadership.html"}
SEC_LABEL = {"about":"회사 소개","business":"사업 분야","news":"뉴스룸","resources":"자료","careers":"채용","contact":"문의"}

LEADER_CSS = """
  .lead{background:var(--paper);padding-block:clamp(44px,5.2vw,104px)}
  .lead-grid{display:grid;grid-template-columns:minmax(280px,.8fr) 1.3fr;
    gap:clamp(30px,4.6vw,88px);align-items:start;max-width:none}
  .portrait{margin:0}
  .portrait img{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:center 22%;
    border-radius:6px;box-shadow:0 34px 64px -36px rgba(10,58,99,.5)}
  .portrait figcaption{margin-top:clamp(16px,1.7vw,26px)}
  .p-name{font-size:clamp(23px,2.2vw,40px);font-weight:900;letter-spacing:-.03em;color:var(--navy);line-height:1.2}
  .p-role{margin-top:7px;font-family:var(--mono);font-size:var(--fs-small);
    letter-spacing:.14em;font-weight:500;color:var(--brand)}
  .say blockquote{margin:clamp(16px,1.8vw,28px) 0 0;font-size:clamp(21px,2.5vw,44px);font-weight:800;
    line-height:1.5;letter-spacing:-.03em;color:var(--navy);text-wrap:balance}
  .say p{margin-top:clamp(14px,1.5vw,24px);max-width:64ch;font-size:var(--fs-body);
    line-height:1.95;color:var(--muted)}
  .sign{margin-top:clamp(28px,3vw,50px);padding-top:clamp(20px,2vw,32px);border-top:1px solid var(--line);
    display:flex;align-items:flex-end;gap:clamp(18px,2.2vw,36px);flex-wrap:wrap}
  .sign-slot{width:clamp(140px,13vw,196px);aspect-ratio:12/5;border:1.5px dashed #C3CDC2;border-radius:4px;
    background:#F1F4F0;display:grid;place-items:center;font-size:var(--fs-small);color:#8C9A8E}
  .sign-who{display:flex;flex-direction:column;gap:4px;font-size:var(--fs-small);color:var(--muted)}
  .sign-who b{font-size:var(--fs-h3);font-weight:800;letter-spacing:-.02em;color:var(--ink)}
  .career{padding-block:clamp(44px,5.2vw,104px)}
  .career-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(16px,2.2vw,40px);
    margin-top:clamp(28px,3.2vw,56px)}
  .career-grid div{border-top:2px solid var(--navy);padding-top:clamp(12px,1.5vw,20px)}
  .career-grid b{display:block;font-size:var(--fs-h3);font-weight:800;letter-spacing:-.02em;color:var(--navy)}
  .career-grid span{display:block;margin-top:8px;font-size:var(--fs-small);color:var(--muted)}
  .career-link{display:inline-block;margin-top:clamp(26px,2.8vw,44px);font-family:var(--mono);
    font-size:var(--fs-small);font-weight:700;letter-spacing:.05em;color:var(--brand)}
  @media (max-width:900px){ .lead-grid{grid-template-columns:1fr;gap:28px}
    .portrait img{max-width:420px} .career-grid{grid-template-columns:repeat(2,1fr)} }
  @media (max-width:560px){ .career-grid{grid-template-columns:1fr} }
"""

ABOUT_CSS = """
  .screen.about{min-height:calc(100svh - var(--hh) - 64px);scroll-snap-align:none}
  .about .stage{padding:clamp(18px,3.4vh,44px) 0 clamp(20px,4vh,48px)}
  .about .close{top:clamp(10px,1.4vw,28px)}
  @media (max-width:900px){ .screen.about{min-height:0} .about .stage{padding-block:34px 40px} }
"""

# ── 본문 보정 ──────────────────────────────────────────────────────────────
NEWS_JS = """
<script>
(function(){
  var buttons = document.querySelectorAll('.filter-btn');
  var rows = document.querySelectorAll('#newsList .news-row');
  function applyFilter(cat){
    rows.forEach(function(r){ r.classList.toggle('hidden', cat !== 'all' && r.dataset.cat !== cat); });
    buttons.forEach(function(b){ b.classList.toggle('active', b.dataset.filter === cat); });
    var note = document.getElementById('columnNote');
    if (note) note.style.display = (cat === 'column') ? 'block' : 'none';
    var teaser = document.getElementById('otherWritingTeaser');
    if (teaser) teaser.style.display = (cat === 'all' || cat === 'column') ? 'block' : 'none';
  }
  buttons.forEach(function(b){ b.addEventListener('click', function(){ applyFilter(b.dataset.filter); }); });
  function handleHash(){
    var hash = location.hash.replace('#','');
    if (!hash) return;
    var t = document.getElementById(hash);
    if (t && t.classList.contains('news-row')) {
      applyFilter(t.dataset.cat);
      setTimeout(function(){ t.scrollIntoView({behavior:'smooth', block:'center'}); }, 150);
    } else if (['media','press','column'].indexOf(hash) > -1) applyFilter(hash);
  }
  addEventListener('DOMContentLoaded', handleHash);
  addEventListener('hashchange', handleHash);
})();
</script>"""

def fix_body(f, body):
    # 위치 페이지: 목업의 깨진 iframe src 복구
    if f == "location.html":
        body = re.sub(r'src="https://maps\.google\.com/maps\?q=[^"]*"output=embed"',
                      'src="https://maps.google.com/maps?q=%EC%84%9C%EC%9A%B8%EC%8B%9C%20%EC%84%B1%EB%8F%99%EA%B5%AC%20%EB%AC%B4%ED%95%99%EB%A1%9C6%EA%B8%B8%2050&output=embed"',
                      body)
    # 사업분야 상세: 풀블리드 배너는 사진형 히어로가 대신함
    if f.startswith("service-"):
        body = re.sub(r'<div class="hero-banner">.*?</div>\s*</div>', '', body, count=1, flags=re.S)
    # 법적 문서
    if f in ("privacy.html","terms.html"):
        body = body.replace("<article>", '<article class="legal">', 1)
    # 목업의 mono 라벨 폰트 크기 등 inline 값은 그대로 두되, 아주 작은 px 는 살짝 키움
    body = re.sub(r'font-size:1[1-3](\.\d)?px', 'font-size:var(--fs-small)', body)
    body = body.replace('font-size:14.5px','font-size:var(--fs-small)').replace('font-size:15.5px','font-size:var(--fs-body)')
    body = re.sub(r'font-size:(19|20)px', 'font-size:var(--fs-h3)', body)
    # 흰 배경 위 <section> 교차 톤: 두 번째 섹션마다 연한 배경 (콘텐츠 페이지 리듬)
    return body

def page_html(title, sec, extra_css, hero, body, extra_js=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
{FONTS}
<style>
{css}
{extra_css}</style>
</head>
<body data-sec="{sec}">
{header}
{hero}
{body}
{footer}
<script>
{js}</script>{extra_js}
</body>
</html>
"""

# ── 서브페이지 42개 ────────────────────────────────────────────────────────
for f, m in pages.items():
    body = (SRC/f).read_text(encoding="utf-8")
    body = fix_body(f, body)
    if f in SUBBAR:
        hero = hero_subbar(f, m)
    elif f in PHOTO:
        hero = hero_photo(f, m)
    else:
        hero = hero_band(f, m)
    if not body.lstrip().startswith("<main"):
        body = "<main>\n" + body + "\n</main>"
    extra_js = NEWS_JS if f == "news.html" else ""
    page_css = ""
    if f == "about-overview.html":
        page_css = homecss + ABOUT_CSS
        extra_js = f"\n<script>\n{homejs}</script>"
    elif f == "about-leadership.html":
        page_css = LEADER_CSS
    title = f'{re.sub("<.*?>","",m["h1"])} — Verdex AI'
    (OUT/f).write_text(page_html(title, section_of(f), page_css, hero, body, extra_js), encoding="utf-8")

# ── 홈 ──────────────────────────────────────────────────────────────────────
top   = (SHELL/"home-top.html").read_text(encoding="utf-8")
lower = (SHELL/"home-lower.html").read_text(encoding="utf-8")
(OUT/"index.html").write_text(
    page_html("Verdex AI — 탄소는 비용이 아니라, 자산입니다", "", homecss, top, lower,
              f"\n<script>\n{homejs}</script>"), encoding="utf-8")

# ── 이미지 복사 ──────────────────────────────────────────────────────────────
if (ROOT/"images").exists():
    shutil.copytree(ROOT/"images", OUT/"images", dirs_exist_ok=True)

print(f"built {len(pages)+1} pages → {OUT}")
