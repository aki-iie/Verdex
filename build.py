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
    <h1>{BAND_TITLE.get(f, re.sub("<.*?>","",m["h1"]))}</h1>
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
    <h1>{BAND_TITLE.get(f, re.sub("<.*?>","",m["h1"]))}</h1>
    {lede}{by}{upd}
    {subtabs_html(m["subtabs"])}
  </div>
</section>'''

def hero_subbar(f, m):
    """회사 소개 챕터: 로고 밑 섹션 탭 바 (+ 개요를 뺀 페이지는 얇은 챕터 밴드)"""
    bar = f'''<div class="subbar">
  <div class="wrap">
    <span class="sb-title">{SEC_LABEL.get(section_of(f), "")}</span>
    {subtabs_html(m["subtabs"])}
  </div>
</div>'''
    return bar + f'''
<div class="chapband">
  <img src="images/about-solar.jpg" alt="">
  <div class="cb-veil"></div>
  <svg class="cb-vein" viewBox="0 0 1200 240" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">
    <g stroke="#7FD1A8" fill="none" stroke-linecap="round" opacity=".55">
      <path d="M1250,206 C1150,196 1060,180 962,156" stroke-width="1.7"/>
      <path d="M1136,188 C1130,156 1136,128 1150,100" stroke-width="1.2"/>
      <path d="M1052,172 C1046,144 1052,120 1064,96" stroke-width="1.2"/>
      <path d="M972,158 C966,134 972,112 982,92" stroke-width="1.1"/>
      <path d="M1094,180 C1104,192 1116,202 1132,210" stroke-width="1"/>
    </g>
    <g fill="#CDF5DC" opacity=".85">
      <circle cx="1150" cy="99" r="3.2"/><circle cx="1064" cy="95" r="3.2"/>
      <circle cx="982" cy="91" r="2.7"/><circle cx="1132" cy="210" r="2.4"/>
    </g>
  </svg>
  <div class="wrap">
    <div class="eyebrow">{m["eyebrow"]}</div>
    <h1>{BAND_TITLE.get(f, re.sub("<.*?>","",m["h1"]))}</h1>
  </div>
</div>'''

SUBBAR = {"about-overview.html", "about-leadership.html", "about-history.html", "location.html"}
BAND_TITLE = {"about-overview.html": "개요"}
SEC_LABEL = {"about":"회사 소개","business":"사업 분야","news":"뉴스룸","resources":"자료","careers":"채용","contact":"문의"}


HIST_CSS = """
  .hist{padding-block:clamp(44px,5vw,100px)}
  .tl{margin-top:clamp(34px,4vw,72px);display:flex;flex-direction:column;gap:clamp(30px,3.4vw,64px)}
  .tl-group{display:grid;grid-template-columns:minmax(96px,168px) 1fr;gap:clamp(18px,3vw,56px)}
  .tl-year span{position:sticky;top:calc(var(--hh) + 82px);display:block;
    font-family:var(--mono);font-size:clamp(22px,2.2vw,40px);font-weight:700;
    letter-spacing:-.01em;color:var(--navy);line-height:1}
  .tl-items{position:relative;border-left:1px solid var(--line);
    display:flex;flex-direction:column;gap:clamp(24px,2.8vw,48px)}
  .tl-card{position:relative;padding-left:clamp(20px,2.4vw,40px)}
  .tl-card::before{content:"";position:absolute;left:-5px;top:7px;width:9px;height:9px;border-radius:50%;
    background:var(--navy);box-shadow:0 0 0 5px #fff}
  .tl-card.ahead::before,.tl-card.founding::before{background:var(--brand)}
  .tl-card.founding::before{width:13px;height:13px;left:-7px;top:5px}
  .tl-date{font-family:var(--mono);font-size:var(--fs-small);font-weight:500;
    letter-spacing:.08em;color:var(--muted)}
  .chip{display:inline-block;margin-top:10px;font-size:clamp(11px,.86vw,13px);font-weight:700;
    letter-spacing:.02em;padding:.32em .78em;border-radius:2px}
  .chip-tech{background:rgba(14,127,171,.13);color:var(--sky)}
  .chip-rnd{background:rgba(10,58,99,.1);color:var(--navy)}
  .chip-partner{background:rgba(46,139,58,.13);color:var(--brand)}
  .chip-book{background:rgba(127,209,168,.22);color:#1F6B2B}
  .chip-found{background:var(--brand);color:#fff}
  .chip-ahead{background:transparent;color:var(--brand);border:1px dashed var(--brand)}
  .tl-card h3{margin-top:10px;font-size:var(--fs-h3);font-weight:800;letter-spacing:-.022em;
    color:var(--navy);line-height:1.5}
  .tl-card p{margin-top:9px;max-width:58ch;font-size:var(--fs-body);line-height:1.85;color:var(--muted)}
  .tl-card.ahead{border:1px dashed rgba(46,139,58,.45);border-radius:5px;
    background:rgba(46,139,58,.04);padding:clamp(18px,1.8vw,30px);margin-left:clamp(20px,2.4vw,40px)}
  .tl-card.ahead::before{left:calc(-1 * clamp(20px,2.4vw,40px) - 5px)}
  .tl-card.feat{display:grid;grid-template-columns:clamp(110px,11vw,168px) 1fr;
    gap:clamp(18px,2vw,34px);align-items:start}
  .tl-cover{aspect-ratio:3/4;border:1.5px dashed #C3CDC2;border-radius:4px;background:#F1F4F0;
    display:grid;place-items:center;text-align:center;line-height:1.7;
    font-size:var(--fs-small);color:#8C9A8E;padding:10px}
  .tl-link{display:inline-block;margin-top:16px;font-family:var(--mono);font-size:var(--fs-small);
    font-weight:700;letter-spacing:.05em;color:var(--brand)}
  @media (max-width:760px){
    .tl-group{grid-template-columns:1fr;gap:14px}
    .tl-year span{position:static}
    .tl-card.feat{grid-template-columns:1fr}
    .tl-cover{max-width:180px}
  }
"""

LOC_CSS = """
  .loc{padding-block:clamp(44px,5vw,100px)}
  .loc-lede{max-width:56ch;font-size:clamp(15px,1.12vw,20px);line-height:1.9;color:var(--muted)}
  .loc .loc-top{margin-top:clamp(26px,3vw,52px)}
  .loc-top{margin-top:clamp(30px,3.6vw,64px);display:grid;
    grid-template-columns:1.85fr 1fr;gap:clamp(16px,1.8vw,30px);align-items:stretch}
  .map-slot{position:relative;margin:0;aspect-ratio:16/9;border-radius:6px;overflow:hidden;
    border:1.5px dashed #C3CDC2;display:grid;place-items:center;
    background:
      repeating-linear-gradient(0deg,rgba(10,58,99,.055) 0 1px,transparent 1px 46px),
      repeating-linear-gradient(90deg,rgba(10,58,99,.055) 0 1px,transparent 1px 46px),
      linear-gradient(160deg,#EFF4F0,#E4EDE6)}
  .map-slot .slot-label{position:absolute;left:0;right:0;bottom:clamp(14px,1.6vw,26px)}
  .slot-label{font-size:var(--fs-small);line-height:1.8;text-align:center;color:#8C9A8E}
  .map-pin{position:absolute;left:50%;top:46%;width:clamp(30px,2.8vw,42px);height:auto;
    transform:translate(-50%,-100%);filter:drop-shadow(0 8px 14px rgba(10,58,99,.3))}
  .map-ring{position:absolute;left:50%;top:46%;width:clamp(56px,5.4vw,84px);aspect-ratio:1;
    transform:translate(-50%,-50%);border-radius:50%;
    border:1.5px solid rgba(46,139,58,.5);background:rgba(46,139,58,.08)}
  .loc-shots{display:grid;grid-template-rows:1fr 1fr;gap:clamp(16px,1.8vw,30px)}
  .shot-slot{margin:0;border-radius:6px;border:1.5px dashed #C3CDC2;background:#F1F4F0;
    display:grid;place-items:center;text-align:center;line-height:1.8;
    font-size:var(--fs-small);color:#8C9A8E;padding:12px;min-height:118px}
  .loc-btns{margin-top:clamp(20px,2.2vw,34px);display:flex;gap:10px;flex-wrap:wrap}
  .lbtn{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:3px;
    padding:.8em 1.5em;font-size:var(--fs-small);font-weight:700;color:var(--muted);
    transition:border-color .25s,color .25s,background-color .25s}
  .lbtn:hover{border-color:var(--brand);color:var(--brand)}
  .lbtn.primary{background:var(--cta);border-color:var(--cta);color:#fff}
  .lbtn.primary:hover{background:var(--cta-hover);border-color:var(--cta-hover);color:#fff}
  .loc-grid{margin-top:clamp(34px,4vw,72px);display:grid;grid-template-columns:repeat(4,1fr);
    gap:clamp(16px,2.2vw,40px)}
  .loc-grid>div{border-top:2px solid var(--navy);padding-top:clamp(12px,1.5vw,20px)}
  .loc-grid b{display:block;font-family:var(--mono);font-size:var(--fs-small);font-weight:700;
    letter-spacing:.12em;text-transform:uppercase;color:var(--brand)}
  .loc-grid p{margin-top:10px;font-size:var(--fs-h3);font-weight:700;letter-spacing:-.02em;
    color:var(--navy);line-height:1.6}
  .loc-grid span{display:block;margin-top:8px;font-size:var(--fs-small);line-height:1.8;color:var(--muted)}
  @media (max-width:900px){
    .loc-top{grid-template-columns:1fr}
    .loc-shots{grid-template-rows:none;grid-template-columns:1fr 1fr}
    .loc-grid{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:560px){ .loc-grid{grid-template-columns:1fr} .loc-shots{grid-template-columns:1fr} }
"""

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
  .screen.about{min-height:clamp(460px,calc(100svh - var(--hh) - 300px),820px);scroll-snap-align:none}
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
    elif f == "about-history.html":
        page_css = HIST_CSS
    elif f == "location.html":
        page_css = LOC_CSS
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
