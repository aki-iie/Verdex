#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스룸 기본 썸네일 생성 — images/thumb/*.svg

실제 사진이 없는 글에 쓰는 브랜드 기본 이미지입니다.
로고 잎 마크를 허브로 두고 랜딩 히어로와 같은 직선·노드가 뻗어 나가는 구성.

    python3 make_thumbs.py

설치할 것 없습니다(표준 라이브러리만). 색·문구를 바꾸려면 아래 V 를 고치세요.
"""
import math, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent
MARK = ROOT / "images" / "brand" / "verdex-mark-white.svg"
OUT  = ROOT / "images" / "thumb"
MARK_VB = "-195.08 -83.08 743.16 743.16"

V = {
 "column":  dict(bg1="#0A3A63", bg2="#05253F", accent="#7FD1A8", node="#CDF5DC",
                 leaf="#FFFFFF", label="COLUMN",    dark=True),
 "press":   dict(bg1="#0B4A6B", bg2="#052F45", accent="#8FD8EE", node="#DAF2FB",
                 leaf="#FFFFFF", label="PRESS",     dark=True),
 "media":   dict(bg1="#EEF4F0", bg2="#DCE9DF", accent="#2E8B3A", node="#1F6B2B",
                 leaf="#2E8B3A", label="MEDIA",     dark=False),
 "default": dict(bg1="#0A3A63", bg2="#0A4436", accent="#7FD1A8", node="#CDF5DC",
                 leaf="#FFFFFF", label="VERDEX AI", dark=True),
}
RAYS = [(-62, 1.00), (18, 0.86), (152, 0.94), (-148, 0.62), (86, 0.55)]


def leaf_path(fill):
    raw = re.sub(r"<metadata>.*?</metadata>", "", MARK.read_text(encoding="utf-8"), flags=re.S)
    g = re.search(r"(<g transform=.*?</g>)", raw, re.S).group(1)
    return g.replace('fill="#FFFFFF"', 'fill="%s"' % fill)


def build(key, w=800, h=600, label=True, spin=0):
    s = V[key]
    cx, cy = w / 2, h * 0.455
    R  = min(w, h) * 0.30
    mh = min(w, h) * 0.30
    sc = mh / 743.16
    reach = math.hypot(w, h) * 0.62
    rays, nodes = [], []
    for ang, f in RAYS:
        a = math.radians(ang + spin)
        x0, y0 = cx + math.cos(a) * R * 1.18, cy + math.sin(a) * R * 1.18
        x1, y1 = cx + math.cos(a) * reach * f, cy + math.sin(a) * reach * f
        rays.append('<path d="M%.1f,%.1f L%.1f,%.1f"/>' % (x0, y0, x1, y1))
        nodes.append('<circle cx="%.1f" cy="%.1f" r="%.1f"/>' % (x1, y1, max(2.6, w * 0.0058)))
    lab = ""
    if label and s["label"]:
        fs = h * 0.052
        ly = h * 0.875
        lab = ('<text x="%.0f" y="%.0f" text-anchor="middle" font-family="Space Grotesk,'
               'Helvetica Neue,Arial,sans-serif" font-size="%.1f" font-weight="500" '
               'letter-spacing="%.2f" fill="%s" opacity=".92">%s</text>'
               % (cx, ly, fs, fs * 0.28, s["accent"], s["label"]))
    vig = 0.06 if not s["dark"] else 0.30
    band_w = w * 0.62
    band_h = h * 0.13
    band_x = (w - band_w) / 2
    band_y = h * 0.875 - band_h * 0.72
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="Verdex AI">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>
    </linearGradient>
    <radialGradient id="vg" cx="50%%" cy="46%%" r="72%%">
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
  <g mask="url(#clear)">
    <g stroke="%s" fill="none" stroke-width="%.1f" stroke-linecap="round" opacity=".5">%s</g>
    <g fill="%s" opacity=".85">%s</g>
  </g>
  <circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-width="%.1f" opacity=".55"/>
  <g transform="translate(%.1f,%.1f) scale(%.5f)">
    <svg viewBox="%s" width="743.16" height="743.16" overflow="visible">%s</svg>
  </g>
  %s
</svg>''' % (w, h, w, h, s["bg1"], s["bg2"], vig, w, h,
             band_x, band_y, band_w, band_h, band_h / 2, w, h, w, h,
             s["accent"], max(1.5, w * 0.0028), "".join(rays),
             s["node"], "".join(nodes),
             cx, cy, R, s["accent"], max(1.4, w * 0.0022),
             cx - 743.16 * sc / 2, cy - mh / 2, sc, MARK_VB, leaf_path(s["leaf"]), lab)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    SPINS = [0, 26, 53, 79]          # 같은 카테고리가 이어져도 그림이 반복되지 않게
    n = 0
    for k in V:
        for i, sp in enumerate(SPINS, 1):
            (OUT / ("%s-%d.svg" % (k, i))).write_text(build(k, spin=sp), encoding="utf-8")
            n += 1
        (OUT / ("%s.svg" % k)).write_text(build(k), encoding="utf-8")   # 대표 1장
        n += 1
    print("  썸네일 %d장 → %s" % (n, OUT.relative_to(ROOT)))
    # 링크 공유용 큰 이미지 (1200x630) — SEO 작업 때 og:image 로 씁니다
    og = OUT / "og-default.svg"
    og.write_text(build("default", 1200, 630), encoding="utf-8")
    print("  %-28s %5.1fKB" % (og.relative_to(ROOT), og.stat().st_size / 1024))
