# Verdex AI 홈페이지

베르덱스에이아이(verdex.kr) 홈페이지 리뉴얼 작업 저장소입니다.
정적 HTML 44개 페이지로 이루어져 있고, 별도의 서버나 빌드 도구 없이 동작합니다.

## 바로 보는 법

**`site/index.html` 을 브라우저로 열면 됩니다.** 그게 전부입니다.

설치할 것도, 실행할 서버도 없습니다. 44개 페이지가 서로 링크되어 있어
상단 메뉴와 본문 링크만으로 사이트 전체를 돌아볼 수 있습니다.

> 저장소를 내려받았다면: 압축을 푼 뒤 `site` 폴더 안의 `index.html` 을 더블클릭하세요.
> 크롬·사파리·엣지 어디서든 열립니다.

주요 페이지

| 페이지 | 파일 |
|---|---|
| 랜딩 | `site/index.html` |
| 회사 소개 — 개요 | `site/about-overview.html` |
| 회사 소개 — 리더십 | `site/about-leadership.html` |
| 사업 분야 | `site/business-overview.html` |
| 뉴스룸 | `site/news.html` |

## 폴더 구조

```
verdex-site-v3/
├── site/          ← 완성된 HTML 44개 + images/  (배포하거나 열어보는 건 이 폴더)
├── build.py       ← 생성 스크립트.  python3 build.py  → site/ 를 다시 만듦
├── shell/         ← 전 페이지 공통 껍데기
│   ├── site.css       색·폰트·유동 스케일·공통 섹션 스타일
│   ├── header.html    고정 헤더 + 메가메뉴 + 모바일 메뉴
│   ├── footer.html    6단 푸터
│   ├── site.js        헤더 색 전환 · 메가메뉴 · 모바일 메뉴
│   ├── home-top.html  랜딩 히어로 (풍력 사진 + 녹색 라인 SVG)
│   ├── home-lower.html 랜딩 하단 (사업분야 · 뉴스룸 · 지표 · 신뢰근거 · CTA)
│   └── home.css / home.js
├── src/           ← 페이지별 본문 42개 + pages.json (제목·서브탭 메타)
└── images/        ← 사진 · 브랜드 로고 (images/brand/)
```

## 고치는 법

| 바꾸고 싶은 것 | 손댈 파일 |
|---|---|
| 색·폰트·간격 | `shell/site.css` 맨 위 `:root` |
| 상단 메뉴 · 푸터 | `shell/header.html`, `shell/footer.html` |
| 랜딩 히어로 | `shell/home-top.html`, `shell/home.css` |
| 어떤 페이지의 본문 | `src/<페이지>.html` |
| 페이지 제목 · 서브탭 | `src/pages.json` |

고친 뒤 `python3 build.py` 를 한 번 실행하면 `site/` 가 전부 다시 생성됩니다.
`site/*.html` 을 직접 고쳐도 되지만 다음 빌드 때 덮어써지니 급한 확인용으로만 쓰세요.

## 디자인 기준

- 브랜드 그린 `#2E8B3A` (로고에서 추출) · 네이비 `#0A3A63` · CTA `#3A6B46`
- 로고 애셋과 사용 규칙은 `images/brand/BRAND.md`
- 회사 소개 챕터는 "개요" 페이지의 구성(로고 밑 탭 바 → 화면 단위 섹션)을 기준으로 맞춰갑니다

## 아직 확정 전

- 사진 자리(점선 상자) — 대표 프로필 외 나머지는 미정
- 홈 지표 4개 중 3개가 예시 수치
- 개인정보처리방침 · 이용약관의 `[확인 필요]` 공란 (법률 검토 전)
- 문의 폼 — 화면만 있고 전송 기능 없음
- 히어로 풍력 사진 — 라이선스 확인 필요
