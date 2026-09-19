#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스룸 기본 썸네일 생성 — images/thumb/*.svg

실제 사진이 없는 글에 쓰는 브랜드 기본 이미지입니다.
회사 로고(잎 + 워드마크)를 가운데 두고, 랜딩 히어로와 같은 직선·노드가
뒤로 뻗어 나가는 구성입니다.

    python3 make_thumbs.py

설치할 것 없습니다(표준 라이브러리만). 색·문구는 아래 V 를 고치세요.

로고 사용 규칙(images/brand/BRAND.md)
  · 남색 배경  → verdex-logo-ondark.svg  (잎은 초록, 글자만 흰색)
  · 밝은 배경  → verdex-logo-color.svg
  · 최소 가로 96px — 목록 썸네일(가로 약 180px)에서 로고가 그보다 작아지지 않도록
    가로 64% 로 크게 배치합니다.
"""
import math, pathlib, re

ROOT  = pathlib.Path(__file__).resolve().parent
BRAND = ROOT / "images" / "brand"
OUT   = ROOT / "images" / "thumb"
LOGO_VB = (1200, 580)          # 로고 원본 viewBox
LOGO_RATIO = LOGO_VB[0] / LOGO_VB[1]

V = {
 "column":  dict(bg1="#0A3A63", bg2="#05253F", accent="#7FD1A8", node="#CDF5DC",
                 logo="verdex-logo-ondark.svg", label="COLUMN",    dark=True),
 "press":   dict(bg1="#0B4A6B", bg2="#052F45", accent="#8FD8EE", node="#DAF2FB",
                 logo="verdex-logo-ondark.svg", label="PRESS",     dark=True),
 "media":   dict(bg1="#EEF4F0", bg2="#DCE9DF", accent="#2E8B3A", node="#1F6B2B",
                 logo="verdex-logo-color.svg",  label="MEDIA",     dark=False),
 "default": dict(bg1="#0A3A63", bg2="#0A4436", accent="#7FD1A8", node="#CDF5DC",
                 logo="verdex-logo-ondark.svg", label="VERDEX AI", dark=True),
}
# 모서리에 놓는 잎맥 한 다발 — 서브바(.sb-vein)와 같은 형태.
# 좌표는 0~1 비율. 그릴 때 픽셀로 환산합니다(선 굵기가 같이 커지지 않도록).
STEM  = [(1.06, 0.93), (0.86, 0.87), (0.66, 0.77), (0.46, 0.60)]
TWIGS = [[(0.775, 0.822), (0.770, 0.742), (0.796, 0.682), (0.852, 0.620)],
         [(0.628, 0.722), (0.618, 0.652), (0.644, 0.597), (0.700, 0.542)],
         [(0.902, 0.882), (0.902, 0.812), (0.928, 0.757), (0.984, 0.706)]]
TIPS  = [(0.852, 0.620), (0.700, 0.542), (0.984, 0.706)]
FLIPS = [(0, 0), (1, 0), (0, 1), (1, 1)]     # 변주별 모서리


def logo_inner(filename):
    """로고 SVG 에서 그림 부분(<g>…</g>)만 꺼내옵니다. c2pa 메타데이터는 버립니다."""
    raw = re.sub(r"<metadata>.*?</metadata>", "",
                 (BRAND / filename).read_text(encoding="utf-8"), flags=re.S)
    return "".join(re.findall(r"<g transform=.*?</g>", raw, re.S))


def build(key, w=800, h=600, label=True, spin=0):
    s = V[key]
    s_accent, s_node = s["accent"], s["node"]
    cx, cy = w / 2, h * 0.44
    lw = w * 0.64                      # 로고 가로 — 목록 크기에서도 96px 이상
    lh = lw / LOGO_RATIO
    sc = lw / LOGO_VB[0]
    fx, fy = FLIPS[spin % len(FLIPS)]
    def P(pt):
        x, y = pt
        return ((1 - x) if fx else x) * w, ((1 - y) if fy else y) * h
    def curve(pts):
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = [P(q) for q in pts]
        return "M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (x0, y0, x1, y1, x2, y2, x3, y3)

    sw = max(1.6, w * 0.0032)
    lines = ['<path d="%s" stroke-width="%.1f"/>' % (curve(STEM), sw)]
    lines += ['<path d="%s" stroke-width="%.1f"/>' % (curve(t), sw * 0.62) for t in TWIGS]
    end = P(STEM[-1])
    dots = ['<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (end[0], end[1], max(3.0, w * 0.0068))]
    for t in TIPS:
        x, y = P(t)
        dots.append('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, max(2.4, w * 0.0052)))
    vein = ('<g stroke="%s" fill="none" stroke-linecap="round" opacity=".45">%s</g>'
            '<g fill="%s" opacity=".75">%s</g>'
            % (s_accent, "".join(lines), s_node, "".join(dots)))

    ly = h * 0.875
    lab = ""
    if label and s["label"]:
        fs = h * 0.050
        lab = ('<text x="%.0f" y="%.0f" text-anchor="middle" font-family="Space Grotesk,'
               'Helvetica Neue,Arial,sans-serif" font-size="%.1f" font-weight="500" '
               'letter-spacing="%.2f" fill="%s" opacity=".9">%s</text>'
               % (cx, ly, fs, fs * 0.28, s["accent"], s["label"]))

    # 잎맥이 로고를 스치지 않도록 로고 영역만 마스크로 비웁니다
    pad_x, pad_y = lw * 0.07, lh * 0.26
    vig = 0.06 if not s["dark"] else 0.30

    return """<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="Verdex AI">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>
    </linearGradient>
    <radialGradient id="vg" cx="50%%" cy="44%%" r="74%%">
      <stop offset="0" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="%.2f"/>
    </radialGradient>
    <mask id="clear">
      <rect width="%d" height="%d" fill="#fff"/>
      <rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%.0f" fill="#000"/>
    </mask>
  </defs>
  <rect width="%d" height="%d" fill="url(#bg)"/>
  <rect width="%d" height="%d" fill="url(#vg)"/>
  <g mask="url(#clear)">%s</g>
  <g transform="translate(%.1f,%.1f) scale(%.5f)">%s</g>
  %s
</svg>""" % (w, h, w, h,
             s["bg1"], s["bg2"], vig,
             w, h,
             cx - lw / 2 - pad_x, cy - lh / 2 - pad_y, lw + pad_x * 2, lh + pad_y * 2, lh * 0.25,
             w, h, w, h,
             vein,
             cx - lw / 2, cy - lh / 2, sc, logo_inner(s["logo"]),
             lab)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    SPINS = [0, 26, 53, 79]          # 같은 카테고리가 이어져도 그림이 반복되지 않게
    n = 0
    for k in V:
        for i, sp in enumerate(SPINS, 1):
            (OUT / ("%s-%d.svg" % (k, i))).write_text(build(k, spin=sp), encoding="utf-8")
            n += 1
        (OUT / ("%s.svg" % k)).write_text(build(k), encoding="utf-8")
        n += 1
    (OUT / "og-default.svg").write_text(build("default", 1200, 630), encoding="utf-8")
    n += 1
    kb = sum((OUT / f.name).stat().st_size for f in OUT.iterdir()) / 1024
    print("  썸네일 %d장 → %s  (합계 %.0fKB)" % (n, OUT.relative_to(ROOT), kb))
