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

# ── 헤드리스 워드프레스 ────────────────────────────────────────────────────
#  wp_sync.py 가 만든 content/wp-posts.json 이 있으면 글 페이지를 자동 생성합니다.
#  WP_NEWSROOM = True 로 바꾸면 뉴스룸(news.html) 자체가 워드프레스 글로 채워지고,
#  False 면 손으로 쓴 뉴스룸은 그대로 두고 news-live.html 에 따로 만듭니다.
WP_NEWSROOM = False
WP_FILE  = ROOT/"content"/"wp-posts.json"
WP_POSTS = json.load(open(WP_FILE, encoding="utf-8")) if WP_FILE.exists() else []
# 아직 verdex.kr 에 없고 외부(CO2Korea 등)에만 있는 글 — 뉴스룸 목록에만 올립니다.
EXT_FILE = ROOT/"content"/"external.json"
EXT_ITEMS = json.load(open(EXT_FILE, encoding="utf-8")) if EXT_FILE.exists() else []
# 미디어보도(외부 언론사 기사)는 전문을 호스팅하지 않습니다 — 저작권
NO_FULLTEXT = {"media"}

# ── 회사 정보 주입 (content/company.json) ────────────────────────────────────
CO_FILE = ROOT/"content"/"company.json"
CO = json.load(open(CO_FILE, encoding="utf-8")) if CO_FILE.exists() else {}
PENDING = []   # 회사 확인 대기 항목

def todo(label):
    PENDING.append(label)
    return '<mark class="todo">[회사 확인 대기 — %s]</mark>' % label

def legal_fill(body):
    """privacy.html 의 {{토큰}} 을 company.json 값으로 치환.
       값이 비어 있으면 주황색 '확인 대기' 표시를 남겨 그대로 공개되지 않게 합니다."""
    v = {}
    v["보유기간"]   = CO.get("개인정보_보유기간") or todo("보유 기간")
    v["전화"]       = CO.get("전화") or todo("대표 전화")
    v["보호책임자"] = CO.get("개인정보보호책임자") or todo("보호책임자 이름·직위")
    v["시행일"]     = CO.get("방침_시행일") or todo("방침 시행일")

    email = CO.get("개인정보_문의_이메일")
    if email in (None, ""):
        v["이메일"] = todo("공개 이메일 주소")
    elif email == "없음":
        v["이메일"] = "별도 이메일 없음 — 위 연락처로 문의해 주시기 바랍니다."
    else:
        v["이메일"] = '<a href="mailto:%s">%s</a>' % (email, email)

    wt = CO.get("개인정보_위탁업체")
    if wt is None:
        v["위탁"] = "<p>%s</p>" % todo("위탁 업체 유무 및 목록")
    elif not wt:
        v["위탁"] = ("<p>회사는 이용자의 개인정보 처리 업무를 외부에 위탁하고 있지 않습니다. "
                     "향후 위탁이 발생하는 경우 위탁받는 자와 위탁 업무의 내용을 본 방침에 공개하고, "
                     "필요한 경우 사전에 동의를 받겠습니다.</p>")
    else:
        rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (w.get("업체", ""), w.get("업무", ""))
                       for w in wt)
        v["위탁"] = ("<p>회사는 원활한 업무 처리를 위하여 아래와 같이 개인정보 처리 업무를 위탁하고 있으며, "
                     "위탁계약 시 개인정보가 안전하게 관리될 수 있도록 필요한 사항을 규정하고 있습니다.</p>"
                     "<table><tr><th>수탁업체</th><th>위탁 업무</th></tr>%s</table>" % rows)

    for k, val in v.items():
        body = body.replace("{{%s}}" % k, val)
    return body

LEGAL_CSS = """
  .legal-lede{font-size:var(--fs-body);line-height:1.9;color:var(--muted);
    padding-bottom:clamp(20px,2.4vw,36px);border-bottom:1px solid var(--line);
    margin-bottom:clamp(18px,2.2vw,32px)}
  .legal-date{margin-top:clamp(26px,3vw,48px);padding-top:clamp(16px,1.8vw,26px);
    border-top:1px solid var(--line);font-family:var(--mono);
    font-size:var(--fs-small);color:var(--muted)}
  mark.todo{background:#FFF3D6;color:#8A5A00;font-weight:700;
    padding:.14em .5em;border-radius:3px;border:1px dashed #E0B053}
"""

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
SEC = {"news":"news","columns-other":"news","column-":"news","press-":"news","post-":"news",
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
  </div>
</section>'''

def page_head(f, m):
    """서브바 아래에 오는 낮은 제목 블록 (큰 히어로 대체)"""
    top = ""
    if m["crumb"]:     top = f'<div class="crumb">{m["crumb"]}</div>'
    elif m["eyebrow"]: top = f'<div class="eyebrow">{m["eyebrow"]}</div>'
    lede = f'<p class="lede">{m["lede"]}</p>' if m["lede"] else ""
    by   = f'<div class="byline">{m["byline"]}</div>' if m["byline"] else ""
    upd  = f'<div class="updated">{m["updated"]}</div>' if m["updated"] else ""
    title = BAND_TITLE.get(f, re.sub("<.*?>", "", m["h1"]))
    return f'''<section class="phead">
  <div class="wrap">
    {top}
    <h1>{title}</h1>
    {lede}{by}{upd}
  </div>
</section>'''

def hero_subbar(f, m):
    """회사 소개 챕터: 로고 바로 밑에 붙는 섹션 탭 바 (제목·탭·브랜드 라인)"""
    return f'''<div class="subbar">
  <svg class="sb-vein" viewBox="0 0 320 56" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">
    <g stroke="#7FD1A8" fill="none" stroke-linecap="round" opacity=".5">
      <path d="M340,50 C288,45 236,36 186,22" stroke-width="1.4"/>
      <path d="M262,41 C260,30 264,21 272,12" stroke-width="1"/>
      <path d="M212,30 C210,22 214,15 222,8" stroke-width="1"/>
    </g>
    <g fill="#C7F2D6" opacity=".85">
      <circle cx="272" cy="12" r="2.4"/><circle cx="222" cy="8" r="2"/>
    </g>
  </svg>
  <div class="wrap">
    <span class="sb-title">{SEC_LABEL.get(section_of(f), "")}</span>
    {sec_subtabs(f)}
  </div>
</div>'''

SUBBAR = {"about-overview.html", "about-leadership.html", "about-history.html", "location.html"}
# 위 띠(서브바)가 이미 말해주는 내용이라 아래 제목 블록을 두지 않는 페이지
NO_HEAD = SUBBAR | {"business-overview.html", "news.html", "resources.html",
                    "careers.html", "contact.html"}
BAND_TITLE = {"about-overview.html":"개요", "business-overview.html":"개요",
              "news.html":"뉴스·보도", "resources.html":"자료실",
              "careers.html":"채용 안내", "contact.html":"문의하기"}
SEC_LABEL = {"about":"회사 소개","business":"사업 분야","news":"뉴스룸","resources":"자료","careers":"채용","contact":"문의"}

# 챕터별 서브탭 — 회사 소개와 동일한 UI를 모든 메뉴에 적용
SEC_TABS = {
 "about":    [("./about-overview.html","개요"), ("./about-leadership.html","리더십"),
              ("./about-history.html","연혁"), ("./location.html","오시는 길")],
 "business": [("./business-overview.html","개요"), ("./service-impact-assessment.html","AI 환경영향평가"),
              ("./service-carbon-neutrality.html","탄소중립 전략"), ("./service-esg.html","ESG·지속가능성"),
              ("./service-smart-energy.html","스마트 에너지"), ("./service-circular-economy.html","순환경제")],
 "news":     [("./news.html","뉴스·보도"), ("./columns-other.html","대표의 다른 글")],
 "resources":[("./resources.html","자료실"), ("./resource-cbam-report-example.html","CBAM 보고서 예시"),
              ("./resource-eu-compliance-playbook.html","EU 규제 플레이북")],
 "careers":  [("./careers.html","채용 안내")],
 "contact":  [("./contact.html","문의하기"), ("./faq.html","FAQ")],
}

def active_tab(f):
    """상세 페이지(기사·자료)에서도 자기 챕터의 대표 탭이 켜지도록."""
    tabs = SEC_TABS.get(section_of(f), [])
    if any(h == "./" + f for h, _ in tabs):
        return f
    if f.startswith(("post-", "column-", "press-")):
        return "news.html"
    if f.startswith("resource-"):
        return "resources.html"
    return f

def sec_subtabs(f):
    tabs = SEC_TABS.get(section_of(f), [])
    if not tabs:
        return ""
    cur, out = active_tab(f), []
    for h, t in tabs:
        act = ' class="active"' if h == "./" + cur else ''
        out.append('<a href="%s"%s>%s</a>' % (h, act, t))
    return '<div class="subtabs">' + "".join(out) + "</div>"


HIST_CSS = """
  .hist{padding:min(3.6vh,46px) 0 clamp(44px,5vw,100px)}
  .hist .section-head{margin-bottom:min(3.4vh,42px)}
  .tl{margin-top:min(3.4vh,44px);display:flex;flex-direction:column;gap:clamp(30px,3.4vw,64px)}
  .tl-group{display:grid;grid-template-columns:minmax(96px,168px) 1fr;gap:clamp(18px,3vw,56px)}
  .tl-year span{position:sticky;top:calc(var(--hh) + var(--sbh) + clamp(16px,1.8vw,30px));display:block;
    font-family:var(--mono);font-size:clamp(22px,2.2vw,40px);font-weight:700;
    letter-spacing:-.01em;color:var(--navy);line-height:1}
  .tl-items{position:relative;border-left:1px solid transparent;
    display:flex;flex-direction:column;gap:clamp(24px,2.8vw,48px)}
  /* 리더십 레일(A안)과 같은 잎맥 축 */
  .tl-items::before{content:"";position:absolute;left:-1px;top:.45em;bottom:.45em;width:1px;
    background:linear-gradient(180deg,var(--brand-lift) 0%,rgba(127,209,168,.25) 100%)}
  .tl-card{position:relative;padding-left:clamp(20px,2.4vw,40px)}
  .tl-card::before{content:"";position:absolute;left:-5px;top:7px;width:9px;height:9px;border-radius:50%;
    background:var(--brand);box-shadow:0 0 0 5px #fff}
  .tl-card.founding::before{background:#1F6B2B}
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
  .loc{padding:min(2.4vh,30px) 0;height:calc(100svh - var(--hh) - var(--sbh));
    display:flex;align-items:center}
  .loc>.wrap{width:100%}
  .loc .section-head{margin-bottom:min(1.7vh,20px)}
  .loc .section-head h2{margin-top:min(1.2vh,14px);font-size:min(var(--fs-h2),5vh)}
  .loc .section-head p{margin-top:min(1.2vh,14px);
    font-size:min(var(--fs-body),2.05vh);line-height:1.8}
  .loc .eyebrow{font-size:min(var(--fs-eyebrow),1.7vh)}
  .loc-lede{max-width:56ch;font-size:clamp(15px,1.12vw,20px);line-height:1.9;color:var(--muted)}
  .loc .loc-top{margin-top:0}
  .loc-top{margin-top:0;display:grid;height:min(26vh,320px);
    grid-template-columns:1.85fr 1fr;gap:clamp(16px,1.8vw,30px);align-items:stretch}
  .map-slot{position:relative;margin:0;height:100%;border-radius:6px;overflow:hidden;
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
  .loc-shots{display:grid;height:100%;grid-template-rows:1fr 1fr;gap:clamp(16px,1.8vw,30px)}
  .shot-slot{margin:0;border-radius:6px;border:1.5px dashed #C3CDC2;background:#F1F4F0;
    display:grid;place-items:center;text-align:center;line-height:1.8;
    font-size:min(var(--fs-small),1.6vh);color:#8C9A8E;padding:12px;min-height:0}
  .loc-btns{margin-top:min(1.6vh,18px);display:flex;gap:9px;flex-wrap:wrap}
  .lbtn{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:3px;
    padding:.72em 1.4em;font-size:min(var(--fs-small),1.7vh);font-weight:700;color:var(--muted);
    transition:border-color .25s,color .25s,background-color .25s}
  .lbtn:hover{border-color:var(--brand);color:var(--brand)}
  .lbtn.primary{background:var(--cta);border-color:var(--cta);color:#fff}
  .lbtn.primary:hover{background:var(--cta-hover);border-color:var(--cta-hover);color:#fff}
  .loc-grid{margin-top:min(1.7vh,20px);display:grid;grid-template-columns:repeat(4,1fr);
    gap:clamp(14px,1.9vw,34px)}
  .loc-grid>div{border-top:2px solid var(--navy);padding-top:min(1.4vh,16px)}
  .loc-grid b{display:block;font-family:var(--mono);font-size:min(var(--fs-small),1.6vh);font-weight:700;
    letter-spacing:.12em;text-transform:uppercase;color:var(--brand)}
  .loc-grid p{margin-top:min(.8vh,9px);font-size:min(var(--fs-h3),2.05vh);font-weight:700;
    letter-spacing:-.02em;color:var(--navy);line-height:1.45}
  .loc-grid span{display:block;margin-top:min(.7vh,8px);font-size:min(var(--fs-small),1.6vh);
    line-height:1.72;color:var(--muted)}
  @media (max-width:1100px){
    .loc{height:auto;display:block;padding-block:min(3vh,34px) clamp(44px,5vw,90px)}
    .loc-top{height:auto}
    .map-slot{height:auto;aspect-ratio:16/9}
    .loc-shots{height:auto}
    .shot-slot{min-height:110px}
    .loc-grid{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:900px){
    .loc{height:auto;display:block;padding-block:34px 44px}
    .loc-top{height:auto;grid-template-columns:1fr}
    .map-slot{height:auto;aspect-ratio:16/9}
    .loc-shots{height:auto}
    .shot-slot{min-height:118px}
    .loc-shots{grid-template-rows:none;grid-template-columns:1fr 1fr}
    .loc-grid{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:560px){ .loc-grid{grid-template-columns:1fr} .loc-shots{grid-template-columns:1fr} }
"""

LEADER_CSS = """
  /* 인사말 첫 화면: 사진·인용문·여백에 vh 상한을 걸어 서명까지 한 화면에.
     본문 글자 크기(var(--fs-body))는 그대로 두고 줄간격·여백만 조인다. */
  .lead{background:var(--paper);padding:min(2.8vh,36px) 0;
    height:calc(100svh - var(--hh) - var(--sbh));display:flex;align-items:center}
  .lead-grid{display:grid;grid-template-columns:min(27vh,272px) minmax(0,1fr) min(29vh,296px);
    gap:clamp(24px,3.2vw,60px);align-items:start;max-width:none;width:100%}
  .portrait{margin:0}
  .portrait img{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:center 22%;
    border-radius:6px;box-shadow:0 28px 54px -34px rgba(10,58,99,.5)}
  .portrait figcaption{margin-top:min(1.6vh,18px)}
  .p-name{font-size:min(clamp(19px,1.8vw,32px),3.2vh);font-weight:900;letter-spacing:-.03em;
    color:var(--navy);line-height:1.2}
  .p-role{margin-top:5px;font-family:var(--mono);font-size:min(var(--fs-small),1.7vh);
    letter-spacing:.14em;font-weight:500;color:var(--brand)}
  .say .eyebrow{font-size:min(var(--fs-eyebrow),1.7vh)}
  .say blockquote{margin:min(1.2vh,14px) 0 0;font-size:min(clamp(18px,1.8vw,32px),3.3vh);
    font-weight:800;line-height:1.42;letter-spacing:-.03em;color:var(--navy);text-wrap:balance}
  .say p{margin-top:min(1.3vh,16px);max-width:64ch;font-size:var(--fs-body);
    line-height:1.76;color:var(--muted)}
  .sign{margin-top:min(1.9vh,24px);padding-top:min(1.5vh,20px);border-top:1px solid var(--line);
    display:flex;align-items:flex-end;gap:clamp(14px,1.8vw,30px);flex-wrap:wrap}
  .sign-slot{width:min(clamp(110px,10.5vw,160px),19vh);aspect-ratio:12/5;border:1.5px dashed #C3CDC2;
    border-radius:4px;background:#F1F4F0;display:grid;place-items:center;
    font-size:min(var(--fs-small),1.7vh);color:#8C9A8E}
  .sign-who{display:flex;flex-direction:column;gap:2px;font-size:min(var(--fs-small),1.7vh);color:var(--muted)}
  .sign-who b{font-size:min(var(--fs-h3),2.4vh);font-weight:800;letter-spacing:-.02em;color:var(--ink)}
  /* 오른쪽 약력 레일 (A안 — 잎맥 노드 타임라인) */
  .rail{align-self:stretch;border-left:1px solid var(--line);
    padding-left:clamp(18px,1.9vw,36px);display:flex;flex-direction:column}
  .rail .eyebrow{font-size:min(var(--fs-eyebrow),1.7vh)}
  .rail h2{margin-top:min(1.1vh,12px);font-size:min(clamp(17px,1.5vw,28px),2.9vh);
    font-weight:900;letter-spacing:-.03em;color:var(--navy);line-height:1.25}
  .rail-list{--rp:clamp(16px,1.3vw,26px);position:relative;
    margin-top:min(2.3vh,28px);padding-left:var(--rp)}
  .rail-list::before{content:"";position:absolute;left:3px;top:.7em;bottom:.7em;width:1px;
    background:linear-gradient(180deg,var(--brand-lift),rgba(127,209,168,.22))}
  .rail-list li{position:relative;padding-bottom:min(2.4vh,28px)}
  .rail-list li:last-child{padding-bottom:0}
  .rail-list li::before{content:"";position:absolute;left:calc(var(--rp) * -1);top:.62em;width:7px;height:7px;
    border-radius:50%;background:var(--brand);box-shadow:0 0 0 3.5px var(--paper)}
  .rail-list b{display:block;font-size:min(var(--fs-h3),2.35vh);font-weight:800;
    letter-spacing:-.02em;color:var(--navy);line-height:1.34}
  .rail-list span{display:block;margin-top:3px;font-size:min(var(--fs-small),1.65vh);color:var(--muted)}
  .career-link{display:inline-block;margin-top:min(2.6vh,30px);font-family:var(--mono);
    font-size:min(var(--fs-small),1.65vh);font-weight:700;letter-spacing:.05em;color:var(--brand)}
  .career-link:hover{color:var(--cta-hover)}

  @media (max-width:1240px){
    .lead-grid{grid-template-columns:min(26vh,250px) minmax(0,1fr)}
    .rail{grid-column:1 / -1;border-left:0;border-top:1px solid var(--line);
      padding-left:0;padding-top:min(2.2vh,26px);margin-top:min(1.4vh,18px)}
    .rail-list{margin-top:min(1.8vh,22px);padding-left:0;
      display:grid;grid-template-columns:repeat(4,1fr);gap:clamp(14px,1.8vw,30px)}
    .rail-list::before{display:none}
    .rail-list li{padding:min(1vh,12px) 0 0;border-top:2px solid var(--navy)}
    .rail-list li::before{display:none}
    .career-link{margin-top:min(2vh,22px)}
  }
  @media (max-width:900px){
    .lead{height:auto;display:block;padding-block:34px 40px}
    .lead-grid{grid-template-columns:1fr;gap:24px}
    .portrait img{max-width:360px}
    .say blockquote{font-size:clamp(21px,5.2vw,30px)}
    .rail-list{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:560px){ .rail-list{grid-template-columns:1fr;gap:14px} }
"""

ABOUT_CSS = """
  /* 개요 화면: 어떤 창 크기에서도 헤더+탭바를 뺀 나머지에 정확히 들어가도록
     세로를 먹는 값마다 vh 상한을 건다 (min(기존값, N vh)) */
  /* main > section 공통 여백(96px)이 개요 화면까지 밀고 있어 제거 */
  .screen.about{padding:0;height:calc(100svh - var(--hh) - var(--sbh));min-height:0;scroll-snap-align:none}
  .about.open{height:auto;min-height:calc(100svh - var(--hh) - var(--sbh))}
  .about .stage{padding:min(3vh,34px) 0 min(3.4vh,40px);gap:min(2.2vh,26px)}
  .about .intro{padding-bottom:min(1.4vh,16px)}
  /* 심볼만이 아니라 풀 로고(잎+워드마크). 사진 위에 흰색 녹아웃으로 직접 얹는다 */
  .about .mark{width:min(clamp(160px,16.5vw,290px),19vh);aspect-ratio:auto;
    background:none;border-radius:0;display:block}
  .about .mark img{width:100%;height:auto;display:block}
  .about h2{margin-top:min(2.4vh,26px);font-size:min(clamp(24px,3.9vw,74px),6.4vh)}
  .about .lede{margin-top:min(1.8vh,20px);font-size:min(clamp(13px,1.22vw,22px),2.1vh);line-height:1.78}
  .about .cell{min-height:min(clamp(84px,9.4vw,186px),16vh);padding-block:min(1.8vh,22px)}
  .about .cell b{font-size:min(clamp(18px,2.35vw,44px),4.6vh)}
  .about .hint{padding-top:min(1.6vh,18px);font-size:min(clamp(12px,1.02vw,18px),1.8vh)}
  .about .panels{min-height:0;padding-top:min(2.4vh,28px)}
  /* 펼친 상태: 가운데 정렬을 풀고 위로 붙임 (닫힌 상태의 여백이 남아 비대칭으로 보이던 문제) */
  .screen.about.open{align-items:flex-start}
  .about.open .stage{justify-content:flex-start;padding-top:min(2vh,22px);gap:0}
  .about.open .close{top:min(1.6vh,18px)}
  @media (max-width:900px){
    .screen.about{height:auto;min-height:calc(100svh - var(--hh) - var(--sbh))}
    .about .stage{padding-block:30px 36px;gap:18px}
    .about .cell{min-height:64px}
  }
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

THUMB_CATS = {"column", "press", "media"}

def thumb_for(cat, n):
    """카테고리 기본 썸네일. 목록 순서대로 4종 변주를 돌려써서
       같은 카테고리가 연달아도 같은 그림이 이어지지 않게 합니다."""
    c = cat if cat in THUMB_CATS else "default"
    return "images/thumb/%s-%d.svg" % (c, n % 4 + 1)

def fill_thumbs(body):
    """.news-row 의 회색 플레이스홀더를 카테고리 기본 썸네일로 교체.
       어떤 사진이 필요한지 적어둔 문구는 주석으로 남겨 정보를 잃지 않습니다."""
    rows = re.split(r'(?=<div class="news-row"|<a class="news-row")', body)
    out, seq = [], 0
    for r in rows:
        m = re.search(r'data-cat="(\w+)"', r)
        if m or r.lstrip().startswith(("<div class=\"news-row\"", "<a class=\"news-row\"")):
            # data-cat 이 없는 외부 글 목록(대표의 다른 글)은 칼럼으로 봅니다
            cat = m.group(1) if m else "column"
            src = thumb_for(cat, seq)
            seq += 1
            r = re.sub(
                r'<div class="news-media"><div class="tag-mini">(.*?)</div></div>',
                lambda x: ('<!-- 필요한 사진: %s -->'
                           '<div class="news-media shot"><img src="%s" alt="" loading="lazy"></div>'
                           % (x.group(1).replace("<br>", " ").strip(), src)),
                r, flags=re.S)
        out.append(r)
    return "".join(out)

def fill_home_cards(body):
    """홈의 최신 소식 카드 3장도 카테고리 썸네일로."""
    def one(m):
        blk = m.group(0)
        cat = "press"
        for k in ("column", "media", "press"):
            if 'tag-%s' % k in blk:
                cat = k; break
        need = re.search(r'<div class="placeholder-tag">(.*?)</div>', blk, re.S)
        note = '<!-- 필요한 사진: %s -->' % (need.group(1).strip() if need else "")
        one.n = getattr(one, "n", -1) + 1
        return re.sub(r'<div class="biz-media">.*?</div>\s*</div>',
                      note + '<div class="biz-media shot"><img src="%s" alt="" loading="lazy"></div>'
                      % thumb_for(cat, one.n),
                      blk, count=1, flags=re.S)
    return re.sub(r'<a class="biz-card".*?</a>', one, body, flags=re.S)

def fix_body(f, body):
    # 위치 페이지: 목업의 깨진 iframe src 복구
    if f == "location.html":
        body = re.sub(r'src="https://maps\.google\.com/maps\?q=[^"]*"output=embed"',
                      'src="https://maps.google.com/maps?q=%EC%84%9C%EC%9A%B8%EC%8B%9C%20%EC%84%B1%EB%8F%99%EA%B5%AC%20%EB%AC%B4%ED%95%99%EB%A1%9C6%EA%B8%B8%2050&output=embed"',
                      body)
    # 법적 문서
    if f in ("privacy.html","terms.html"):
        body = body.replace("<article>", '<article class="legal">', 1)
    if f == "privacy.html":
        body = legal_fill(body)
    # 목업의 mono 라벨 폰트 크기 등 inline 값은 그대로 두되, 아주 작은 px 는 살짝 키움
    body = re.sub(r'font-size:1[1-3](\.\d)?px', 'font-size:var(--fs-small)', body)
    body = body.replace('font-size:14.5px','font-size:var(--fs-small)').replace('font-size:15.5px','font-size:var(--fs-body)')
    body = re.sub(r'font-size:(19|20)px', 'font-size:var(--fs-h3)', body)
    if 'class="news-row"' in body:
        body = fill_thumbs(body)
    if 'class="home-news"' in body:
        body = fill_home_cards(body)
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
    bar = hero_subbar(f, m) if section_of(f) else ""
    hero = bar if f in NO_HEAD else bar + page_head(f, m)
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
    elif f in ("privacy.html","terms.html"):
        page_css = LEGAL_CSS
    title = f'{re.sub("<.*?>","",m["h1"])} — Verdex AI'
    (OUT/f).write_text(page_html(title, section_of(f), page_css, hero, body, extra_js), encoding="utf-8")

# ── 워드프레스 글 → 우리 디자인 ──────────────────────────────────────────────
WP_CSS = """
  .wp-lead{margin:0 0 clamp(26px,3.2vw,56px);border-radius:10px;overflow:hidden;background:var(--paper)}
  .wp-lead img{width:100%;height:auto;display:block}
  .news-media.shot{border:0;background:none}
  .news-media.shot img{width:100%;height:100%;object-fit:cover;display:block}
  .back-link{display:inline-block;margin-top:clamp(34px,4vw,68px);padding-top:clamp(20px,2.4vw,36px);
    border-top:1px solid var(--line);width:100%;font-family:var(--mono);font-size:var(--fs-small);
    font-weight:700;letter-spacing:.05em;color:var(--brand)}
  .back-link:hover{color:var(--cta-hover)}
  .wp-empty{padding:clamp(40px,5vw,90px) 0;text-align:center;color:var(--muted);font-size:var(--fs-body)}
  .news-src{font-family:var(--mono);font-size:var(--fs-small);font-weight:500;
    letter-spacing:.04em;color:var(--sky)}
"""

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def wp_meta(p):
    """워드프레스 글 한 건을 페이지 메타(제목 블록 재료)로 변환."""
    return dict(
        crumb='<a href="./news.html">뉴스룸</a> / ' + esc(p["cat_label"]),
        eyebrow="", h1=esc(p["title"]), lede="",
        byline=('<span class="author">정복영</span><span>대표 · Verdex AI</span>'
                if p["cat"] == "column" else ""),
        updated=(p["date"].replace("-", ".") + ' · <a href="' + esc(p["wp_link"])
                 + '" target="_blank" rel="noopener">원문 ↗</a>'),
        subtabs=[])

def wp_post_page(p):
    f = "post-%s.html" % p["id"]
    m = wp_meta(p)
    hero = hero_subbar(f, m) + page_head(f, m)
    lead = ('<figure class="wp-lead"><img src="%s" alt="%s"></figure>'
            % (p["image"], esc(p["image_alt"]))) if p.get("image") else ""
    body = ('<main>\n<article>\n  <div class="wrap">\n    ' + lead
            + '\n    <div class="body-text">\n' + p["html"] + '\n    </div>\n'
            '    <a class="back-link" href="./news.html">← 뉴스룸으로</a>\n'
            '  </div>\n</article>\n</main>')
    (OUT/f).write_text(page_html(p["title"] + " — Verdex AI", "news", WP_CSS, hero, body),
                       encoding="utf-8")
    return f

ROW_TPL = """      <div class="news-row" data-cat="{cat}" id="{rid}">
        <a class="row-link" href="{href}"{ext} aria-label="{alt}"></a>
        {media}
        <div>
          <h3>{title}</h3>
          <div class="news-meta"><span class="tag tag-{cat}">{label}</span>{src}</div>
        </div>
        <span class="news-date">{date}</span>
      </div>"""

def is_external(p):
    """전문을 우리가 호스팅하지 않는 항목 — 목록에서 바로 원문으로 보냅니다."""
    return p["cat"] in NO_FULLTEXT or p.get("external_only")

def row_href(p):
    if is_external(p):
        return p.get("external_url") or p.get("wp_link") or "#"
    return "./post-%s.html" % p["id"]

def newsroom_items():
    """워드프레스 글 + 외부 전용 항목을 한 목록으로.
       '게시 예정'(날짜 없음)을 맨 위에, 나머지는 날짜 내림차순."""
    items = list(WP_POSTS)
    for i, e in enumerate(EXT_ITEMS):
        e = dict(e)
        e.setdefault("id", "ext%d" % i)
        e.setdefault("date", "")
        e["external_only"] = True
        items.append(e)
    pending = [i for i in items if not i.get("date")]          # 게시 예정 — 맨 위
    dated   = sorted([i for i in items if i.get("date")],
                     key=lambda i: i["date"], reverse=True)     # 나머지 최신순
    return pending + dated

def wp_news_rows(posts):
    rows = []
    for _i, p in enumerate(posts):
        img = p.get("image") or thumb_for(p["cat"], _i)
        media = ('<div class="news-media shot"><img src="%s" alt="" loading="lazy"></div>' % img)
        ext = is_external(p)
        src = ""
        if p.get("source"):
            src = '<span class="news-src">%s ↗</span>' % esc(p["source"])
        elif ext:
            src = '<span class="news-src">원문 ↗</span>'
        rows.append(ROW_TPL.format(
            cat=p["cat"], rid="wp-%s" % p["id"], href=row_href(p),
            ext=' target="_blank" rel="noopener"' if ext else "",
            alt=esc(p["title"]), media=media, title=esc(p["title"]),
            label=esc(p["cat_label"]), src=src,
            date=p.get("date_label") or (p["date"].replace("-", ".") if p.get("date") else "게시 예정")))
    return "\n\n".join(rows) or ('<div class="wp-empty">아직 가져온 글이 없습니다. '
                                 '<code>python3 wp_sync.py</code> 를 먼저 실행하세요.</div>')

NEWS_SHELL = """<main>
<section>
  <div class="wrap">
    <div class="filters">
      <button class="filter-btn active" data-filter="all">전체</button>
      <button class="filter-btn" data-filter="media">미디어보도</button>
      <button class="filter-btn" data-filter="press">보도자료</button>
      <button class="filter-btn" data-filter="column">칼럼</button>
    </div>

    <p id="columnNote">
      정복영 대표의 「탄소중립개론」 칼럼은 CO2Korea에서 매주 수요일 동시 게재됩니다 —
      <a href="https://www.co2korea.com/news/articleList.html?sc_sub_section_code=S2N44&amp;view_type=sm" target="_blank" rel="noopener">CO2Korea에서 보기 ↗</a>
    </p>

    <div class="news-list" id="newsList">
{rows}
    </div>
  </div>
</section>
</main>"""

def wp_newsroom(fname, posts):
    m = dict(crumb="", eyebrow="", h1="뉴스룸", lede="", byline="", updated="", subtabs=[])
    hero = hero_subbar("news.html", m)
    body = NEWS_SHELL.format(rows=wp_news_rows(posts))
    (OUT/fname).write_text(page_html("뉴스룸 — Verdex AI", "news", WP_CSS, hero, body, NEWS_JS),
                           encoding="utf-8")

if WP_POSTS or EXT_ITEMS:
    _made = [wp_post_page(_p) for _p in WP_POSTS if not is_external(_p)]
    _items = newsroom_items()
    _target = "news.html" if WP_NEWSROOM else "news-live.html"
    wp_newsroom(_target, _items)
    print("  뉴스룸 %d건 → 전문 %d건(post-*.html) · 외부링크 %d건 → %s"
          % (len(_items), len(_made), len(_items) - len(_made), _target))
else:
    print("  (content/wp-posts.json 없음 — python3 wp_sync.py 를 먼저 실행하면 워드프레스 글이 붙습니다)")


# ── 홈 ──────────────────────────────────────────────────────────────────────
top   = (SHELL/"home-top.html").read_text(encoding="utf-8")
lower = (SHELL/"home-lower.html").read_text(encoding="utf-8")
lower = fill_home_cards(lower)   # 홈 최신 소식 카드도 기본 썸네일
(OUT/"index.html").write_text(
    page_html("Verdex AI — 탄소는 비용이 아니라, 자산입니다", "", homecss, top, lower,
              f"\n<script>\n{homejs}</script>"), encoding="utf-8")

# ── 이미지 복사 ──────────────────────────────────────────────────────────────
if (ROOT/"images").exists():
    shutil.copytree(ROOT/"images", OUT/"images", dirs_exist_ok=True)

print(f"built {len(pages)+1} pages → {OUT}")
if PENDING:
    print("\n  ⚠ 회사 확인 대기 %d건 — content/company.json 에 채우세요:" % len(PENDING))
    for _t in PENDING:
        print("     · " + _t)
    print("     (채우기 전에는 개인정보처리방침에 주황색 표시가 남습니다)")
