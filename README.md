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

## 대표님이 글을 올리는 법 — 헤드리스 워드프레스

**대표님은 지금까지 하시던 대로 verdex.kr 워드프레스(wp-admin)에서 글을 쓰시면 됩니다.**
새로 배우실 도구도, 워드프레스에 설치할 플러그인도 없습니다.
워드프레스는 이제 공개 사이트가 아니라 **글 쓰는 도구**로만 씁니다.

```
대표님: wp-admin 에서 글 발행
   ↓  (REST API)
python3 wp_sync.py      ← 글·카테고리·대표이미지를 content/wp-posts.json 으로
   ↓
python3 build.py        ← 우리 디자인의 뉴스룸 + 글 페이지 생성
   ↓
site/ 폴더 배포
```

### 실행

```bash
python3 wp_sync.py          # 전체 동기화
python3 wp_sync.py --limit 5   # 최신 5개만 (테스트)
python3 wp_sync.py --no-images # 이미지 빼고 글만
python3 build.py
```

만들어지는 것

| 결과 | 설명 |
|---|---|
| `content/wp-posts.json` | 가져온 글 원본 (빌드가 읽는 파일) |
| `images/wp/` | 대표이미지 |
| `site/post-<글번호>.html` | 글 상세 페이지 |
| `site/news-live.html` | 워드프레스 글로 채운 뉴스룸 |

지금은 손으로 쓴 `news.html` 과 워드프레스판 `news-live.html` 이 **둘 다** 만들어집니다.
비교해 보시고 워드프레스판으로 확정되면 `build.py` 맨 위의

```python
WP_NEWSROOM = False   →   True
```

한 줄만 바꾸면 `news.html` 자체가 워드프레스 글로 채워집니다.

### 카테고리 연결

워드프레스 카테고리를 뉴스룸 필터(미디어보도·보도자료·칼럼)에 잇는 표는
`wp_sync.py` 맨 위 `CAT_MAP` 에 있습니다. 카테고리를 새로 만드시면 여기 한 줄만 추가하면 됩니다.

```python
CAT_MAP = {
    "탄소중립강좌": ("column", "칼럼"),
    "소식":        ("press",  "보도자료"),
    "언론보도":     ("media",  "미디어보도"),
}
```

### 자동화

`wp_sync.py → build.py` 를 GitHub Actions 에 걸면 사람 손이 아예 빠집니다.
하루 한 번 또는 대표님이 글을 올리실 때마다 돌려서 `site/` 를 다시 만들고 배포하면 됩니다.

> **주의** — `content/wp-posts.json` 이 저장소에 들어 있다면 그건 화면 확인용 샘플입니다.
> `wp_sync.py` 를 한 번 돌리면 실제 데이터로 덮어써집니다.

### 저작권 규칙 — 뉴스룸 3분류 (반드시 유지)

인수인계 메모 1.3 항목을 빌드 단계에서 강제합니다.

| 분류 | 전문 게재 | 링크 | 근거 |
|---|---|---|---|
| **보도자료** `press` | ○ `post-<id>.html` 생성 | 사이트 내부 | 회사 저작물 |
| **칼럼** `column` | ○ `post-<id>.html` 생성 | 사이트 내부 | 대표 저작물 |
| **미디어보도** `media` | **✕ 생성 안 함** | 언론사 원문 새 창 | 언론사 저작권 |

`media` 로 분류된 글은 `wp_sync.py` 가 본문을 **아예 저장하지 않고**(`html: ""`),
본문 안의 첫 외부 링크를 `external_url` 로 뽑아 둡니다. `build.py` 는 이 글에 대해
상세 페이지를 만들지 않고 목록에서 바로 원문으로 내보냅니다.
따라서 대표님이 워드프레스에서 카테고리만 "언론보도"로 고르시면 규칙이 자동으로 지켜집니다.

### 게시 예정 글 — content/external.json

아직 verdex.kr 에 없고 CO2Korea 등 외부에만 있는 글은 `content/external.json` 에 적습니다.
뉴스룸 목록 **맨 위**에 "게시 예정"으로 노출되고 원문으로 연결됩니다.

```json
[{ "title": "[탄소중립개론]11. 기후위기와 죄수의 딜레마",
   "cat": "column", "cat_label": "칼럼",
   "date": "", "date_label": "게시 예정",
   "source": "CO2Korea",
   "external_url": "https://www.co2korea.com/news/articleView.html?idxno=2614" }]
```

대표님이 그 글을 워드프레스에 실제로 발행하시면, 이 파일에서 해당 줄만 지우면 됩니다.
그러면 워드프레스판이 전문 게재로 자동 전환됩니다.

## 뉴스룸 기본 썸네일

실제 사진이 없는 글에 쓰는 브랜드 기본 이미지입니다. 로고 잎 마크를 허브로 두고
랜딩 히어로와 같은 직선·노드가 뻗어 나가는 구성이라 사이트 전체와 한 언어로 묶입니다.

```bash
python3 make_thumbs.py     # images/thumb/*.svg 재생성 (표준 라이브러리만, 설치 불필요)
```

| 파일 | 쓰이는 곳 |
|---|---|
| `images/thumb/press-1~4.svg` | 보도자료 |
| `images/thumb/column-1~4.svg` | 칼럼 |
| `images/thumb/media-1~4.svg` | 미디어보도 (밝은 톤 — 외부 기사라 구분) |
| `images/thumb/default-1~4.svg` | 그 외 |
| `images/thumb/og-default.svg` | 링크 공유용 1200×630 (SEO 작업 때 og:image) |

카테고리마다 4종을 두고 목록 순서대로 돌려쓰기 때문에, 같은 카테고리가 연달아 나와도
선 각도가 달라 반복처럼 보이지 않습니다. SVG라 한 장 3.4KB고 어떤 크기에서도 선명합니다.

**실제 사진이 들어오면** 그 글의 썸네일은 자동으로 사진으로 바뀝니다 —
워드프레스 글은 대표이미지를 지정하면 되고, 손으로 쓴 글은 `src/` 의 해당 줄을 바꾸면 됩니다.
빌드가 원래 자리에 `<!-- 필요한 사진: ... -->` 주석을 남겨두므로 어떤 사진이 필요한지는 그대로 남아 있습니다.
