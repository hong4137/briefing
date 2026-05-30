# CLCO_PRD.md v3 — PWA 제거 + 리드와이즈 리더 테마 + 핸드픽 이미지 맵 최종 설계 명세서

> **작성**: 클코 (Cl-Co / 설계자)
> **기반**: 안티 (Anti / 계획자) 2차 지시서 v2.0 + 유저 피드백 v3 (API 키 없는 핸드픽 이미지 맵)
> **날짜**: 2026-05-28
> **수신**: 코덱스 (Codex / 전문 코더)

---

## 0. 현황 파악 (As-Is v2)

### 파일 트리 현재 상태

```
briefing/
├── index.html        ← PWA 코드 전체 포함 (메타 태그, CSS, HTML 배너, JS 등록)
├── archive.html      ← PWA 코드 전체 포함
├── about.html        ← PWA 코드 전체 포함
├── search.html       ← PWA 코드 전체 포함
├── manifest.json     ← [DELETE 대상]
├── sw.js             ← [DELETE 대상]
├── theme-modern.css  ← [DONE] 코덱스 1차 구현 완료, 구조 유효
├── icons/            ← 아이콘 파일 폴더 (삭제 불필요)
└── archive/          ← 기사 HTML 파일들
```

### 코덱스 1차 구현 상태 점검

`theme-modern.css` 검토 결과:
- CSS 변수(`:root`), `body.shell-page`, `body.reader-mode` 네임스페이스 격리 구조 **정상**
- GNB 글래스모피즘, 히어로 이미지, 타임라인 리스트, 리더 푸터 CSS **정상**
- 범용 선택자(`body {}`, `p {}`, `.container {}` 등) 미사용 **확인**
- **추가 필요**: 없음 (구조 완전하나, 4대 HTML에 `body.shell-page` 클래스 아직 미적용)

---

## 1. PWA 완전 제거 명세

### 1-1. 삭제 대상 파일

코덱스는 아래 두 파일을 저장소에서 **완전히 삭제**한다.

| 파일 | 액션 | 비고 |
|---|---|---|
| `briefing/manifest.json` | **DELETE** | PWA 앱 매니페스트 |
| `briefing/sw.js` | **DELETE** | 서비스 워커 스크립트 |

> `briefing/icons/` 폴더는 삭제하지 않는다. (파비콘 아이콘으로 재활용 가능)

---

### 1-2. 4대 HTML 공통 제거 블록 정의

아래 4개 파일에서 동일한 패턴의 코드를 제거한다:
- `index.html`
- `archive.html`
- `about.html`
- `search.html`

#### [A] `<head>` 내 PWA 메타 태그 블록 제거

아래 7줄 전체를 삭제한다. (파일마다 내용 동일)

```html
<!-- 제거 대상 - HEAD 내 PWA 메타 태그 블록 -->
<!-- PWA Meta Tags -->
<meta name="theme-color" content="#0a0a0f">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="JFNB">
<meta name="application-name" content="JFNB">
<meta name="msapplication-TileColor" content="#0a0a0f">
<meta name="msapplication-TileImage" content="icons/icon-144x144.png">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" sizes="180x180" href="icons/icon-192x192.png">
```

**유지 대상** (파비콘은 PWA 전용이 아니므로 보존):
```html
<!-- 유지 - 일반 파비콘 -->
<link rel="icon" type="image/png" sizes="32x32" href="icons/icon-96x96.png">
<link rel="icon" type="image/png" sizes="16x16" href="icons/icon-72x72.png">
```

#### [B] `<style>` 내 PWA CSS 블록 제거

각 파일의 `<style>` 태그 내에서 아래 섹션 전체를 삭제한다.
시작 주석(`/* PWA Install Banner */`)부터 끝 미디어 쿼리까지를 찾아 제거한다.

```css
/* 제거 대상 CSS 블록 - 시작 ~ 끝 */
/* PWA Install Banner */
.pwa-install-banner { ... }
.pwa-install-banner.show { ... }
@keyframes slideUp { ... }
.pwa-banner-content { ... }
.pwa-banner-info { ... }
.pwa-banner-icon { ... }
.pwa-banner-text h4 { ... }
.pwa-banner-text p { ... }
.pwa-banner-actions { ... }
.pwa-btn-install { ... }
.pwa-btn-install:hover { ... }
.pwa-btn-dismiss { ... }
.pwa-btn-dismiss:hover { ... }

/* PWA Update Toast */
.pwa-update-toast { ... }
.pwa-update-toast.show { ... }
@keyframes fadeInUp { ... }
.pwa-update-toast span { ... }
.pwa-update-btn { ... }

@media (max-width: 480px) {
    .pwa-install-banner { ... }
    .pwa-banner-text p { ... }
}
```

#### [C] `<body>` 내 PWA HTML 배너 제거

아래 두 HTML 블록을 삭제한다.

```html
<!-- 제거 대상 HTML 블록 1 -->
<!-- PWA Install Banner -->
<div class="pwa-install-banner" id="pwaInstallBanner">
    ... (전체 내용)
</div>

<!-- 제거 대상 HTML 블록 2 -->
<!-- PWA Update Toast -->
<div class="pwa-update-toast" id="pwaUpdateToast">
    ... (전체 내용)
</div>
```

#### [D] `<script>` PWA 등록 블록 제거

`<!-- PWA Registration -->` 주석과 해당 `<script>` 태그 전체를 삭제한다.

```html
<!-- 제거 대상 스크립트 블록 전체 -->
<!-- PWA Registration -->
<script>
    // Service Worker Registration
    let deferredPrompt = null;
    let swRegistration = null;

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', async () => {
            ... (전체 내용)
        });
    }

    // Install Prompt
    window.addEventListener('beforeinstallprompt', (e) => { ... });

    async function installPWA() { ... }
    function dismissInstallBanner() { ... }
    function updatePWA() { ... }

    window.addEventListener('appinstalled', () => { ... });
</script>
```

---

### 1-3. 파일별 PWA 코드 위치 참조표

코덱스가 각 파일에서 제거할 정확한 코드 위치.

#### `index.html`

| 제거 항목 | 위치 (참조용 라인) | 비고 |
|---|---|---|
| [A] PWA 메타 태그 | `<head>` 내, `<!-- PWA Meta Tags -->` ~ `<link rel="apple-touch-icon">` | 10줄 |
| [B] PWA CSS | `<style>` 내, `/* PWA Install Banner */` ~ 마지막 `@media (max-width: 480px)` 블록 | ~120줄 |
| [C] 배너 HTML | `<body>` 후반부, `<!-- PWA Install Banner -->` div + `<!-- PWA Update Toast -->` div | ~35줄 |
| [D] 등록 스크립트 | `<!-- PWA Registration -->` `<script>` 블록 전체 | ~72줄 |

#### `archive.html`

| 제거 항목 | 위치 (참조용 라인) | 비고 |
|---|---|---|
| [A] PWA 메타 태그 | `<head>` 내, `<!-- PWA Meta Tags -->` ~ `<link rel="apple-touch-icon">` | 10줄 |
| [B] PWA CSS | `<style>` 내, `/* PWA Install Banner */` ~ 마지막 `@media` 블록 | ~120줄 |
| [C] 배너 HTML | `<body>` 후반부 | ~25줄 |
| [D] 등록 스크립트 | `<!-- PWA Registration -->` `<script>` 블록 전체 | ~72줄 |

#### `about.html`

| 제거 항목 | 위치 (참조용 라인) | 비고 |
|---|---|---|
| [A] PWA 메타 태그 | `<head>` 내 | 10줄 |
| [B] PWA CSS | `<style>` 내 `/* PWA Install Banner */` ~ 끝 | ~120줄 |
| [C] 배너 HTML | `<body>` 후반부 | ~25줄 |
| [D] 등록 스크립트 | `<!-- PWA Registration -->` `<script>` 블록 | ~72줄 |

#### `search.html`

| 제거 항목 | 위치 (참조용 라인) | 비고 |
|---|---|---|
| [A] PWA 메타 태그 | `<head>` 내 | 10줄 |
| [B] PWA CSS | `<style>` 내 `/* PWA Install Banner */` ~ 끝 | ~120줄 |
| [C] 배너 HTML | `<body>` 후반부 | ~25줄 |
| [D] 등록 스크립트 | `<!-- PWA Registration -->` `<script>` 블록 | ~72줄 |

---

## 2. 서비스 워커 강제 해제 (SW Unregister) 클린업 스크립트

### 2-1. 목적

`sw.js`와 `manifest.json`을 삭제하더라도, 이미 해당 사이트에 방문한 기존 사용자의 브라우저에는 서비스 워커가 **등록된 상태로 남아 있다.** 이 경우:

- 서비스 워커가 구버전 캐시를 계속 서빙 → 최신 HTML/CSS가 반영되지 않음
- `sw.js` 파일이 삭제되었으므로 워커가 다음 업데이트를 받을 수 없음 → 무기한 구버전 캐시 상태 지속

이를 해결하기 위해 4대 HTML 파일에 **클린업 스크립트**를 삽입한다.

### 2-2. 클린업 스크립트 코드

```html
<!-- SW Cleanup: Unregister any previously installed service workers -->
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
      for (let registration of registrations) {
        registration.unregister();
      }
    });
    caches.keys().then(function(cacheNames) {
      cacheNames.forEach(function(cacheName) {
        caches.delete(cacheName);
      });
    });
  }
</script>
```

> **기존 지시서 스크립트 대비 추가사항**: `caches.keys().then(...)` 블록을 추가하여 서비스 워커가 남긴 캐시 스토리지까지 함께 삭제한다. 서비스 워커 해제만으로는 캐시가 남을 수 있기 때문이다.

### 2-3. 삽입 위치

4개 HTML 파일(`index.html`, `archive.html`, `about.html`, `search.html`)의 `<head>` 내,
**`<title>` 태그 직전**에 삽입한다.

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- 파비콘 (유지) -->
  <link rel="icon" type="image/png" sizes="32x32" href="icons/icon-96x96.png">
  <link rel="icon" type="image/png" sizes="16x16" href="icons/icon-72x72.png">

  <!-- ★ SW Cleanup - 여기에 삽입 -->
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for (let registration of registrations) {
          registration.unregister();
        }
      });
      caches.keys().then(function(cacheNames) {
        cacheNames.forEach(function(cacheName) {
          caches.delete(cacheName);
        });
      });
    }
  </script>

  <title>...</title>
  ...
```

**왜 `<title>` 직전인가?**
- `<head>` 내 가장 이른 위치에서 비동기적으로 실행되어야 캐시 충돌을 페이지 렌더링 전에 최대한 일찍 처리할 수 있다.
- 렌더링을 블로킹하지 않는다 (Promise 기반 비동기 코드이므로).

### 2-4. 향후 제거 시점

이 클린업 스크립트는 **영구 코드가 아니다.** 기존 방문자들의 브라우저에서 구 서비스 워커가 완전히 청소될 예상 기간(배포 후 약 4~8주) 이후에 제거해도 된다. 단, 당분간은 남겨두어도 무해하다(`getRegistrations()`가 빈 배열을 반환할 뿐).

---

## 3. `body` 클래스 적용 (Shell Page 활성화)

`theme-modern.css`의 `body.shell-page` 및 `body.reader-mode` 스타일이 실제로 적용되려면 각 HTML 파일의 `<body>` 태그에 클래스가 있어야 한다.

### 3-1. 셸 페이지 4개 파일

| 파일 | 변경 전 | 변경 후 |
|---|---|---|
| `index.html` | `<body>` | `<body class="shell-page">` |
| `archive.html` | `<body>` | `<body class="shell-page archive-page">` |
| `about.html` | `<body>` | `<body class="shell-page">` |
| `search.html` | `<body>` | `<body class="shell-page">` |

### 3-2. 기사 본문 페이지 (포스트 프로세서 처리)

`archive/*.html` 파일은 포스트 프로세서(`scripts/post_process.py`)가 자동으로 처리한다.
수동으로 변경하지 않는다.

---

## 4. 스타일 격리 아키텍처 (Style Isolation — Clean Room 재확인)

### 4-1. 격리 원칙 재확인

`theme-modern.css` 검토 결과 올바르게 구현되어 있음을 확인했다.
코덱스는 이 파일을 **수정하지 않는다.** 구조 요약:

```
theme-modern.css
│
├─ :root { }                         ← CSS 변수만. 전역 선택자 없음.
│
├─ body.shell-page .xxx { }          ← 셸 페이지 전용 (index/archive/about/search)
│    ├─ .nav, .gnb → GNB 스타일
│    ├─ .timeline-list → 타임라인 목록
│    └─ .footer → 푸터
│
└─ body.reader-mode .xxx { }         ← 기사 페이지 전용 (archive/*.html)
     ├─ .reader-nav → 미니멀 GNB
     ├─ .reader-hero → 히어로 이미지
     └─ .reader-footer → 리더 푸터
```

### 4-2. 기사 본문 HTML 충돌 방지 규칙

`archive/YYYY-MM-DD.html` 기사 파일들은 자체 `<style>` 블록에서 아래 선택자를 사용한다:

```css
/* 기사 자체 스타일 (절대 수정 불가) */
body { font-family: ...; background: ...; }
.container { max-width: 900px; ... }
.article-card { ... }
.section-title { ... }
h2.section-title { ... }
```

`theme-modern.css`는 `body.reader-mode` 접두사로 격리되어 있으므로 이들과 충돌하지 않는다.
단, `body { background: ...; }` vs `body.reader-mode { background: ...; }` 에서 후자가 명시도(specificity)가 높아 승리한다. 이 경우 기사의 원래 body 배경색이 `theme-modern.css`의 `#121214`로 덮이는데, 두 값이 시각적으로 유사(`#0a0a0f` vs `#121214`)하므로 실질적 문제는 없다.

---

## 5. Coal Dark 테마 + 타이포그래피 최종 사양 확인

기존 `theme-modern.css`에 구현된 사양 확인. 변경 없음.

### 5-1. 색상 팔레트 (확정)

```
배경 기본:      #121214   (Coal Dark — 순흑보다 밝고 따뜻한 차콜)
배경 패널:      #18181b   (카드, 오버레이)
배경 호버:      #26262c
텍스트 1차:     #e8e8ea   (순백 아닌 오프화이트 — 장시간 독서 피로 감소)
텍스트 2차:     #9898a6
텍스트 3차:     #5c5c70   (날짜, 메타)
경계선:         rgba(255,255,255,0.08)
GNB 배경:       rgba(18,18,20,0.80) + backdrop-filter: blur(20px) saturate(160%)
액센트:         #e84040 (레드), #4a9eff (블루), #f5c842 (골드)
```

### 5-2. 타이포그래피 사양 (확정)

```
폰트 스택 (UI):    Outfit → Noto Sans KR → -apple-system → sans-serif
폰트 스택 (모노):  JetBrains Mono
폰트 스택 (세리프): Playfair Display

본문 독서 폭:      max-width: 680px (--reading-width)
셸 콘텐츠 폭:      max-width: 1200px (--content-width)
줄 간격:           1.82 (한글/영문 혼용 최적값)
폰트 크기 기준:    16px (브라우저 기본값 유지)
한글 자간:         Noto Sans KR 자동 (별도 letter-spacing 불필요)
```

---

## 6. 핸드픽 프리미엄 이미지 맵 (API 키 불필요 — v3 신규)

### 6-0. 설계 배경 및 v2 대비 변경점

| 항목 | v2 (Unsplash API) | v3 (핸드픽 맵) |
|---|---|---|
| API 키 필요 | 필요 (`UNSPLASH_ACCESS_KEY`) | **불필요** |
| GitHub Actions Secret | 필요 | **불필요** |
| 호출 방식 | 빌드 시 HTTP 요청 | **Python 딕셔너리 조회 (로컬)** |
| 이미지 변화 | 매 빌드 달라짐(랜덤) | **날짜 해시 기반 결정론적 선택** |
| 장애 위험 | API 다운/할당 초과 시 실패 | **없음 (오프라인 동작)** |
| 이미지 품질 | 검색 결과 품질 변동 | **사전 큐레이션된 초고화질만** |

Unsplash CDN URL은 API 인증 없이 공개 접근이 가능하다.
URL 형식: `https://images.unsplash.com/photo-{ID}?w=1200&q=80&fit=crop&auto=format`

---

### 6-1. 우선순위 체계 (v3 확정)

```
Priority 1: 기사 HTML 내 이미지 감지 → 히어로로 승격      [변경 없음]
Priority 2: CATEGORY_IMAGE_MAP 조회 → 카테고리 핸드픽 이미지  [신규 - API 불필요]
Priority 3: DEFAULT_IMAGE_POOL 조회 → 기본 테크 이미지      [신규 - API 불필요]
Priority 4: CSS 그라데이션 폴백                           [변경 없음]

[제거됨] Unsplash Search API 호출 (Priority 2, 3)
```

---

### 6-2. 카테고리 탐지 키워드 패턴 (Python regex)

```python
CATEGORY_PATTERNS = [
    # (카테고리 키, regex 패턴)
    ("ai",          r'AI|인공지능|LLM|ChatGPT|Gemini|Claude|Grok|딥러닝|머신러닝|GPT|오픈AI|OpenAI|Anthropic'),
    ("chip",        r'반도체|칩|HBM|TSMC|SK하이닉스|하이닉스|마이크론|Micron|NVIDIA|엔비디아|삼성전자|파운드리|웨이퍼'),
    ("finance",     r'주식|증시|S&P|나스닥|시총|IPO|상장|월가|투자|채권|금리|연준|Fed|주가|코스피|다우'),
    ("robot",       r'로봇|휴머노이드|Unitree|보스턴다이내믹스|Figure|Agility|자동화|드론'),
    ("space",       r'우주|SpaceX|스타링크|Starlink|위성|로켓|발사|NASA|스타십|Starship|ISS'),
    ("health",      r'헬스|의료|Fitbit|웨어러블|건강|바이오|임상|FDA|제약|스마트워치|애플워치'),
    ("ev",          r'전기차|EV|배터리|Tesla|테슬라|리비안|BYD|충전|전동화|자율주행'),
    ("economy",     r'무역|관세|수출|수입|경제|글로벌|GDP|인플레|관세|공급망|달러|환율'),
]
```

탐지 우선순위: 리스트 순서대로 첫 번째 매칭 카테고리 사용.
기사 제목 + 요약 텍스트를 합쳐서 탐지한다.

---

### 6-3. 핸드픽 프리미엄 이미지 맵 (CATEGORY_IMAGE_MAP)

각 카테고리별 4장, 기본 풀 4장. 총 36장 큐레이션.
선택 알고리즘: `index = int(md5(date_str)) % len(pool)` (날짜 결정론적)

```python
# post_process.py 내 상단 상수로 선언
BASE = "https://images.unsplash.com/photo-"
PARAMS_LG = "?w=1200&q=80&fit=crop&auto=format"
PARAMS_SM = "?w=640&q=80&fit=crop&auto=format"

def _img(photo_id, alt, credit_name, credit_slug):
    return {
        "url":         BASE + photo_id + PARAMS_LG,
        "url_small":   BASE + photo_id + PARAMS_SM,
        "alt":         alt,
        "credit_name": credit_name,
        "credit_url":  f"https://unsplash.com/photos/{photo_id}",
    }

CATEGORY_IMAGE_MAP = {

    # ── AI / 인공지능 ─────────────────────────────────────────────
    "ai": [
        _img("1677442135703-1787eea5ce01",
             "Blue neural network visualization on dark background",
             "Growtika", "growtika"),
        _img("1620712943543-bcc4688e7485",
             "Humanoid robot face with silver metallic surface",
             "Possessed Photography", "possessedphotography"),
        _img("1526378722484-bd91ca387e72",
             "Robot hand reaching through digital interface",
             "Franck V.", "franckinjapan"),
        _img("1655720828018-edd2daec9349",
             "Abstract AI data streams in deep blue",
             "Steve Johnson", "steve_j"),
    ],

    # ── 반도체 / 칩 ──────────────────────────────────────────────
    "chip": [
        _img("1518770660439-4636190af475",
             "Close-up of blue printed circuit board",
             "Alexandre Debiève", "alexkixa"),
        _img("1563770557593-f9e36f476dc8",
             "Silicon semiconductor wafer under purple light",
             "Laura Ockel", "lauraockel"),
        _img("1591696331111-ef9586a5b17a",
             "Macro shot of CPU processor chip",
             "Slejven Djurakovic", "slavudin"),
        _img("1601004890684-d8cbf643f5f2",
             "Intel microprocessor on motherboard close-up",
             "Olivier Collet", "olivier_collet"),
    ],

    # ── 주식 / 금융 ──────────────────────────────────────────────
    "finance": [
        _img("1611974789855-9c2a0a7236a3",
             "Stock market candlestick chart on dark screen",
             "Maxim Hopman", "nampoh"),
        _img("1590283603385-17ffb3a7f29f",
             "Charging Bull bronze statue on Wall Street",
             "Konstantin Evdokimov", "konstantinv"),
        _img("1579621970563-ebec7560ff3e",
             "Financial data graph with upward trend on dark background",
             "Tech Daily", "techdailyca"),
        _img("1638913971789-f64cf5acac09",
             "Multiple trading monitors showing financial data",
             "Austin Distel", "austindistel"),
    ],

    # ── 로봇 / 휴머노이드 ─────────────────────────────────────────
    "robot": [
        _img("1485827404703-89b55fcc595e",
             "White humanoid robot standing against grey background",
             "Alex Knight", "agk42"),
        _img("1535378917042-10a22c95931a",
             "Industrial robotic arm in dark factory",
             "Lenny Kuhne", "lennykuhne"),
        _img("1561144257-e32e8efc6c4f",
             "Robotic arm welding with sparks in dark setting",
             "Ant Rozetsky", "rozetsky"),
        _img("1508614589041-895b88991e3e",
             "Futuristic robot head with glowing eyes",
             "Possessed Photography", "possessedphotography"),
    ],

    # ── 우주 / SpaceX / 위성 ─────────────────────────────────────
    "space": [
        _img("1446776811953-b23d57bd21aa",
             "Earth from orbit with blue atmosphere",
             "NASA", "nasa"),
        _img("1516849841032-87cbac4d88f7",
             "Rocket launching with bright exhaust flame at night",
             "SpaceX", "spacex"),
        _img("1454789548928-701522940945",
             "Milky Way galaxy with stars over dark landscape",
             "Greg Rakozy", "grakozy"),
        _img("1614730321146-b6fa6a46bcb4",
             "Nebula and stars in deep space",
             "Jeremy Thomas", "jeremythomasphoto"),
    ],

    # ── 헬스케어 / 웨어러블 ──────────────────────────────────────
    "health": [
        _img("1576091160399-112ba8d25d1d",
             "Medical professional using digital health tablet",
             "National Cancer Institute", "nci"),
        _img("1559757148-5c350d0d3c56",
             "DNA strand and biotechnology research visualization",
             "Warren Umoh", "warrenumoh"),
        _img("1576671081837-49000212a223",
             "Smart wearable health monitoring device on wrist",
             "Luke Chesser", "lukechesser"),
        _img("1505751172876-fa1923c5c528",
             "Doctor reviewing digital patient data on screen",
             "Online Marketing", "impulsq"),
    ],

    # ── 전기차 / EV ───────────────────────────────────────────────
    "ev": [
        _img("1593941707882-a5bba14938c7",
             "Electric vehicle charging port glowing blue",
             "dcbel", "dcbel"),
        _img("1558618666-fcd25c85cd64",
             "Red Tesla Model S on mountain road",
             "Charlie Deets", "charliedeets"),
        _img("1617788138017-80ad40651399",
             "EV charging station with multiple connectors",
             "Juice Flair", "juiceflair"),
        _img("1603584173870-7f23fdae1b7a",
             "Modern electric vehicle interior dashboard at night",
             "Jp Valery", "jpvalery"),
    ],

    # ── 무역 / 글로벌 경제 ───────────────────────────────────────
    "economy": [
        _img("1553729459-efe14ef6055d",
             "Container cargo ship at ocean port",
             "Channey", "channey"),
        _img("1486406146926-c627a92ad1ab",
             "Glass skyscrapers of financial district",
             "Sean Pollock", "seanpollock"),
        _img("1454165804606-c3d57bc86b40",
             "Business professionals in meeting room",
             "Cytonn Photography", "cytonn_photography"),
        _img("1494412574643-ff11b0a5c1c3",
             "Aerial view of cargo containers at port terminal",
             "Tom Fisk", "tomfisk"),
    ],
}

# ── 기본 풀 (카테고리 미매칭 시) ────────────────────────────────
DEFAULT_IMAGE_POOL = [
    _img("1504711434969-e33886168f5c",
         "Aerial view of city lights at night in blue tones",
         "Maximalfocus", "maximalfocus"),
    _img("1451187580459-43490279c0fa",
         "Planet Earth seen from space with city lights",
         "NASA", "nasa"),
    _img("1498050108023-c5249f4df085",
         "Laptop with code on screen in dark environment",
         "Christopher Gower", "cgower"),
    _img("1522071820081-009f0129c71c",
         "Team working on laptops in modern office",
         "Annie Spratt", "anniespratt"),
]
```

---

### 6-4. 날짜 결정론적 선택 알고리즘

```python
import hashlib

def select_from_pool(pool: list, date_str: str) -> dict:
    """같은 날짜는 항상 같은 이미지를 반환. 날짜마다 다른 이미지 선택."""
    digest = hashlib.md5(date_str.encode("utf-8")).hexdigest()
    index  = int(digest, 16) % len(pool)
    return pool[index]
```

**설계 의도**:
- `md5(date_str)` → 동일 날짜면 항상 동일 인덱스 → **재빌드 시 이미지 변경 없음**
- 날짜마다 다른 인덱스 → 아카이브 목록에서 다채로운 이미지 표시
- GitHub Actions 빌드 환경에 외부 의존성 없음

---

### 6-5. `briefings.json` 스키마 추가 필드 (v3 확정)

```json
{
  "hero_url":         "https://images.unsplash.com/photo-{ID}?w=1200&q=80&fit=crop&auto=format",
  "hero_url_small":   "https://images.unsplash.com/photo-{ID}?w=640&q=80&fit=crop&auto=format",
  "hero_alt":         "이미지 설명 (영문)",
  "hero_credit_name": "Photographer Name",
  "hero_credit_url":  "https://unsplash.com/photos/{ID}",
  "hero_source":      "article_image | handpick_category | handpick_default | css_gradient"
}
```

`hero_source` 값 변경 (v2 → v3):

| v2 값 | v3 값 | 설명 |
|---|---|---|
| `unsplash_keyword` | `handpick_category` | 카테고리 핸드픽 맵에서 선택 |
| `unsplash_date_fallback` | `handpick_default` | 기본 풀에서 선택 |
| `article_image` | `article_image` | 변경 없음 |
| `css_gradient` | `css_gradient` | 변경 없음 |

---

## 7. 포스트 프로세서 (`scripts/post_process.py`) 최종 명세 (v3)

기사 `archive/*.html` 파일에 자동 삽입되는 코드 구조.

### 7-1. 삽입 순서

포스트 프로세서가 기사 HTML을 변환할 때 삽입하는 요소와 순서:

```
<head>
  [기존 <style> 보존]
  ↓ 주입: <link rel="stylesheet" href="../theme-modern.css">
</head>
<body class="reader-mode">   ← body에 reader-mode 클래스 추가
  ↓ 주입 1: <nav class="reader-nav">...</nav>
  ↓ 주입 2: <div class="reader-hero ...">...</div>
  [기존 기사 콘텐츠 100% 보존]
  ↓ 주입 3: <footer class="reader-footer">...</footer>
</body>
```

### 7-2. `resolve_hero()` 완전 구현 코드 (v3)

**v2 대비 핵심 변경**: Unsplash API 호출 제거 → CATEGORY_IMAGE_MAP 조회로 교체

```python
import re
import hashlib
from bs4 import BeautifulSoup
from pathlib import Path

# §6-3의 상수 선언 (CATEGORY_PATTERNS, CATEGORY_IMAGE_MAP, DEFAULT_IMAGE_POOL)
# ... (§6-3 코드 그대로 배치)

def select_from_pool(pool: list, date_str: str) -> dict:
    """날짜 해시 기반 결정론적 선택 (§6-4 알고리즘)."""
    index = int(hashlib.md5(date_str.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[index]

def find_article_image(soup: BeautifulSoup) -> dict | None:
    """Priority 1: 기사 본문 내 이미지 탐색 및 히어로 승격."""
    BLOCKED = re.compile(r'icon|logo|badge|emoji|bullet|arrow|avatar', re.I)
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src or BLOCKED.search(src):
            continue
        w = img.get("width")
        h = img.get("height")
        if w and int(w) <= 200:
            continue
        if h and int(h) <= 100:
            continue
        img["data-promoted"] = "hero"
        return {
            "url":         src,
            "url_small":   src,
            "alt":         img.get("alt", ""),
            "credit_name": "",
            "credit_url":  "",
            "source":      "article_image",
        }
    return None

def detect_category(title: str, summary: str) -> str | None:
    """Priority 2: 제목+요약 텍스트에서 카테고리 탐지."""
    text = title + " " + summary
    for category_key, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return category_key
    return None

def resolve_hero(soup: BeautifulSoup, meta: dict) -> tuple[str, dict | None]:
    """
    히어로 이미지 결정. (html_snippet, image_meta) 반환.
    image_meta는 briefings.json 저장용. html_snippet은 주입용.
    """
    date_str = meta.get("date", "2026-01-01")
    title    = meta.get("title", "")
    summary  = meta.get("summary", "")

    # ── Priority 1: 기사 본문 이미지 ─────────────────────────────
    article_img = find_article_image(soup)
    if article_img:
        article_img["source"] = "article_image"
        return build_hero_html(article_img, date_str), article_img

    # ── Priority 2: 카테고리 핸드픽 맵 ──────────────────────────
    category = detect_category(title, summary)
    if category and category in CATEGORY_IMAGE_MAP:
        img_meta = select_from_pool(CATEGORY_IMAGE_MAP[category], date_str)
        img_meta = {**img_meta, "source": "handpick_category"}
        return build_hero_html(img_meta, date_str), img_meta

    # ── Priority 3: 기본 풀 ──────────────────────────────────────
    img_meta = select_from_pool(DEFAULT_IMAGE_POOL, date_str)
    img_meta = {**img_meta, "source": "handpick_default"}
    return build_hero_html(img_meta, date_str), img_meta

    # ── Priority 4: CSS 그라데이션 폴백 (도달 불가 — 기본 풀이 항상 존재)
    # return f'<div class="reader-hero no-image" data-article-date="{date_str}"></div>', None

def build_hero_html(img: dict, date_str: str) -> str:
    """히어로 이미지 div HTML 생성."""
    credit_html = ""
    if img.get("credit_name") and img.get("credit_url"):
        credit_html = (
            f'<a class="reader-hero-credit" href="{img["credit_url"]}" '
            f'target="_blank" rel="noopener">'
            f'Photo by {img["credit_name"]} / Unsplash</a>'
        )
    return f"""<div class="reader-hero has-image" data-article-date="{date_str}">
  <picture>
    <source media="(max-width: 640px)" srcset="{img['url_small']}">
    <img class="reader-hero-img" src="{img['url']}" alt="{img['alt']}"
         loading="lazy" decoding="async">
  </picture>
  <div class="reader-hero-overlay"></div>
  {credit_html}
</div>"""
```

### 7-3. `process_article()` 메인 함수

```python
GNB_HTML = """<nav class="reader-nav">
  <div class="reader-nav-inner">
    <a href="../index.html" class="reader-nav-logo">JFNB</a>
    <div class="reader-nav-links">
      <a href="../index.html">홈</a>
      <a href="../archive.html">아카이브</a>
      <a href="../about.html">소개</a>
    </div>
  </div>
</nav>"""

FOOTER_HTML = """<footer class="reader-footer">
  <a href="../archive.html">← 아카이브로 돌아가기</a>
</footer>"""

def process_article(html_path: Path, meta: dict) -> dict:
    """
    단일 기사 HTML 파일 변환.
    반환: briefings.json에 병합할 hero 메타데이터 dict.
    """
    soup = BeautifulSoup(html_path.read_text("utf-8"), "html.parser")

    # 1. <head>에 theme-modern.css 링크 주입
    head = soup.find("head")
    link = soup.new_tag("link", rel="stylesheet", href="../theme-modern.css")
    head.append(link)

    # 2. <body>에 reader-mode 클래스 추가
    body = soup.find("body")
    existing = body.get("class", [])
    body["class"] = existing + ["reader-mode"]

    # 3. 히어로 이미지 결정
    hero_html, img_meta = resolve_hero(soup, meta)

    # 4. GNB + 히어로를 <body> 최상단에 삽입
    body.insert(0, BeautifulSoup(hero_html, "html.parser"))
    body.insert(0, BeautifulSoup(GNB_HTML, "html.parser"))

    # 5. 리더 푸터를 </body> 직전에 삽입
    body.append(BeautifulSoup(FOOTER_HTML, "html.parser"))

    # 6. 저장
    html_path.write_text(str(soup), "utf-8")

    # 7. briefings.json 갱신용 메타 반환
    if img_meta:
        return {
            "hero_url":         img_meta.get("url", ""),
            "hero_url_small":   img_meta.get("url_small", ""),
            "hero_alt":         img_meta.get("alt", ""),
            "hero_credit_name": img_meta.get("credit_name", ""),
            "hero_credit_url":  img_meta.get("credit_url", ""),
            "hero_source":      img_meta.get("source", "css_gradient"),
        }
    return {"hero_source": "css_gradient"}
```

### 7-4. 진입점 (메인 루프)

```python
import json

ARCHIVE_DIR    = Path("briefing/archive")
BRIEFINGS_JSON = Path("briefing/briefings.json")

def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    for briefing in data.get("briefings", []):
        date = briefing.get("date", "")
        html_path = ARCHIVE_DIR / f"{date}.html"
        if not html_path.exists():
            continue

        hero_meta = process_article(html_path, briefing)
        briefing.update(hero_meta)
        print(f"[OK] {date} → source={hero_meta.get('hero_source')}")

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print(f"[DONE] briefings.json updated.")

if __name__ == "__main__":
    main()
```

---

## 8. 코덱스 구현 체크리스트 (v3 최종)

### Phase 1: PWA 제거 (최우선)

- [ ] `briefing/manifest.json` 삭제
- [ ] `briefing/sw.js` 삭제
- [ ] `index.html` — [A][B][C][D] 4개 블록 제거 (§1-2 참조)
- [ ] `archive.html` — [A][B][C][D] 4개 블록 제거
- [ ] `about.html` — [A][B][C][D] 4개 블록 제거
- [ ] `search.html` — [A][B][C][D] 4개 블록 제거

### Phase 2: SW 클린업 스크립트 삽입

- [ ] `index.html` `<head>` 내 SW Unregister + Cache Delete 스크립트 삽입 (§2-2)
- [ ] `archive.html` 동일 삽입
- [ ] `about.html` 동일 삽입
- [ ] `search.html` 동일 삽입

### Phase 3: Shell-page 클래스 적용

- [ ] `index.html` → `<body class="shell-page">`
- [ ] `archive.html` → `<body class="shell-page archive-page">`
- [ ] `about.html` → `<body class="shell-page">`
- [ ] `search.html` → `<body class="shell-page">`

### Phase 4: 테마 적용 확인

- [ ] `theme-modern.css` 범용 선택자 없음 검증
- [ ] `index.html`에서 `theme-modern.css` `<link>` 태그 존재 확인
- [ ] GNB 글래스모피즘이 4개 페이지에서 시각적으로 표시됨

### Phase 5: 포스트 프로세서 구현 (v3 — API 키 불필요)

- [ ] `briefing/scripts/post_process.py` 신규 작성 (§6-3 상수 + §7 전체 코드)
- [ ] ~~GitHub Actions Secret `UNSPLASH_ACCESS_KEY`~~ **불필요 — 제거됨**
- [ ] `pip install beautifulsoup4` 의존성 확인 (requirements.txt 또는 Actions workflow에 추가)
- [ ] 로컬 테스트: `python briefing/scripts/post_process.py` 실행
- [ ] `archive/2026-05-27.html` 변환 결과 브라우저 확인
- [ ] `briefings.json` 내 `hero_source` 필드 값 확인 (`handpick_category` 또는 `handpick_default`)
- [ ] 8개 카테고리 날짜별 이미지 변화 확인 (예: 2026-05-01, 05-10, 05-20 각기 다른 이미지)

---

## 9. 검수 기준 (완료 조건)

### PWA 제거 검증

```bash
# manifest.json, sw.js 삭제 확인
ls briefing/manifest.json   # → No such file
ls briefing/sw.js           # → No such file

# 4대 HTML에서 PWA 잔재 없음 확인
grep -rn "serviceWorker.register\|manifest.json\|pwa-install-banner\|pwaInstallBanner" \
  briefing/index.html briefing/archive.html briefing/about.html briefing/search.html
# → 결과 없어야 함

# SW 클린업 스크립트 삽입 확인
grep -n "getRegistrations" briefing/index.html
# → 결과 있어야 함
```

### 스타일 격리 검증

```bash
# theme-modern.css에 범용 선택자 없음
grep -n "^body {" briefing/theme-modern.css         # → 없어야 함
grep -n "^p {" briefing/theme-modern.css            # → 없어야 함
grep -n "^\* {" briefing/theme-modern.css           # → 없어야 함
```

### 포스트 프로세서 검증 (v3 신규)

```bash
# 스크립트 존재 확인
ls briefing/scripts/post_process.py                 # → 존재해야 함

# API 키 의존성 없음 확인
grep -n "UNSPLASH_ACCESS_KEY\|api.unsplash.com" briefing/scripts/post_process.py
# → 결과 없어야 함 (API 호출 코드가 없어야 함)

# 핸드픽 맵 상수 존재 확인
grep -n "CATEGORY_IMAGE_MAP\|DEFAULT_IMAGE_POOL" briefing/scripts/post_process.py
# → 두 상수 모두 있어야 함

# 변환 후 briefings.json에 hero 필드 존재 확인
python -c "
import json
data = json.load(open('briefing/briefings.json', encoding='utf-8'))
b = data['briefings'][0]
assert 'hero_url' in b, 'hero_url missing'
assert 'hero_source' in b, 'hero_source missing'
assert b['hero_source'] in ('article_image','handpick_category','handpick_default','css_gradient')
print('OK:', b['hero_source'], b['hero_url'][:60])
"
```

### 시각적 검증

- [ ] `index.html` 브라우저 열기 → 배경 `#121214`, GNB 글래스모피즘 표시
- [ ] `archive.html` 브라우저 열기 → 타임라인 목록 렌더링
- [ ] `archive/2026-05-27.html` 브라우저 열기 → 기사 본문 레이아웃 깨지지 않음 + GNB 표시 + 히어로 이미지 표시
- [ ] 히어로 이미지 우측 하단에 "Photo by ... / Unsplash" 크레딧 표시
- [ ] 다른 날짜 기사(`archive/2026-05-20.html` 등)는 다른 히어로 이미지 표시 (결정론적 다양성)
- [ ] 브라우저 DevTools → Application → Service Workers → 등록된 SW 없음
- [ ] 브라우저 DevTools → Application → Cache Storage → 비어 있음

---

*v3 설계 완료 (2026-05-28). 이 문서(`CLCO_PRD.md`)를 코덱스(Codex)에게 전달하여 구현을 시작하세요.*

---

# CLCO_PRD.md — 3차 UI 개편 설계 (v3.1)

> **추가 작성**: 클코 (Cl-Co / 설계자)
> **기반**: 안티 (Anti / 기획자) 3차 지시서 `CLCO_HANDOFF.md` v3.0
> **날짜**: 2026-05-30
> **수신**: 코덱스 (Codex / 전문 코더)

---

## A. 실태 조사 결과 (Codex 작업 전 현황)

| 파일 | 항목 | 현재 값 | 목표 값 |
|---|---|---|---|
| `index.html` | Hero 섹션 HTML | `<section class="hero">` 존재 (3차 목표 제거 대상) | **완전 삭제** |
| `index.html` | 커버 이미지 해상도 | `w=800`, `h=450` | **`w=1200`, `h=675`** |
| `index.html` | 로고 텍스트 | `JFNB` ✅ | 유지 |
| `archive.html` | 로고 텍스트 | `Jae's Briefing` ❌ | **`JFNB`** |
| `about.html` | 로고 텍스트 | `Jae's Briefing` ❌ | **`JFNB`** |
| `search.html` | 로고 텍스트 | `Jae's Briefing` ❌ | **`JFNB`** |
| 전체 GNB 링크 | `target="_blank"` | **미존재 ✅** (GNB 네비 링크에는 없음) | 현상 유지, 변경 불필요 |
| `post_process.py` `GNB_HTML` | 로고·링크 | `JFNB`, `target` 없음 ✅ | 현상 유지 |

> **`target="_blank"` 진단**: GNB 네비게이션 링크에는 현재 `target="_blank"`가 **존재하지 않음**.
> 유일하게 `target="_blank"`가 있는 곳은 `index.html`의 `.highlight` 외부 기사 링크이며, 이는 외신 원문을 별도 탭에서 여는 **의도된 정상 동작**이므로 건드리지 않는다.

---

## B. 3차 설계 명세

### B-1. `index.html` — Hero 섹션 완전 제거

#### HTML 삭제 대상 (약 682~685라인)

```html
<!-- 아래 블록 전체 삭제 -->
    <!-- Hero -->
    <section class="hero" style="padding: 3rem 2rem 2rem 2rem;">
        <h1>Essential NEWS</h1>
    </section>
```

#### CSS 삭제 대상 (`<style>` 내부)

아래 규칙들을 **통째로 삭제**한다. 다른 선택자에 영향 없음.

```css
/* 삭제 대상 CSS 블록 1 — 약 128~161라인 */
        .hero {
            padding: 4rem 2rem;
            text-align: center;
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        }

        .hero h1 {
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 1rem;
            background: var(--gradient-fire);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .hero p {
            font-size: 1.2rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 2rem;
        }

        .hero-stats {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 2rem;
        }

        .stat {
            text-align: center;
        }
```

```css
/* 삭제 대상 CSS 블록 2 — @media (max-width: 1024px) 내부 두 줄 */
            .hero h1 { font-size: 2.5rem; }
            .hero-stats { flex-wrap: wrap; gap: 2rem; }
```

```css
/* 삭제 대상 CSS 블록 3 — @media (max-width: 768px) 내부 한 줄 */
            .hero { padding: 3rem 1.5rem; }
```

#### `.latest` 상단 여백 조정

Hero 제거 후 GNB와 최신 브리핑 카드 사이 여백을 적절히 확보한다.
기존 `.latest` 규칙을 아래와 같이 교체:

```css
/* 교체 전 */
        .latest {
            max-width: 1400px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }

/* 교체 후 */
        .latest {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2.5rem 2rem 3rem;
        }
```

---

### B-2. `index.html` — 최신 브리핑 커버 이미지 해상도 업그레이드 + Hero 비주얼 강화

#### `renderLatest()` 함수 내 커버 이미지 URL 교체 (약 832라인)

```javascript
// 교체 전
                <img src="${briefing.thumb_url.replace('w=480','w=800').replace('h=270','h=450')}"

// 교체 후
                <img src="${briefing.thumb_url.replace('w=480','w=1200').replace('h=270','h=675')}"
```

> 16:9 비율(1200×675)로 변경하여 풀와이드 Hero 비주얼 완성.

#### `.latest-card:hover` 보더 라이팅 강화 (기존 CSS 교체)

```css
/* 교체 전 */
        .latest-card:hover {
            border-color: var(--accent-red);
            transform: translateY(-4px);
            box-shadow: 0 20px 60px rgba(255, 59, 59, 0.15);
        }

/* 교체 후 */
        .latest-card:hover {
            border-color: var(--accent-red);
            transform: translateY(-6px);
            box-shadow:
                0 0 0 1px rgba(255, 59, 59, 0.25),
                0 24px 80px rgba(255, 59, 59, 0.22),
                0 8px 32px rgba(255, 140, 66, 0.12);
        }
```

---

### B-3. GNB 로고 텍스트 `JFNB` 일괄 통일

`archive.html`, `about.html`, `search.html` 각각에서 아래 1줄 교체:

```html
<!-- 교체 전 (3개 파일 동일) -->
                <span class="nav-logo-text">Jae's Briefing</span>

<!-- 교체 후 (3개 파일 동일) -->
                <span class="nav-logo-text">JFNB</span>
```

---

### B-4. GNB `target="_blank"` 현황 확정 (조치 없음)

```bash
# 검증 명령어 — 실행 후 GNB 링크에 target 없음 확인
grep -n 'target="_blank"' briefing/index.html briefing/archive.html briefing/about.html briefing/search.html briefing/scripts/post_process.py
```

> 예상 결과: `index.html`의 `.highlight` 기사 링크(외신 원문)에만 출력됨.
> GNB 네비게이션 `<a>` 태그에는 해당 속성 없음 → **조치 불필요**.

---

## C. 코덱스 구현 체크리스트 (v3.1)

### Phase 1 — `index.html` Hero 완전 제거
- [ ] HTML: `<section class="hero">...</section>` 블록 삭제
- [ ] CSS: `.hero {}`, `.hero h1 {}`, `.hero p {}`, `.hero-stats {}`, `.stat {}` 5개 블록 삭제
- [ ] CSS 반응형: `@media` 내 `.hero` 관련 3개 규칙 삭제
- [ ] CSS: `.latest {}` padding `3rem 2rem` → `2.5rem 2rem 3rem` 교체

### Phase 2 — `index.html` 최신 브리핑 Hero 비주얼 강화
- [ ] JS: `renderLatest()` 커버 이미지 `w=800`, `h=450` → `w=1200`, `h=675` 교체
- [ ] CSS: `.latest-card:hover` 보더 라이팅 강화 규칙으로 교체

### Phase 3 — 로고 텍스트 일괄 통일
- [ ] `archive.html`: `Jae's Briefing` → `JFNB`
- [ ] `about.html`: `Jae's Briefing` → `JFNB`
- [ ] `search.html`: `Jae's Briefing` → `JFNB`

### Phase 4 — GNB target 전수조사 확인
- [ ] `grep -n 'target="_blank"'` 실행 → GNB 링크에 해당 없음 확인
- [ ] `post_process.py` GNB_HTML 동일 확인

---

## D. 검수 기준

### 시각적 검증
- [ ] `index.html` 로드 시 `Essential NEWS` 섹션 미표시
- [ ] GNB 바로 아래 최신 브리핑 카드가 즉시 등장 (여백 자연스러움)
- [ ] 최신 브리핑 커버 이미지가 기존보다 고화질·와이드 비율로 표시
- [ ] 카드 호버 시 붉은 보더 글로우 효과 선명하게 발생
- [ ] `archive.html`, `about.html`, `search.html` 좌상단 로고 `JFNB` 표시
- [ ] 모든 GNB 내비 링크 클릭 시 동일 탭 전환 (새 탭 없음)
- [ ] 모바일 375px 뷰포트 정상 레이아웃

### 코드 검증
```bash
grep -n "Essential NEWS\|hero-stats\|class=\"hero\"" briefing/index.html  # → 결과 없어야 함
grep -n "Jae's Briefing" briefing/archive.html briefing/about.html briefing/search.html  # → 결과 없어야 함
grep -n "w=800\|h=450" briefing/index.html  # → renderLatest 커버에 없어야 함
```

---

*v3.1 설계 추가 완료 (2026-05-30). Phase 1 → 4 순서로 구현 후 검수 기준으로 자가 검증하세요.*
