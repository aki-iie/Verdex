# Verdex AI — 로고 애셋 사용 안내

원본(149×69px PNG)을 벡터로 트레이싱해 만든 세트입니다. 흰 배경은 제거(투명)되어 있습니다.
**인쇄물(명함·현수막·보고서 표지)에는 반드시 디자이너가 만든 원본 AI/EPS 파일을 쓰세요.**
이 SVG는 웹용으로는 충분하지만, 149px 래스터에서 복원한 것이라 곡선이 원본과 미세하게 다를 수 있습니다.

## 파일

| 파일 | 용도 |
|---|---|
| `verdex-logo-color.svg` | 흰색/밝은 배경 (기본) |
| `verdex-logo-ondark.svg` | 남색 배경 — 잎은 초록 유지, 글자만 흰색 |
| `verdex-logo-white.svg` | 사진·짙은 배경 위 단색 흰색 (잎맥은 투명) |
| `verdex-logo-mono-ink.svg` | 흑백 인쇄·팩스용 |
| `verdex-mark.svg` | 잎 심볼 단독 (앱 아이콘·워터마크·SNS 프로필) |
| `verdex-mark-white.svg` | 잎 심볼 흰색 |
| `verdex-favicon.svg` | 초록 라운드 사각 + 흰 잎 — 16px에서도 읽힘 |
| `favicon-32.png` / `apple-touch-icon.png` | 브라우저 탭 · iOS 홈 화면 |
| `png/*.png` | SVG를 못 쓰는 곳(메일 서명, 일부 문서)용 |

## 색

| 이름 | HEX | 용도 |
|---|---|---|
| Verdex Green | `#2E8B3A` | 브랜드 기본 · CTA · 강조 |
| Green Deep | `#1F6B2B` | hover · 그라데이션 어두운 쪽 |
| Ink | `#22251F` | 워드마크 · 본문 텍스트 |
| Navy | `#0A3A63` | 다크 배경 · 헤딩 |
| Sky | `#0E7FAB` | 데이터 · 보조 |
| Mint | `#6BC08A` | 다크 배경 위 액센트 |

## 사용 규칙

- 최소 가로 96px. 그보다 작으면 `verdex-mark.svg`만 사용.
- 여백(clear space)은 잎 높이의 40% 이상. 다른 요소를 그 안에 넣지 않습니다.
- 사진 위에는 `verdex-logo-white.svg`만. 컬러 버전을 사진에 직접 얹지 않습니다.
- 금지: 비율 왜곡, 그림자·외곽선 추가, 색 임의 변경, 잎과 글자 간격 변경, 회전.

## HTML 적용 예

```html
<!-- 헤더: 배경 밝기에 따라 교차 -->
<a class="brand" href="./index.html">
  <img class="logo-light" src="images/brand/verdex-logo-color.svg" alt="Verdex AI" height="32">
  <img class="logo-dark"  src="images/brand/verdex-logo-white.svg" alt="Verdex AI" height="32">
</a>

<!-- <head> -->
<link rel="icon" href="images/brand/verdex-favicon.svg" type="image/svg+xml">
<link rel="icon" href="images/brand/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="images/brand/apple-touch-icon.png">
```
