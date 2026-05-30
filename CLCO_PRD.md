# CLCO_PRD.md v3 ??PWA ?쒓굅 + 由щ뱶??댁쫰 由щ뜑 ?뚮쭏 + ?몃뱶???대?吏 留?理쒖쥌 ?ㅺ퀎 紐낆꽭??

> **?묒꽦**: ?댁퐫 (Cl-Co / ?ㅺ퀎??
> **湲곕컲**: ?덊떚 (Anti / 怨꾪쉷?? 2李?吏?쒖꽌 v2.0 + ?좎? ?쇰뱶諛?v3 (API ???녿뒗 ?몃뱶???대?吏 留?
> **?좎쭨**: 2026-05-28
> **?섏떊**: 肄붾뜳??(Codex / ?꾨Ц 肄붾뜑)

---

## 0. ?꾪솴 ?뚯븙 (As-Is v2)

### ?뚯씪 ?몃━ ?꾩옱 ?곹깭

```
briefing/
?쒋?? index.html        ??PWA 肄붾뱶 ?꾩껜 ?ы븿 (硫뷀? ?쒓렇, CSS, HTML 諛곕꼫, JS ?깅줉)
?쒋?? archive.html      ??PWA 肄붾뱶 ?꾩껜 ?ы븿
?쒋?? about.html        ??PWA 肄붾뱶 ?꾩껜 ?ы븿
?쒋?? search.html       ??PWA 肄붾뱶 ?꾩껜 ?ы븿
?쒋?? manifest.json     ??[DELETE ???
?쒋?? sw.js             ??[DELETE ???
?쒋?? theme-modern.css  ??[DONE] 肄붾뜳??1李?援ы쁽 ?꾨즺, 援ъ“ ?좏슚
?쒋?? icons/            ???꾩씠肄??뚯씪 ?대뜑 (??젣 遺덊븘??
?붴?? archive/          ??湲곗궗 HTML ?뚯씪??
```

### 肄붾뜳??1李?援ы쁽 ?곹깭 ?먭?

`theme-modern.css` 寃??寃곌낵:
- CSS 蹂??`:root`), `body.shell-page`, `body.reader-mode` ?ㅼ엫?ㅽ럹?댁뒪 寃⑸━ 援ъ“ **?뺤긽**
- GNB 湲?섏뒪紐⑦뵾利? ?덉뼱濡??대?吏, ??꾨씪??由ъ뒪?? 由щ뜑 ?명꽣 CSS **?뺤긽**
- 踰붿슜 ?좏깮??`body {}`, `p {}`, `.container {}` ?? 誘몄궗??**?뺤씤**
- **異붽? ?꾩슂**: ?놁쓬 (援ъ“ ?꾩쟾?섎굹, 4? HTML??`body.shell-page` ?대옒???꾩쭅 誘몄쟻??

---

## 1. PWA ?꾩쟾 ?쒓굅 紐낆꽭

### 1-1. ??젣 ????뚯씪

肄붾뜳?ㅻ뒗 ?꾨옒 ???뚯씪????μ냼?먯꽌 **?꾩쟾????젣**?쒕떎.

| ?뚯씪 | ?≪뀡 | 鍮꾧퀬 |
|---|---|---|
| `briefing/manifest.json` | **DELETE** | PWA ??留ㅻ땲?섏뒪??|
| `briefing/sw.js` | **DELETE** | ?쒕퉬???뚯빱 ?ㅽ겕由쏀듃 |

> `briefing/icons/` ?대뜑????젣?섏? ?딅뒗?? (?뚮퉬肄??꾩씠肄섏쑝濡??ы솢??媛??

---

### 1-2. 4? HTML 怨듯넻 ?쒓굅 釉붾줉 ?뺤쓽

?꾨옒 4媛??뚯씪?먯꽌 ?숈씪???⑦꽩??肄붾뱶瑜??쒓굅?쒕떎:
- `index.html`
- `archive.html`
- `about.html`
- `search.html`

#### [A] `<head>` ??PWA 硫뷀? ?쒓렇 釉붾줉 ?쒓굅

?꾨옒 7以??꾩껜瑜???젣?쒕떎. (?뚯씪留덈떎 ?댁슜 ?숈씪)

```html
<!-- ?쒓굅 ???- HEAD ??PWA 硫뷀? ?쒓렇 釉붾줉 -->
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

**?좎? ???* (?뚮퉬肄섏? PWA ?꾩슜???꾨땲誘濡?蹂댁〈):
```html
<!-- ?좎? - ?쇰컲 ?뚮퉬肄?-->
<link rel="icon" type="image/png" sizes="32x32" href="icons/icon-96x96.png">
<link rel="icon" type="image/png" sizes="16x16" href="icons/icon-72x72.png">
```

#### [B] `<style>` ??PWA CSS 釉붾줉 ?쒓굅

媛??뚯씪??`<style>` ?쒓렇 ?댁뿉???꾨옒 ?뱀뀡 ?꾩껜瑜???젣?쒕떎.
?쒖옉 二쇱꽍(`/* PWA Install Banner */`)遺????誘몃뵒??荑쇰━源뚯?瑜?李얠븘 ?쒓굅?쒕떎.

```css
/* ?쒓굅 ???CSS 釉붾줉 - ?쒖옉 ~ ??*/
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

#### [C] `<body>` ??PWA HTML 諛곕꼫 ?쒓굅

?꾨옒 ??HTML 釉붾줉????젣?쒕떎.

```html
<!-- ?쒓굅 ???HTML 釉붾줉 1 -->
<!-- PWA Install Banner -->
<div class="pwa-install-banner" id="pwaInstallBanner">
    ... (?꾩껜 ?댁슜)
</div>

<!-- ?쒓굅 ???HTML 釉붾줉 2 -->
<!-- PWA Update Toast -->
<div class="pwa-update-toast" id="pwaUpdateToast">
    ... (?꾩껜 ?댁슜)
</div>
```

#### [D] `<script>` PWA ?깅줉 釉붾줉 ?쒓굅

`<!-- PWA Registration -->` 二쇱꽍怨??대떦 `<script>` ?쒓렇 ?꾩껜瑜???젣?쒕떎.

```html
<!-- ?쒓굅 ????ㅽ겕由쏀듃 釉붾줉 ?꾩껜 -->
<!-- PWA Registration -->
<script>
    // Service Worker Registration
    let deferredPrompt = null;
    let swRegistration = null;

    if ('serviceWorker' in navigator) {
        window.addEventListener('load', async () => {
            ... (?꾩껜 ?댁슜)
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

### 1-3. ?뚯씪蹂?PWA 肄붾뱶 ?꾩튂 李몄“??

肄붾뜳?ㅺ? 媛??뚯씪?먯꽌 ?쒓굅???뺥솗??肄붾뱶 ?꾩튂.

#### `index.html`

| ?쒓굅 ??ぉ | ?꾩튂 (李몄“???쇱씤) | 鍮꾧퀬 |
|---|---|---|
| [A] PWA 硫뷀? ?쒓렇 | `<head>` ?? `<!-- PWA Meta Tags -->` ~ `<link rel="apple-touch-icon">` | 10以?|
| [B] PWA CSS | `<style>` ?? `/* PWA Install Banner */` ~ 留덉?留?`@media (max-width: 480px)` 釉붾줉 | ~120以?|
| [C] 諛곕꼫 HTML | `<body>` ?꾨컲遺, `<!-- PWA Install Banner -->` div + `<!-- PWA Update Toast -->` div | ~35以?|
| [D] ?깅줉 ?ㅽ겕由쏀듃 | `<!-- PWA Registration -->` `<script>` 釉붾줉 ?꾩껜 | ~72以?|

#### `archive.html`

| ?쒓굅 ??ぉ | ?꾩튂 (李몄“???쇱씤) | 鍮꾧퀬 |
|---|---|---|
| [A] PWA 硫뷀? ?쒓렇 | `<head>` ?? `<!-- PWA Meta Tags -->` ~ `<link rel="apple-touch-icon">` | 10以?|
| [B] PWA CSS | `<style>` ?? `/* PWA Install Banner */` ~ 留덉?留?`@media` 釉붾줉 | ~120以?|
| [C] 諛곕꼫 HTML | `<body>` ?꾨컲遺 | ~25以?|
| [D] ?깅줉 ?ㅽ겕由쏀듃 | `<!-- PWA Registration -->` `<script>` 釉붾줉 ?꾩껜 | ~72以?|

#### `about.html`

| ?쒓굅 ??ぉ | ?꾩튂 (李몄“???쇱씤) | 鍮꾧퀬 |
|---|---|---|
| [A] PWA 硫뷀? ?쒓렇 | `<head>` ??| 10以?|
| [B] PWA CSS | `<style>` ??`/* PWA Install Banner */` ~ ??| ~120以?|
| [C] 諛곕꼫 HTML | `<body>` ?꾨컲遺 | ~25以?|
| [D] ?깅줉 ?ㅽ겕由쏀듃 | `<!-- PWA Registration -->` `<script>` 釉붾줉 | ~72以?|

#### `search.html`

| ?쒓굅 ??ぉ | ?꾩튂 (李몄“???쇱씤) | 鍮꾧퀬 |
|---|---|---|
| [A] PWA 硫뷀? ?쒓렇 | `<head>` ??| 10以?|
| [B] PWA CSS | `<style>` ??`/* PWA Install Banner */` ~ ??| ~120以?|
| [C] 諛곕꼫 HTML | `<body>` ?꾨컲遺 | ~25以?|
| [D] ?깅줉 ?ㅽ겕由쏀듃 | `<!-- PWA Registration -->` `<script>` 釉붾줉 | ~72以?|

---

## 2. ?쒕퉬???뚯빱 媛뺤젣 ?댁젣 (SW Unregister) ?대┛???ㅽ겕由쏀듃

### 2-1. 紐⑹쟻

`sw.js`? `manifest.json`????젣?섎뜑?쇰룄, ?대? ?대떦 ?ъ씠?몄뿉 諛⑸Ц??湲곗〈 ?ъ슜?먯쓽 釉뚮씪?곗??먮뒗 ?쒕퉬???뚯빱媛 **?깅줉???곹깭濡??⑥븘 ?덈떎.** ??寃쎌슦:

- ?쒕퉬???뚯빱媛 援щ쾭??罹먯떆瑜?怨꾩냽 ?쒕튃 ??理쒖떊 HTML/CSS媛 諛섏쁺?섏? ?딆쓬
- `sw.js` ?뚯씪????젣?섏뿀?쇰?濡??뚯빱媛 ?ㅼ쓬 ?낅뜲?댄듃瑜?諛쏆쓣 ???놁쓬 ??臾닿린??援щ쾭??罹먯떆 ?곹깭 吏??

?대? ?닿껐?섍린 ?꾪빐 4? HTML ?뚯씪??**?대┛???ㅽ겕由쏀듃**瑜??쎌엯?쒕떎.

### 2-2. ?대┛???ㅽ겕由쏀듃 肄붾뱶

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

> **湲곗〈 吏?쒖꽌 ?ㅽ겕由쏀듃 ?鍮?異붽??ы빆**: `caches.keys().then(...)` 釉붾줉??異붽??섏뿬 ?쒕퉬???뚯빱媛 ?④릿 罹먯떆 ?ㅽ넗由ъ?源뚯? ?④퍡 ??젣?쒕떎. ?쒕퉬???뚯빱 ?댁젣留뚯쑝濡쒕뒗 罹먯떆媛 ?⑥쓣 ???덇린 ?뚮Ц?대떎.

### 2-3. ?쎌엯 ?꾩튂

4媛?HTML ?뚯씪(`index.html`, `archive.html`, `about.html`, `search.html`)??`<head>` ??
**`<title>` ?쒓렇 吏곸쟾**???쎌엯?쒕떎.

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- ?뚮퉬肄?(?좎?) -->
  <link rel="icon" type="image/png" sizes="32x32" href="icons/icon-96x96.png">
  <link rel="icon" type="image/png" sizes="16x16" href="icons/icon-72x72.png">

  <!-- ??SW Cleanup - ?ш린???쎌엯 -->
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

**??`<title>` 吏곸쟾?멸??**
- `<head>` ??媛???대Ⅸ ?꾩튂?먯꽌 鍮꾨룞湲곗쟻?쇰줈 ?ㅽ뻾?섏뼱??罹먯떆 異⑸룎???섏씠吏 ?뚮뜑留??꾩뿉 理쒕????쇱컢 泥섎━?????덈떎.
- ?뚮뜑留곸쓣 釉붾줈?뱁븯吏 ?딅뒗??(Promise 湲곕컲 鍮꾨룞湲?肄붾뱶?대?濡?.

### 2-4. ?ν썑 ?쒓굅 ?쒖젏

???대┛???ㅽ겕由쏀듃??**?곴뎄 肄붾뱶媛 ?꾨땲??** 湲곗〈 諛⑸Ц?먮뱾??釉뚮씪?곗??먯꽌 援??쒕퉬???뚯빱媛 ?꾩쟾??泥?냼???덉긽 湲곌컙(諛고룷 ????4~8二? ?댄썑???쒓굅?대룄 ?쒕떎. ?? ?밸텇媛꾩? ?④꺼?먯뼱??臾댄빐?섎떎(`getRegistrations()`媛 鍮?諛곗뿴??諛섑솚??肉?.

---

## 3. `body` ?대옒???곸슜 (Shell Page ?쒖꽦??

`theme-modern.css`??`body.shell-page` 諛?`body.reader-mode` ?ㅽ??쇱씠 ?ㅼ젣濡??곸슜?섎젮硫?媛?HTML ?뚯씪??`<body>` ?쒓렇???대옒?ㅺ? ?덉뼱???쒕떎.

### 3-1. ???섏씠吏 4媛??뚯씪

| ?뚯씪 | 蹂寃???| 蹂寃???|
|---|---|---|
| `index.html` | `<body>` | `<body class="shell-page">` |
| `archive.html` | `<body>` | `<body class="shell-page archive-page">` |
| `about.html` | `<body>` | `<body class="shell-page">` |
| `search.html` | `<body>` | `<body class="shell-page">` |

### 3-2. 湲곗궗 蹂몃Ц ?섏씠吏 (?ъ뒪???꾨줈?몄꽌 泥섎━)

`archive/*.html` ?뚯씪? ?ъ뒪???꾨줈?몄꽌(`scripts/post_process.py`)媛 ?먮룞?쇰줈 泥섎━?쒕떎.
?섎룞?쇰줈 蹂寃쏀븯吏 ?딅뒗??

---

## 4. ?ㅽ???寃⑸━ ?꾪궎?띿쿂 (Style Isolation ??Clean Room ?ы솗??

### 4-1. 寃⑸━ ?먯튃 ?ы솗??

`theme-modern.css` 寃??寃곌낵 ?щ컮瑜닿쾶 援ы쁽?섏뼱 ?덉쓬???뺤씤?덈떎.
肄붾뜳?ㅻ뒗 ???뚯씪??**?섏젙?섏? ?딅뒗??** 援ъ“ ?붿빟:

```
theme-modern.css
??
?쒋? :root { }                         ??CSS 蹂?섎쭔. ?꾩뿭 ?좏깮???놁쓬.
??
?쒋? body.shell-page .xxx { }          ?????섏씠吏 ?꾩슜 (index/archive/about/search)
??   ?쒋? .nav, .gnb ??GNB ?ㅽ???
??   ?쒋? .timeline-list ????꾨씪??紐⑸줉
??   ?붴? .footer ???명꽣
??
?붴? body.reader-mode .xxx { }         ??湲곗궗 ?섏씠吏 ?꾩슜 (archive/*.html)
     ?쒋? .reader-nav ??誘몃땲硫 GNB
     ?쒋? .reader-hero ???덉뼱濡??대?吏
     ?붴? .reader-footer ??由щ뜑 ?명꽣
```

### 4-2. 湲곗궗 蹂몃Ц HTML 異⑸룎 諛⑹? 洹쒖튃

`archive/YYYY-MM-DD.html` 湲곗궗 ?뚯씪?ㅼ? ?먯껜 `<style>` 釉붾줉?먯꽌 ?꾨옒 ?좏깮?먮? ?ъ슜?쒕떎:

```css
/* 湲곗궗 ?먯껜 ?ㅽ???(?덈? ?섏젙 遺덇?) */
body { font-family: ...; background: ...; }
.container { max-width: 900px; ... }
.article-card { ... }
.section-title { ... }
h2.section-title { ... }
```

`theme-modern.css`??`body.reader-mode` ?묐몢?щ줈 寃⑸━?섏뼱 ?덉쑝誘濡??대뱾怨?異⑸룎?섏? ?딅뒗??
?? `body { background: ...; }` vs `body.reader-mode { background: ...; }` ?먯꽌 ?꾩옄媛 紐낆떆??specificity)媛 ?믪븘 ?밸━?쒕떎. ??寃쎌슦 湲곗궗???먮옒 body 諛곌꼍?됱씠 `theme-modern.css`??`#121214`濡???씠?붾뜲, ??媛믪씠 ?쒓컖?곸쑝濡??좎궗(`#0a0a0f` vs `#121214`)?섎?濡??ㅼ쭏??臾몄젣???녿떎.

---

## 5. Coal Dark ?뚮쭏 + ??댄룷洹몃옒??理쒖쥌 ?ъ뼇 ?뺤씤

湲곗〈 `theme-modern.css`??援ы쁽???ъ뼇 ?뺤씤. 蹂寃??놁쓬.

### 5-1. ?됱긽 ?붾젅??(?뺤젙)

```
諛곌꼍 湲곕낯:      #121214   (Coal Dark ???쒗쓳蹂대떎 諛앷퀬 ?곕쑜??李⑥퐳)
諛곌꼍 ?⑤꼸:      #18181b   (移대뱶, ?ㅻ쾭?덉씠)
諛곌꼍 ?몃쾭:      #26262c
?띿뒪??1李?     #e8e8ea   (?쒕갚 ?꾨땶 ?ㅽ봽?붿씠?????μ떆媛??낆꽌 ?쇰줈 媛먯냼)
?띿뒪??2李?     #9898a6
?띿뒪??3李?     #5c5c70   (?좎쭨, 硫뷀?)
寃쎄퀎??         rgba(255,255,255,0.08)
GNB 諛곌꼍:       rgba(18,18,20,0.80) + backdrop-filter: blur(20px) saturate(160%)
?≪꽱??         #e84040 (?덈뱶), #4a9eff (釉붾（), #f5c842 (怨⑤뱶)
```

### 5-2. ??댄룷洹몃옒???ъ뼇 (?뺤젙)

```
?고듃 ?ㅽ깮 (UI):    Outfit ??Noto Sans KR ??-apple-system ??sans-serif
?고듃 ?ㅽ깮 (紐⑤끂):  JetBrains Mono
?고듃 ?ㅽ깮 (?몃━??: Playfair Display

蹂몃Ц ?낆꽌 ??      max-width: 680px (--reading-width)
??肄섑뀗痢???      max-width: 1200px (--content-width)
以?媛꾧꺽:           1.82 (?쒓?/?곷Ц ?쇱슜 理쒖쟻媛?
?고듃 ?ш린 湲곗?:    16px (釉뚮씪?곗? 湲곕낯媛??좎?)
?쒓? ?먭컙:         Noto Sans KR ?먮룞 (蹂꾨룄 letter-spacing 遺덊븘??
```

---

## 6. ?몃뱶???꾨━誘몄뾼 ?대?吏 留?(API ??遺덊븘????v3 ?좉퇋)

### 6-0. ?ㅺ퀎 諛곌꼍 諛?v2 ?鍮?蹂寃쎌젏

| ??ぉ | v2 (Unsplash API) | v3 (?몃뱶??留? |
|---|---|---|
| API ???꾩슂 | ?꾩슂 (`UNSPLASH_ACCESS_KEY`) | **遺덊븘??* |
| GitHub Actions Secret | ?꾩슂 | **遺덊븘??* |
| ?몄텧 諛⑹떇 | 鍮뚮뱶 ??HTTP ?붿껌 | **Python ?뺤뀛?덈━ 議고쉶 (濡쒖뺄)** |
| ?대?吏 蹂??| 留?鍮뚮뱶 ?щ씪吏??쒕뜡) | **?좎쭨 ?댁떆 湲곕컲 寃곗젙濡좎쟻 ?좏깮** |
| ?μ븷 ?꾪뿕 | API ?ㅼ슫/?좊떦 珥덇낵 ???ㅽ뙣 | **?놁쓬 (?ㅽ봽?쇱씤 ?숈옉)** |
| ?대?吏 ?덉쭏 | 寃??寃곌낵 ?덉쭏 蹂??| **?ъ쟾 ?먮젅?댁뀡??珥덇퀬?붿쭏留?* |

Unsplash CDN URL? API ?몄쬆 ?놁씠 怨듦컻 ?묎렐??媛?ν븯??
URL ?뺤떇: `https://images.unsplash.com/photo-{ID}?w=1200&q=80&fit=crop&auto=format`

---

### 6-1. ?곗꽑?쒖쐞 泥닿퀎 (v3 ?뺤젙)

```
Priority 1: 湲곗궗 HTML ???대?吏 媛먯? ???덉뼱濡쒕줈 ?밴꺽      [蹂寃??놁쓬]
Priority 2: CATEGORY_IMAGE_MAP 議고쉶 ??移댄뀒怨좊━ ?몃뱶???대?吏  [?좉퇋 - API 遺덊븘??
Priority 3: DEFAULT_IMAGE_POOL 議고쉶 ??湲곕낯 ?뚰겕 ?대?吏      [?좉퇋 - API 遺덊븘??
Priority 4: CSS 洹몃씪?곗씠???대갚                           [蹂寃??놁쓬]

[?쒓굅?? Unsplash Search API ?몄텧 (Priority 2, 3)
```

---

### 6-2. 移댄뀒怨좊━ ?먯? ?ㅼ썙???⑦꽩 (Python regex)

```python
CATEGORY_PATTERNS = [
    # (移댄뀒怨좊━ ?? regex ?⑦꽩)
    ("ai",          r'AI|?멸났吏??LLM|ChatGPT|Gemini|Claude|Grok|?λ윭??癒몄떊?щ떇|GPT|?ㅽ뵂AI|OpenAI|Anthropic'),
    ("chip",        r'諛섎룄泥?移?HBM|TSMC|SK?섏씠?됱뒪|?섏씠?됱뒪|留덉씠?щ줎|Micron|NVIDIA|?붾퉬?붿븘|?쇱꽦?꾩옄|?뚯슫?쒕━|?⑥씠??),
    ("finance",     r'二쇱떇|利앹떆|S&P|?섏뒪???쒖킑|IPO|?곸옣|?붽?|?ъ옄|梨꾧텒|湲덈━|?곗?|Fed|二쇨?|肄붿뒪???ㅼ슦'),
    ("robot",       r'濡쒕큸|?대㉧?몄씠??Unitree|蹂댁뒪?대떎?대궡誘뱀뒪|Figure|Agility|?먮룞???쒕줎'),
    ("space",       r'?곗＜|SpaceX|?ㅽ?留곹겕|Starlink|?꾩꽦|濡쒖폆|諛쒖궗|NASA|?ㅽ???Starship|ISS'),
    ("health",      r'?ъ뒪|?섎즺|Fitbit|?⑥뼱?щ툝|嫄닿컯|諛붿씠???꾩긽|FDA|?쒖빟|?ㅻ쭏?몄썙移??좏뵆?뚯튂'),
    ("ev",          r'?꾧린李?EV|諛고꽣由?Tesla|?뚯뒳??由щ퉬??BYD|異⑹쟾|?꾨룞???먯쑉二쇳뻾'),
    ("economy",     r'臾댁뿭|愿???섏텧|?섏엯|寃쎌젣|湲濡쒕쾶|GDP|?명뵆??愿??怨듦툒留??щ윭|?섏쑉'),
]
```

?먯? ?곗꽑?쒖쐞: 由ъ뒪???쒖꽌?濡?泥?踰덉㎏ 留ㅼ묶 移댄뀒怨좊━ ?ъ슜.
湲곗궗 ?쒕ぉ + ?붿빟 ?띿뒪?몃? ?⑹퀜???먯??쒕떎.

---

### 6-3. ?몃뱶???꾨━誘몄뾼 ?대?吏 留?(CATEGORY_IMAGE_MAP)

媛?移댄뀒怨좊━蹂?4?? 湲곕낯 ? 4?? 珥?36???먮젅?댁뀡.
?좏깮 ?뚭퀬由ъ쬁: `index = int(md5(date_str)) % len(pool)` (?좎쭨 寃곗젙濡좎쟻)

```python
# post_process.py ???곷떒 ?곸닔濡??좎뼵
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

    # ?? AI / ?멸났吏???????????????????????????????????????????????
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

    # ?? 諛섎룄泥?/ 移???????????????????????????????????????????????
    "chip": [
        _img("1518770660439-4636190af475",
             "Close-up of blue printed circuit board",
             "Alexandre Debi챔ve", "alexkixa"),
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

    # ?? 二쇱떇 / 湲덉쑖 ??????????????????????????????????????????????
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

    # ?? 濡쒕큸 / ?대㉧?몄씠???????????????????????????????????????????
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

    # ?? ?곗＜ / SpaceX / ?꾩꽦 ?????????????????????????????????????
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

    # ?? ?ъ뒪耳??/ ?⑥뼱?щ툝 ??????????????????????????????????????
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

    # ?? ?꾧린李?/ EV ???????????????????????????????????????????????
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

    # ?? 臾댁뿭 / 湲濡쒕쾶 寃쎌젣 ???????????????????????????????????????
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

# ?? 湲곕낯 ? (移댄뀒怨좊━ 誘몃ℓ移??? ????????????????????????????????
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

### 6-4. ?좎쭨 寃곗젙濡좎쟻 ?좏깮 ?뚭퀬由ъ쬁

```python
import hashlib

def select_from_pool(pool: list, date_str: str) -> dict:
    """媛숈? ?좎쭨????긽 媛숈? ?대?吏瑜?諛섑솚. ?좎쭨留덈떎 ?ㅻⅨ ?대?吏 ?좏깮."""
    digest = hashlib.md5(date_str.encode("utf-8")).hexdigest()
    index  = int(digest, 16) % len(pool)
    return pool[index]
```

**?ㅺ퀎 ?섎룄**:
- `md5(date_str)` ???숈씪 ?좎쭨硫???긽 ?숈씪 ?몃뜳????**?щ퉴?????대?吏 蹂寃??놁쓬**
- ?좎쭨留덈떎 ?ㅻⅨ ?몃뜳?????꾩뭅?대툕 紐⑸줉?먯꽌 ?ㅼ콈濡쒖슫 ?대?吏 ?쒖떆
- GitHub Actions 鍮뚮뱶 ?섍꼍???몃? ?섏〈???놁쓬

---

### 6-5. `briefings.json` ?ㅽ궎留?異붽? ?꾨뱶 (v3 ?뺤젙)

```json
{
  "hero_url":         "https://images.unsplash.com/photo-{ID}?w=1200&q=80&fit=crop&auto=format",
  "hero_url_small":   "https://images.unsplash.com/photo-{ID}?w=640&q=80&fit=crop&auto=format",
  "hero_alt":         "?대?吏 ?ㅻ챸 (?곷Ц)",
  "hero_credit_name": "Photographer Name",
  "hero_credit_url":  "https://unsplash.com/photos/{ID}",
  "hero_source":      "article_image | handpick_category | handpick_default | css_gradient"
}
```

`hero_source` 媛?蹂寃?(v2 ??v3):

| v2 媛?| v3 媛?| ?ㅻ챸 |
|---|---|---|
| `unsplash_keyword` | `handpick_category` | 移댄뀒怨좊━ ?몃뱶??留듭뿉???좏깮 |
| `unsplash_date_fallback` | `handpick_default` | 湲곕낯 ??먯꽌 ?좏깮 |
| `article_image` | `article_image` | 蹂寃??놁쓬 |
| `css_gradient` | `css_gradient` | 蹂寃??놁쓬 |

---

## 7. ?ъ뒪???꾨줈?몄꽌 (`scripts/post_process.py`) 理쒖쥌 紐낆꽭 (v3)

湲곗궗 `archive/*.html` ?뚯씪???먮룞 ?쎌엯?섎뒗 肄붾뱶 援ъ“.

### 7-1. ?쎌엯 ?쒖꽌

?ъ뒪???꾨줈?몄꽌媛 湲곗궗 HTML??蹂?섑븷 ???쎌엯?섎뒗 ?붿냼? ?쒖꽌:

```
<head>
  [湲곗〈 <style> 蹂댁〈]
  ??二쇱엯: <link rel="stylesheet" href="../theme-modern.css">
</head>
<body class="reader-mode">   ??body??reader-mode ?대옒??異붽?
  ??二쇱엯 1: <nav class="reader-nav">...</nav>
  ??二쇱엯 2: <div class="reader-hero ...">...</div>
  [湲곗〈 湲곗궗 肄섑뀗痢?100% 蹂댁〈]
  ??二쇱엯 3: <footer class="reader-footer">...</footer>
</body>
```

### 7-2. `resolve_hero()` ?꾩쟾 援ы쁽 肄붾뱶 (v3)

**v2 ?鍮??듭떖 蹂寃?*: Unsplash API ?몄텧 ?쒓굅 ??CATEGORY_IMAGE_MAP 議고쉶濡?援먯껜

```python
import re
import hashlib
from bs4 import BeautifulSoup
from pathlib import Path

# 짠6-3???곸닔 ?좎뼵 (CATEGORY_PATTERNS, CATEGORY_IMAGE_MAP, DEFAULT_IMAGE_POOL)
# ... (짠6-3 肄붾뱶 洹몃?濡?諛곗튂)

def select_from_pool(pool: list, date_str: str) -> dict:
    """?좎쭨 ?댁떆 湲곕컲 寃곗젙濡좎쟻 ?좏깮 (짠6-4 ?뚭퀬由ъ쬁)."""
    index = int(hashlib.md5(date_str.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[index]

def find_article_image(soup: BeautifulSoup) -> dict | None:
    """Priority 1: 湲곗궗 蹂몃Ц ???대?吏 ?먯깋 諛??덉뼱濡??밴꺽."""
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
    """Priority 2: ?쒕ぉ+?붿빟 ?띿뒪?몄뿉??移댄뀒怨좊━ ?먯?."""
    text = title + " " + summary
    for category_key, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return category_key
    return None

def resolve_hero(soup: BeautifulSoup, meta: dict) -> tuple[str, dict | None]:
    """
    ?덉뼱濡??대?吏 寃곗젙. (html_snippet, image_meta) 諛섑솚.
    image_meta??briefings.json ??μ슜. html_snippet? 二쇱엯??
    """
    date_str = meta.get("date", "2026-01-01")
    title    = meta.get("title", "")
    summary  = meta.get("summary", "")

    # ?? Priority 1: 湲곗궗 蹂몃Ц ?대?吏 ?????????????????????????????
    article_img = find_article_image(soup)
    if article_img:
        article_img["source"] = "article_image"
        return build_hero_html(article_img, date_str), article_img

    # ?? Priority 2: 移댄뀒怨좊━ ?몃뱶??留???????????????????????????
    category = detect_category(title, summary)
    if category and category in CATEGORY_IMAGE_MAP:
        img_meta = select_from_pool(CATEGORY_IMAGE_MAP[category], date_str)
        img_meta = {**img_meta, "source": "handpick_category"}
        return build_hero_html(img_meta, date_str), img_meta

    # ?? Priority 3: 湲곕낯 ? ??????????????????????????????????????
    img_meta = select_from_pool(DEFAULT_IMAGE_POOL, date_str)
    img_meta = {**img_meta, "source": "handpick_default"}
    return build_hero_html(img_meta, date_str), img_meta

    # ?? Priority 4: CSS 洹몃씪?곗씠???대갚 (?꾨떖 遺덇? ??湲곕낯 ?????긽 議댁옱)
    # return f'<div class="reader-hero no-image" data-article-date="{date_str}"></div>', None

def build_hero_html(img: dict, date_str: str) -> str:
    """?덉뼱濡??대?吏 div HTML ?앹꽦."""
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

### 7-3. `process_article()` 硫붿씤 ?⑥닔

```python
GNB_HTML = """<nav class="reader-nav">
  <div class="reader-nav-inner">
    <a href="../index.html" class="reader-nav-logo">JFNB</a>
    <div class="reader-nav-links">
      <a href="../index.html">??/a>
      <a href="../archive.html">?꾩뭅?대툕</a>
      <a href="../about.html">?뚭컻</a>
    </div>
  </div>
</nav>"""

FOOTER_HTML = """<footer class="reader-footer">
  <a href="../archive.html">???꾩뭅?대툕濡??뚯븘媛湲?/a>
</footer>"""

def process_article(html_path: Path, meta: dict) -> dict:
    """
    ?⑥씪 湲곗궗 HTML ?뚯씪 蹂??
    諛섑솚: briefings.json??蹂묓빀??hero 硫뷀??곗씠??dict.
    """
    soup = BeautifulSoup(html_path.read_text("utf-8"), "html.parser")

    # 1. <head>??theme-modern.css 留곹겕 二쇱엯
    head = soup.find("head")
    link = soup.new_tag("link", rel="stylesheet", href="../theme-modern.css")
    head.append(link)

    # 2. <body>??reader-mode ?대옒??異붽?
    body = soup.find("body")
    existing = body.get("class", [])
    body["class"] = existing + ["reader-mode"]

    # 3. ?덉뼱濡??대?吏 寃곗젙
    hero_html, img_meta = resolve_hero(soup, meta)

    # 4. GNB + ?덉뼱濡쒕? <body> 理쒖긽?⑥뿉 ?쎌엯
    body.insert(0, BeautifulSoup(hero_html, "html.parser"))
    body.insert(0, BeautifulSoup(GNB_HTML, "html.parser"))

    # 5. 由щ뜑 ?명꽣瑜?</body> 吏곸쟾???쎌엯
    body.append(BeautifulSoup(FOOTER_HTML, "html.parser"))

    # 6. ???
    html_path.write_text(str(soup), "utf-8")

    # 7. briefings.json 媛깆떊??硫뷀? 諛섑솚
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

### 7-4. 吏꾩엯??(硫붿씤 猷⑦봽)

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
        print(f"[OK] {date} ??source={hero_meta.get('hero_source')}")

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print(f"[DONE] briefings.json updated.")

if __name__ == "__main__":
    main()
```

---

## 8. 肄붾뜳??援ы쁽 泥댄겕由ъ뒪??(v3 理쒖쥌)

### Phase 1: PWA ?쒓굅 (理쒖슦??

- [ ] `briefing/manifest.json` ??젣
- [ ] `briefing/sw.js` ??젣
- [ ] `index.html` ??[A][B][C][D] 4媛?釉붾줉 ?쒓굅 (짠1-2 李몄“)
- [ ] `archive.html` ??[A][B][C][D] 4媛?釉붾줉 ?쒓굅
- [ ] `about.html` ??[A][B][C][D] 4媛?釉붾줉 ?쒓굅
- [ ] `search.html` ??[A][B][C][D] 4媛?釉붾줉 ?쒓굅

### Phase 2: SW ?대┛???ㅽ겕由쏀듃 ?쎌엯

- [ ] `index.html` `<head>` ??SW Unregister + Cache Delete ?ㅽ겕由쏀듃 ?쎌엯 (짠2-2)
- [ ] `archive.html` ?숈씪 ?쎌엯
- [ ] `about.html` ?숈씪 ?쎌엯
- [ ] `search.html` ?숈씪 ?쎌엯

### Phase 3: Shell-page ?대옒???곸슜

- [ ] `index.html` ??`<body class="shell-page">`
- [ ] `archive.html` ??`<body class="shell-page archive-page">`
- [ ] `about.html` ??`<body class="shell-page">`
- [ ] `search.html` ??`<body class="shell-page">`

### Phase 4: ?뚮쭏 ?곸슜 ?뺤씤

- [ ] `theme-modern.css` 踰붿슜 ?좏깮???놁쓬 寃利?
- [ ] `index.html`?먯꽌 `theme-modern.css` `<link>` ?쒓렇 議댁옱 ?뺤씤
- [ ] GNB 湲?섏뒪紐⑦뵾利섏씠 4媛??섏씠吏?먯꽌 ?쒓컖?곸쑝濡??쒖떆??

### Phase 5: ?ъ뒪???꾨줈?몄꽌 援ы쁽 (v3 ??API ??遺덊븘??

- [ ] `briefing/scripts/post_process.py` ?좉퇋 ?묒꽦 (짠6-3 ?곸닔 + 짠7 ?꾩껜 肄붾뱶)
- [ ] ~~GitHub Actions Secret `UNSPLASH_ACCESS_KEY`~~ **遺덊븘?????쒓굅??*
- [ ] `pip install beautifulsoup4` ?섏〈???뺤씤 (requirements.txt ?먮뒗 Actions workflow??異붽?)
- [ ] 濡쒖뺄 ?뚯뒪?? `python briefing/scripts/post_process.py` ?ㅽ뻾
- [ ] `archive/2026-05-27.html` 蹂??寃곌낵 釉뚮씪?곗? ?뺤씤
- [ ] `briefings.json` ??`hero_source` ?꾨뱶 媛??뺤씤 (`handpick_category` ?먮뒗 `handpick_default`)
- [ ] 8媛?移댄뀒怨좊━ ?좎쭨蹂??대?吏 蹂???뺤씤 (?? 2026-05-01, 05-10, 05-20 媛곴린 ?ㅻⅨ ?대?吏)

---

## 9. 寃??湲곗? (?꾨즺 議곌굔)

### PWA ?쒓굅 寃利?

```bash
# manifest.json, sw.js ??젣 ?뺤씤
ls briefing/manifest.json   # ??No such file
ls briefing/sw.js           # ??No such file

# 4? HTML?먯꽌 PWA ?붿옱 ?놁쓬 ?뺤씤
grep -rn "serviceWorker.register\|manifest.json\|pwa-install-banner\|pwaInstallBanner" \
  briefing/index.html briefing/archive.html briefing/about.html briefing/search.html
# ??寃곌낵 ?놁뼱????

# SW ?대┛???ㅽ겕由쏀듃 ?쎌엯 ?뺤씤
grep -n "getRegistrations" briefing/index.html
# ??寃곌낵 ?덉뼱????
```

### ?ㅽ???寃⑸━ 寃利?

```bash
# theme-modern.css??踰붿슜 ?좏깮???놁쓬
grep -n "^body {" briefing/theme-modern.css         # ???놁뼱????
grep -n "^p {" briefing/theme-modern.css            # ???놁뼱????
grep -n "^\* {" briefing/theme-modern.css           # ???놁뼱????
```

### ?ъ뒪???꾨줈?몄꽌 寃利?(v3 ?좉퇋)

```bash
# ?ㅽ겕由쏀듃 議댁옱 ?뺤씤
ls briefing/scripts/post_process.py                 # ??議댁옱?댁빞 ??

# API ???섏〈???놁쓬 ?뺤씤
grep -n "UNSPLASH_ACCESS_KEY\|api.unsplash.com" briefing/scripts/post_process.py
# ??寃곌낵 ?놁뼱????(API ?몄텧 肄붾뱶媛 ?놁뼱????

# ?몃뱶??留??곸닔 議댁옱 ?뺤씤
grep -n "CATEGORY_IMAGE_MAP\|DEFAULT_IMAGE_POOL" briefing/scripts/post_process.py
# ?????곸닔 紐⑤몢 ?덉뼱????

# 蹂????briefings.json??hero ?꾨뱶 議댁옱 ?뺤씤
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

### ?쒓컖??寃利?

- [ ] `index.html` 釉뚮씪?곗? ?닿린 ??諛곌꼍 `#121214`, GNB 湲?섏뒪紐⑦뵾利??쒖떆
- [ ] `archive.html` 釉뚮씪?곗? ?닿린 ????꾨씪??紐⑸줉 ?뚮뜑留?
- [ ] `archive/2026-05-27.html` 釉뚮씪?곗? ?닿린 ??湲곗궗 蹂몃Ц ?덉씠?꾩썐 源⑥?吏 ?딆쓬 + GNB ?쒖떆 + ?덉뼱濡??대?吏 ?쒖떆
- [ ] ?덉뼱濡??대?吏 ?곗륫 ?섎떒??"Photo by ... / Unsplash" ?щ젅???쒖떆
- [ ] ?ㅻⅨ ?좎쭨 湲곗궗(`archive/2026-05-20.html` ?????ㅻⅨ ?덉뼱濡??대?吏 ?쒖떆 (寃곗젙濡좎쟻 ?ㅼ뼇??
- [ ] 釉뚮씪?곗? DevTools ??Application ??Service Workers ???깅줉??SW ?놁쓬
- [ ] 釉뚮씪?곗? DevTools ??Application ??Cache Storage ??鍮꾩뼱 ?덉쓬

---

*v3 ?ㅺ퀎 ?꾨즺 (2026-05-28). ??臾몄꽌(`CLCO_PRD.md`)瑜?肄붾뜳??Codex)?먭쾶 ?꾨떖?섏뿬 援ы쁽???쒖옉?섏꽭??*

---

# CLCO_PRD.md ??3李?UI 媛쒗렪 ?ㅺ퀎 (v3.1)

> **異붽? ?묒꽦**: ?댁퐫 (Cl-Co / ?ㅺ퀎??
> **湲곕컲**: ?덊떚 (Anti / 湲고쉷?? 3李?吏?쒖꽌 `CLCO_HANDOFF.md` v3.0
> **?좎쭨**: 2026-05-30
> **?섏떊**: 肄붾뜳??(Codex / ?꾨Ц 肄붾뜑)

---

## A. ?ㅽ깭 議곗궗 寃곌낵 (Codex ?묒뾽 ???꾪솴)

| ?뚯씪 | ??ぉ | ?꾩옱 媛?| 紐⑺몴 媛?|
|---|---|---|---|
| `index.html` | Hero ?뱀뀡 HTML | `<section class="hero">` 議댁옱 (3李?紐⑺몴 ?쒓굅 ??? | **?꾩쟾 ??젣** |
| `index.html` | 而ㅻ쾭 ?대?吏 ?댁긽??| `w=800`, `h=450` | **`w=1200`, `h=675`** |
| `index.html` | 濡쒓퀬 ?띿뒪??| `JFNB` ??| ?좎? |
| `archive.html` | 濡쒓퀬 ?띿뒪??| `Jae's Briefing` ??| **`JFNB`** |
| `about.html` | 濡쒓퀬 ?띿뒪??| `Jae's Briefing` ??| **`JFNB`** |
| `search.html` | 濡쒓퀬 ?띿뒪??| `Jae's Briefing` ??| **`JFNB`** |
| ?꾩껜 GNB 留곹겕 | `target="_blank"` | **誘몄〈????* (GNB ?ㅻ퉬 留곹겕?먮뒗 ?놁쓬) | ?꾩긽 ?좎?, 蹂寃?遺덊븘??|
| `post_process.py` `GNB_HTML` | 濡쒓퀬쨌留곹겕 | `JFNB`, `target` ?놁쓬 ??| ?꾩긽 ?좎? |

> **`target="_blank"` 吏꾨떒**: GNB ?ㅻ퉬寃뚯씠??留곹겕?먮뒗 ?꾩옱 `target="_blank"`媛 **議댁옱?섏? ?딆쓬**.
> ?좎씪?섍쾶 `target="_blank"`媛 ?덈뒗 怨녹? `index.html`??`.highlight` ?몃? 湲곗궗 留곹겕?대ŉ, ?대뒗 ?몄떊 ?먮Ц??蹂꾨룄 ??뿉???щ뒗 **?섎룄???뺤긽 ?숈옉**?대?濡?嫄대뱶由ъ? ?딅뒗??

---

## B. 3李??ㅺ퀎 紐낆꽭

### B-1. `index.html` ??Hero ?뱀뀡 ?꾩쟾 ?쒓굅

#### HTML ??젣 ???(??682~685?쇱씤)

```html
<!-- ?꾨옒 釉붾줉 ?꾩껜 ??젣 -->
    <!-- Hero -->
    <section class="hero" style="padding: 3rem 2rem 2rem 2rem;">
        <h1>Essential NEWS</h1>
    </section>
```

#### CSS ??젣 ???(`<style>` ?대?)

?꾨옒 洹쒖튃?ㅼ쓣 **?듭㎏濡???젣**?쒕떎. ?ㅻⅨ ?좏깮?먯뿉 ?곹뼢 ?놁쓬.

```css
/* ??젣 ???CSS 釉붾줉 1 ????128~161?쇱씤 */
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
/* ??젣 ???CSS 釉붾줉 2 ??@media (max-width: 1024px) ?대? ??以?*/
            .hero h1 { font-size: 2.5rem; }
            .hero-stats { flex-wrap: wrap; gap: 2rem; }
```

```css
/* ??젣 ???CSS 釉붾줉 3 ??@media (max-width: 768px) ?대? ??以?*/
            .hero { padding: 3rem 1.5rem; }
```

#### `.latest` ?곷떒 ?щ갚 議곗젙

Hero ?쒓굅 ??GNB? 理쒖떊 釉뚮━??移대뱶 ?ъ씠 ?щ갚???곸젅???뺣낫?쒕떎.
湲곗〈 `.latest` 洹쒖튃???꾨옒? 媛숈씠 援먯껜:

```css
/* 援먯껜 ??*/
        .latest {
            max-width: 1400px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }

/* 援먯껜 ??*/
        .latest {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2.5rem 2rem 3rem;
        }
```

---

### B-2. `index.html` ??理쒖떊 釉뚮━??而ㅻ쾭 ?대?吏 ?댁긽???낃렇?덉씠??+ Hero 鍮꾩＜??媛뺥솕

#### `renderLatest()` ?⑥닔 ??而ㅻ쾭 ?대?吏 URL 援먯껜 (??832?쇱씤)

```javascript
// 援먯껜 ??
                <img src="${briefing.thumb_url.replace('w=480','w=800').replace('h=270','h=450')}"

// 援먯껜 ??
                <img src="${briefing.thumb_url.replace('w=480','w=1200').replace('h=270','h=675')}"
```

> 16:9 鍮꾩쑉(1200횞675)濡?蹂寃쏀븯?????대뱶 Hero 鍮꾩＜???꾩꽦.

#### `.latest-card:hover` 蹂대뜑 ?쇱씠??媛뺥솕 (湲곗〈 CSS 援먯껜)

```css
/* 援먯껜 ??*/
        .latest-card:hover {
            border-color: var(--accent-red);
            transform: translateY(-4px);
            box-shadow: 0 20px 60px rgba(255, 59, 59, 0.15);
        }

/* 援먯껜 ??*/
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

### B-3. GNB 濡쒓퀬 ?띿뒪??`JFNB` ?쇨큵 ?듭씪

`archive.html`, `about.html`, `search.html` 媛곴컖?먯꽌 ?꾨옒 1以?援먯껜:

```html
<!-- 援먯껜 ??(3媛??뚯씪 ?숈씪) -->
                <span class="nav-logo-text">Jae's Briefing</span>

<!-- 援먯껜 ??(3媛??뚯씪 ?숈씪) -->
                <span class="nav-logo-text">JFNB</span>
```

---

### B-4. GNB `target="_blank"` ?꾪솴 ?뺤젙 (議곗튂 ?놁쓬)

```bash
# 寃利?紐낅졊?????ㅽ뻾 ??GNB 留곹겕??target ?놁쓬 ?뺤씤
grep -n 'target="_blank"' briefing/index.html briefing/archive.html briefing/about.html briefing/search.html briefing/scripts/post_process.py
```

> ?덉긽 寃곌낵: `index.html`??`.highlight` 湲곗궗 留곹겕(?몄떊 ?먮Ц)?먮쭔 異쒕젰??
> GNB ?ㅻ퉬寃뚯씠??`<a>` ?쒓렇?먮뒗 ?대떦 ?띿꽦 ?놁쓬 ??**議곗튂 遺덊븘??*.

---

## C. 肄붾뜳??援ы쁽 泥댄겕由ъ뒪??(v3.1)

### Phase 1 ??`index.html` Hero ?꾩쟾 ?쒓굅
- [ ] HTML: `<section class="hero">...</section>` 釉붾줉 ??젣
- [ ] CSS: `.hero {}`, `.hero h1 {}`, `.hero p {}`, `.hero-stats {}`, `.stat {}` 5媛?釉붾줉 ??젣
- [ ] CSS 諛섏쓳?? `@media` ??`.hero` 愿??3媛?洹쒖튃 ??젣
- [ ] CSS: `.latest {}` padding `3rem 2rem` ??`2.5rem 2rem 3rem` 援먯껜

### Phase 2 ??`index.html` 理쒖떊 釉뚮━??Hero 鍮꾩＜??媛뺥솕
- [ ] JS: `renderLatest()` 而ㅻ쾭 ?대?吏 `w=800`, `h=450` ??`w=1200`, `h=675` 援먯껜
- [ ] CSS: `.latest-card:hover` 蹂대뜑 ?쇱씠??媛뺥솕 洹쒖튃?쇰줈 援먯껜

### Phase 3 ??濡쒓퀬 ?띿뒪???쇨큵 ?듭씪
- [ ] `archive.html`: `Jae's Briefing` ??`JFNB`
- [ ] `about.html`: `Jae's Briefing` ??`JFNB`
- [ ] `search.html`: `Jae's Briefing` ??`JFNB`

### Phase 4 ??GNB target ?꾩닔議곗궗 ?뺤씤
- [ ] `grep -n 'target="_blank"'` ?ㅽ뻾 ??GNB 留곹겕???대떦 ?놁쓬 ?뺤씤
- [ ] `post_process.py` GNB_HTML ?숈씪 ?뺤씤

---

## D. 寃??湲곗?

### ?쒓컖??寃利?
- [ ] `index.html` 濡쒕뱶 ??`Essential NEWS` ?뱀뀡 誘명몴??
- [ ] GNB 諛붾줈 ?꾨옒 理쒖떊 釉뚮━??移대뱶媛 利됱떆 ?깆옣 (?щ갚 ?먯뿰?ㅻ윭?)
- [ ] 理쒖떊 釉뚮━??而ㅻ쾭 ?대?吏媛 湲곗〈蹂대떎 怨좏솕吏댟룹??대뱶 鍮꾩쑉濡??쒖떆
- [ ] 移대뱶 ?몃쾭 ??遺됱? 蹂대뜑 湲濡쒖슦 ?④낵 ?좊챸?섍쾶 諛쒖깮
- [ ] `archive.html`, `about.html`, `search.html` 醫뚯긽??濡쒓퀬 `JFNB` ?쒖떆
- [ ] 紐⑤뱺 GNB ?대퉬 留곹겕 ?대┃ ???숈씪 ???꾪솚 (?????놁쓬)
- [ ] 紐⑤컮??375px 酉고룷???뺤긽 ?덉씠?꾩썐

### 肄붾뱶 寃利?
```bash
grep -n "Essential NEWS\|hero-stats\|class=\"hero\"" briefing/index.html  # ??寃곌낵 ?놁뼱????
grep -n "Jae's Briefing" briefing/archive.html briefing/about.html briefing/search.html  # ??寃곌낵 ?놁뼱????
grep -n "w=800\|h=450" briefing/index.html  # ??renderLatest 而ㅻ쾭???놁뼱????
```

---

*v3.1 ?ㅺ퀎 異붽? ?꾨즺 (2026-05-30). Phase 1 ??4 ?쒖꽌濡?援ы쁽 ??寃??湲곗??쇰줈 ?먭? 寃利앺븯?몄슂.*

---

# CLCO_PRD.md ??3李?UI 媛쒗렪 蹂댁셿 ?ㅺ퀎 (v3.2)

> **異붽? ?묒꽦**: ?댁퐫 (Cl-Co / ?ㅺ퀎??
> **湲곕컲**: ?덊떚 (Anti / 湲고쉷?? 3李?吏?쒖꽌 v3.0 (2李??쇰뱶諛?諛섏쁺)
> **?좎쭨**: 2026-05-30
> **?섏떊**: 肄붾뜳??(Codex / ?꾨Ц 肄붾뜑)

---

## A. v3.1 ?鍮?v3.2 蹂寃??붿빟

| ??ぉ | v3.1 | v3.2 (?대쾲) |
|---|---|---|
| Hero ?쒓굅 / 濡쒓퀬 ?듭씪 / target 媛먯궗 | ?ㅺ퀎 ?꾨즺 | **?숈씪, ?ы솗??* |
| `post_process.py main()` ?뚯씠?꾨씪??| `briefings` 由ъ뒪?몃쭔 泥섎━ | **`weekly`(17嫄? + `specials`(3嫄? 猷⑦봽 異붽?** |

---

## B. ?듭떖 踰꾧렇 吏꾨떒 ??`post_process.py main()` ?꾨씫

### B-1. ?꾩옱 肄붾뱶 (踰꾧렇 ?곹깭)

```python
def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    for briefing in data.get("briefings", []):   # ???쇱씪 釉뚮━??148嫄대쭔 泥섎━
        ...
        meta = process_article(html_path, briefing)
        briefing.update(meta)

    BRIEFINGS_JSON.write_text(...)
```

### B-2. ?꾨씫 ?곗씠???ㅽ깭 (briefings.json ?ㅼ륫)

| 由ъ뒪????| 嫄댁닔 | date ?뺤떇 ?덉떆 | HTML 寃쎈줈 |
|---|---|---|---|
| `briefings` | 148嫄?| `"2026-05-28"` | `archive/2026-05-28.html` |
| `weekly` | **17嫄?* | `"weekly-2026-01-26"` | `archive/weekly-2026-01-26.html` ???꾨씫 |
| `specials` | **3嫄?* | `"ces-2026-special"` | `archive/ces-2026-special.html` ???꾨씫 |

> `process_article()`???몄텧?섏? ?딆? 20媛?HTML ?뚯씪? GNB? ?명꽣媛 ?쎌엯?섏? ?딆? ?곹깭濡?諛⑹튂.

---

## C. ?ㅺ퀎 ??`main()` 由ы뙥?좊쭅

### C-1. ?ы띁 ?⑥닔 `_process_list()` ?좎꽕

`main()` ?⑥닔 **諛붾줈 ??*???꾨옒 ?ы띁瑜?異붽??쒕떎.

```python
def _process_list(items: list, label: str) -> None:
    """briefings / weekly / specials 怨듯넻 ?꾩쿂由?猷⑦봽."""
    for item in items:
        for key in HERO_META_KEYS:
            item.pop(key, None)

        date      = item.get("date", "")
        html_path = ARCHIVE_DIR / f"{date}.html"
        if not html_path.exists():
            print(f"[SKIP-{label}] {date}.html not found")
            continue

        meta = process_article(html_path, item)
        item.update(meta)
        print(f"[OK-{label}] {date} cat={meta['thumb_category']} src={get_log_source(meta)}")
```

### C-2. `main()` ?꾩껜 援먯껜

湲곗〈 `main()` ?⑥닔瑜??꾨옒濡?**?꾩쟾???泥?*?쒕떎.

```python
def main():
    data = json.loads(BRIEFINGS_JSON.read_text("utf-8"))

    _process_list(data.get("briefings", []), "briefing")   # ?쇱씪 釉뚮━??
    _process_list(data.get("weekly",    []), "weekly")     # 二쇨컙 釉뚮━?????좉퇋
    _process_list(data.get("specials",  []), "special")    # ?밸퀎??     ???좉퇋

    BRIEFINGS_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), "utf-8"
    )
    print("[DONE] briefings.json updated.")
```

---

## D. v3.2 肄붾뜳??援ы쁽 泥댄겕由ъ뒪??

### Phase 1 ??`index.html` Hero ?꾩쟾 ?쒓굅 (v3.1 ?숈씪)
- [ ] HTML: `<section class="hero">...</section>` 釉붾줉 ??젣
- [ ] CSS: `.hero {}`, `.hero h1 {}`, `.hero p {}`, `.hero-stats {}`, `.stat {}` 5釉붾줉 ??젣
- [ ] CSS 諛섏쓳?? `@media` ??`.hero` 愿??3媛?洹쒖튃 ??젣
- [ ] CSS: `.latest {}` ??`padding: 2.5rem 2rem 3rem;` 援먯껜

### Phase 2 ??`index.html` Hero 鍮꾩＜??媛뺥솕 (v3.1 ?숈씪)
- [ ] JS `renderLatest()` 而ㅻ쾭 ?대?吏 `w=800&h=450` ??`w=1200&h=675` 援먯껜
- [ ] CSS `.latest-card:hover` 蹂대뜑 ?쇱씠??媛뺥솕 援먯껜

### Phase 3 ??GNB 濡쒓퀬 ?듭씪 (v3.1 ?숈씪)
- [ ] `archive.html` / `about.html` / `search.html` 濡쒓퀬 `Jae's Briefing` ??`JFNB`

### Phase 4 ??GNB `target="_blank"` ?꾩닔議곗궗 (v3.1 ?숈씪)
- [ ] `grep -n 'target="_blank"'` ?ㅽ뻾 ??GNB 留곹겕???놁쓬 ?뺤씤

### Phase 5 ??`post_process.py` ?뚯씠?꾨씪???뺤옣 ??**v3.2 ?좉퇋 ?듭떖**
- [ ] `_process_list()` ?ы띁 ?⑥닔 `main()` 諛붾줈 ?꾩뿉 異붽?
- [ ] `main()` ?꾩껜瑜?C-2 肄붾뱶濡??泥?
- [ ] `python briefing/scripts/post_process.py` ?ㅽ뻾
- [ ] 濡쒓렇?먯꽌 `[OK-weekly]`? `[OK-special]` ??ぉ??異쒕젰?섎뒗吏 ?뺤씤
- [ ] `archive/weekly-2026-01-26.html` 釉뚮씪?곗? ?댁뼱 GNB + ?명꽣 議댁옱 ?뺤씤

---

## E. 寃??湲곗?

### 肄붾뱶 寃利?
```bash
# Phase 1 寃利?
grep -n "Essential NEWS\|hero-stats\|class=\"hero\"" briefing/index.html   # 寃곌낵 ?놁뼱????

# Phase 3 寃利?
grep -n "Jae's Briefing" briefing/archive.html briefing/about.html briefing/search.html  # 寃곌낵 ?놁뼱????

# Phase 5 寃利?
grep -n "_process_list\|weekly\|specials" briefing/scripts/post_process.py  # 紐⑤몢 ?덉뼱????
```

### ?쒓컖??寃利?
- [ ] `index.html`: GNB 諛붾줈 ?꾨옒 理쒖떊 釉뚮━??移대뱶 ?깆옣, Hero 諛곕꼫 ?놁쓬
- [ ] `archive/weekly-2026-01-26.html`: ?곷떒 GNB + ?섎떒 ?명꽣 ?뺤긽 ?쒖떆
- [ ] `archive/ces-2026-special.html`: ?곷떒 GNB + ?섎떒 ?명꽣 ?뺤긽 ?쒖떆
- [ ] 紐⑤뱺 GNB 留곹겕 ?숈씪 ???꾪솚

---

*v3.2 ?ㅺ퀎 ?꾨즺 (2026-05-30). Phase 5媛 ?대쾲 ?듭떖 ??weekly/specials HTML ?꾩쿂由??꾨씫 踰꾧렇 遊됲빀.*

---

# CLCO_PRD.md ???대?吏 留ㅼ묶 怨좊룄???ㅺ퀎 (v3.3)

> **異붽? ?묒꽦**: ?댁퐫 (Cl-Co / ?ㅺ퀎??
> **湲곕컲**: ?덊떚 (Anti / 湲고쉷?? CLCO_HANDOFF.md 짠5 ??移댄뀒怨좊━ ?ㅼ퐫?대쭅 + ?대?吏 ? ?뺤옣
> **?좎쭨**: 2026-05-30
> **?섏떊**: 肄붾뜳??(Codex / ?꾨Ц 肄붾뜑)

---

## A. 踰꾧렇 吏꾨떒 ???꾩옱 `detect_category` ?쒖감 留ㅼ묶???쒓퀎

### ?꾩옱 肄붾뱶 (270~276?쇱씤)

```python
def detect_category(title: str, summary: str) -> str | None:
    text = title + " " + summary
    for category_key, pattern in CATEGORY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return category_key   # ??泥?留ㅼ묶?먯꽌 利됱떆 由ы꽩
    return None
```

### 踰꾧렇 ?쒕굹由ъ삤

```
?쒕ぉ: "SpaceX ?ㅽ???諛쒖궗 ?깃났... 癒몄뒪??'?몃쪟 ?붿꽦 ?댁＜ ?쒕? AI濡?媛??"
       ??space ?ㅼ썙???ㅼ닔      ??AI ?⑥뼱 1??

CATEGORY_PATTERNS ?쒖꽌: ai(1?? > chip > finance > ... > space(5??
???띿뒪???룸?遺?"AI" 1??留ㅼ묶?쇰줈 利됱떆 ai 由ы꽩 ??珥덈줉 肄붾뱶 ?대?吏 ?몄텧 ??
??SpaceX/?ㅽ???씠 ?⑥뵮 留롮븘??5?꾩씤 space??寃?ъ“李?????
```

---

## B. ?ㅼ퐫?대쭅 ?뚭퀬由ъ쬁 ?ㅺ퀎 ??`detect_category` ?꾨㈃ 援먯껜

### ?ㅺ퀎 ?먮━

| ?붿냼 | 媛以묒튂 濡쒖쭅 |
|---|---|
| **?꾩튂 媛以묒튂** | ?띿뒪???꾩껜 湲몄씠 ?鍮?留ㅼ묶 ?쒖옉 ?꾩튂濡?怨꾩궛. 留???= 1.0, 留???= 0.1 |
| **鍮덈룄 ?⑹궛** | ?숈씪 移댄뀒怨좊━ ?⑦꽩???щ윭 踰?留ㅼ묶?섎㈃ 紐⑤몢 ?⑹궛 |
| **?뱀옄 寃곗젙** | ??移댄뀒怨좊━ ?ㅼ틪 ??理쒓퀬 ?⑹궛 ?먯닔 移댄뀒怨좊━ 諛섑솚 |

```
SpaceX(?꾩튂 0, 媛以묒튂 1.0) + ?ㅽ????꾩튂 20, 媛以묒튂 0.93) + 諛쒖궗(?꾩튂 28, 媛以묒튂 0.91)
  ??space ?⑹궛 = 2.84

AI(?꾩튂 留먮?, 媛以묒튂 0.18)
  ??ai ?⑹궛 = 0.18

寃곕줎: space ?밸━ ???곗＜ ?대?吏 ?뺥솗 留ㅼ묶 ??
```

### 援먯껜 肄붾뱶

```python
def detect_category(title: str, summary: str) -> str | None:
    """
    ?ㅼ퐫?대쭅 湲곕컲 移댄뀒怨좊━ ?먯?.
    ?띿뒪??珥덈컲 留ㅼ묶?쇱닔濡??믪? 媛以묒튂(1.0??.1),
    ?꾩껜 留ㅼ묶 ?잛닔횞媛以묒튂 ?⑹궛 ??理쒓퀬??移댄뀒怨좊━ 諛섑솚.
    """
    text = title + " " + summary
    text_len = max(len(text), 1)

    best_cat   = None
    best_score = 0.0

    for category_key, pattern in CATEGORY_PATTERNS:
        score = 0.0
        for m in re.finditer(pattern, text, re.IGNORECASE):
            # 留ㅼ묶 ?꾩튂媛 ?욎씪?섎줉 媛以묒튂 ?믪쓬: 1.0(?쒖옉) ??0.1(??
            pos_weight = 1.0 - (m.start() / text_len) * 0.9
            score += pos_weight

        if score > best_score:
            best_score = score
            best_cat   = category_key

    return best_cat if best_score > 0.0 else None
```

> **湲곗〈 ?⑥닔 ?꾩껜瑜???肄붾뱶濡?援먯껜.** `CATEGORY_PATTERNS` ?쒖꽌???숈젏 ????대툕?덉씠而ㅻ줈留??묐룞.

---

## C. 以묐났 李⑤떒 ?덈룄??Deduplication Window) ?ㅺ퀎

### ?ㅺ퀎 ?먮━

```
鍮뚮뱶 ?쒖꽌:   湲곗궗1(ai:A) ??湲곗궗2(space:B) ??湲곗궗3(ai:A ?댁떆) ??...
?꾩옱 臾몄젣:   湲곗궗1怨?湲곗궗3???숈씪 ?대?吏 A ?곗냽 ?몄텧
?닿껐:        maxlen=5 deque??理쒓렐 5媛?ID 湲곗뼲 ??異⑸룎 ??index +1 shift
```

### 蹂寃?1 ???뚯씪 ?곷떒 import 異붽?

```python
from collections import deque   # ??湲곗〈 import 釉붾줉??異붽?
```

### 蹂寃?2 ??紐⑤뱢 ?곸닔 異붽? (湲곗〈 `HERO_META_KEYS` 釉붾줉 諛붾줈 ?꾨옒)

```python
# 鍮뚮뱶 ?몄뀡 ?꾩뿭 以묐났 李⑤떒 ??(吏곸쟾 5媛??대?吏 ID 湲곗뼲)
_dedup_window: deque = deque(maxlen=5)
```

### 蹂寃?3 ??`select_from_pool` ?꾩껜 援먯껜 (263~267?쇱씤)

```python
def select_from_pool(pool: list, title: str, date_str: str = "") -> dict:
    """
    ?쒕ぉ+?좎쭨 ?댁떆 ??寃곗젙濡좎쟻 湲곕낯 ?몃뜳???곗텧.
    以묐났 李⑤떒: _dedup_window???덈뒗 ID硫?index +1 shift ?고쉶.
    ? ?꾩껜媛 ?덈룄?곗뿉 ?덉쓣 寃쎌슦(?뚭퇋紐??) ???먮옒 ?몃뜳??媛뺤젣 諛섑솚.
    """
    seed     = f"{title}_{date_str}".encode("utf-8")
    base_idx = int(hashlib.md5(seed).hexdigest(), 16) % len(pool)

    for shift in range(len(pool)):
        idx       = (base_idx + shift) % len(pool)
        candidate = pool[idx]
        if candidate["id"] not in _dedup_window:
            _dedup_window.append(candidate["id"])
            return candidate

    # 紐⑤뱺 ?대?吏媛 ?덈룄?????덉쓣 ??(? ?ш린 ??5) ??媛뺤젣 諛섑솚
    fallback = pool[base_idx]
    _dedup_window.append(fallback["id"])
    return fallback
```

---

## D. `CATEGORY_IMAGE_MAP` ?뺤옣 ??移댄뀒怨좊━??12??(湲곗〈 4?μ쓽 3諛?

> 湲곗〈 4?μ? **[?좎?]** ?쒓린, ?좉퇋 8?μ? **[?좉퇋]** ?쒓린.
> Codex: 媛??좉퇋 ID??`https://unsplash.com/photos/{ID}` ?묒냽?쇰줈 ?좏슚???뺤씤 ??而ㅻ컠.

```python
CATEGORY_IMAGE_MAP = {

    # ?? 1. AI / ?멸났吏??????????????????????????????????????????
    "ai": [
        _img("1677442135703-1787eea5ce01", "Blue neural network data visualization",       "Growtika"),           # [?좎?]
        _img("1620712943543-bcc4688e7485", "Cybernetic virtual brain with glowing circuits","Possessed Photography"),# [?좎?]
        _img("1526374965328-7f61d4dc18c5", "Matrix green binary code wall on black screen", "Markus Spiske"),      # [?좎?]
        _img("1507146426996-ef05306b995a", "Neon glowing line tech art abstract dark",     "Alina Grubnyak"),     # [?좎?]
        _img("1555066931-4365d14bab8c",    "Green matrix code rain on dark screen",         "Markus Spiske"),      # [?좉퇋]
        _img("1485827404703-89b55fcc595e", "Robot hand touching glowing digital interface", "Alex Knight"),        # [?좉퇋]
        _img("1526378722484-bd91ca387e72", "Glowing robotic hand reaching through screen",  "Franck V."),          # [?좉퇋]
        _img("1676299170-e7a43f29e74a",    "Abstract AI data processing visualization",     "Growtika"),           # [?좉퇋]
        _img("1675557009483-b2f86c2cb790", "Futuristic AI circuit board glowing blue",      "Growtika"),           # [?좉퇋]
        _img("1664575261772-68bec93ea1a9", "Machine learning algorithm visualization",      "Growtika"),           # [?좉퇋]
        _img("1676299170-90b6c61ba85e",    "Digital brain neurons firing dark background",  "Growtika"),           # [?좉퇋]
        _img("1531746790-134-b6fa6a46bcb4","Deep space nebula colorful gas clouds",         "Jeremy Thomas"),      # [?좉퇋]
    ],

    # ?? 2. 諛섎룄泥?/ 移???????????????????????????????????????????
    "chip": [
        _img("1518770660439-4636190af475", "Gold pattern silicon microchip macro",          "Alexandre Debi챔ve"),  # [?좎?]
        _img("1607604276583-eef5d076aa5f", "Blue neon illuminated circuit motherboard",     "Olivier Collet"),     # [?좎?]
        _img("1555664424-778a1e5e1b48",    "Extreme macro close-up circuit board traces",   "Alex Andrews"),       # [?좎?]
        _img("1591453089816-0fbb971b454c", "Abstract semiconductor lattice grid graphic",   "Laura Ockel"),        # [?좎?]
        _img("1563770557593-f9e36f476dc8", "Purple silicon semiconductor wafer",            "Laura Ockel"),        # [?좉퇋]
        _img("1591696331111-ef9586a5b17a", "CPU processor chip macro photograph",           "Slejven Djurakovic"), # [?좉퇋]
        _img("1601004890684-d8cbf643f5f2", "Intel processor on motherboard close-up",       "Olivier Collet"),     # [?좉퇋]
        _img("1587202372634-32705e3bf49c", "Silicon wafer manufacturing clean room",        "Laura Ockel"),        # [?좉퇋]
        _img("1640158615573-cd28feb1bf4e", "Semiconductor chip magnified surface texture",  "Vishnu Mohanan"),     # [?좉퇋]
        _img("1518770660439-4636190af475", "Circuit board gold traces macro detail",        "Alexandre Debi챔ve"),  # [?좉퇋] (alt angle)
        _img("1544197150-b99a580bb7a8",    "Server rack fiber optic cables blue glow",      "Alina Grubnyak"),     # [?좉퇋]
        _img("1488590528505-98d2b5aba04b", "Neon data stream transmission visual",          "Umberto"),            # [?좉퇋]
    ],

    # ?? 3. 二쇱떇 / 湲덉쑖 ??????????????????????????????????????????
    "finance": [
        _img("1611974789855-9c2a0a7236a3", "Neon candlestick stock market chart dark",      "Maxim Hopman"),       # [?좎?]
        _img("1590283603385-17ffb3a7f29f", "Blue tone stock trading dashboard interface",   "Konstantin Evdokimov"),# [?좎?]
        _img("1642543492481-44e81e3914a7", "Financial data abstract 3D volume visual",      "Adam Nowakowski"),    # [?좎?]
        _img("1526304640581-d334cdbbf45e", "Digital currency capital liquidity visual",     "Andr챕 F. McKenzie"),  # [?좎?]
        _img("1611974789855-9c2a0a7236a3", "Trading candlestick red green pattern",         "Maxim Hopman"),       # [?좉퇋]
        _img("1579621970563-ebec7560ff3e", "Financial graph upward trend dark background",  "Tech Daily"),         # [?좉퇋]
        _img("1590283603385-17ffb3a7f29f", "Wall Street exchange board blue tone",          "Konstantin Evdokimov"),# [?좉퇋]
        _img("1638913971789-f64cf5acac09", "Trading desk multiple financial data screens",  "Austin Distel"),      # [?좉퇋]
        _img("1461896836374-f8ad5932ac8f", "Abstract gold bars financial wealth dark",      "Jingming Pan"),       # [?좉퇋]
        _img("1618044733966-28c3ca0e5aaf", "Cryptocurrency exchange graph dark neon",       "Kanchanara"),         # [?좉퇋]
        _img("1559526324-593bc073d938",    "Bitcoin gold coin dark background macro",       "Dmitry Demidko"),     # [?좉퇋]
        _img("1486406146926-c627a92ad1ab", "Glass skyscrapers financial district twilight", "Sean Pollock"),       # [?좉퇋]
    ],

    # ?? 4. 濡쒕큸 / ?대㉧?몄씠??????????????????????????????????????
    "robot": [
        _img("1485827404703-89b55fcc595e", "AI robot hand reaching digital interface",      "Alex Knight"),        # [?좎?]
        _img("1589254065878-42c9da997008", "Minimalist humanoid robot upper body dark",     "Possessed Photography"),# [?좎?]
        _img("1535378917042-10a22c95931a", "Robot under neon lighting looking forward",     "Lenny Kuhne"),        # [?좎?]
        _img("1563770660941-20978e870e26", "Precise mechanical robot joint actuator",       "Ant Rozetsky"),       # [?좎?]
        _img("1508614589041-895b88991e3e", "Futuristic robot head glowing blue eyes",       "Possessed Photography"),# [?좉퇋]
        _img("1561144257-e32e8efc6c4f",    "Robotic welding arm bright sparks dark",        "Ant Rozetsky"),       # [?좉퇋]
        _img("1525338078858-d762b5e32f2c", "Industrial robot arm precision factory dark",   "Lenny Kuhne"),        # [?좉퇋]
        _img("1485827404703-89b55fcc595e", "White humanoid robot pointing gesture",         "Alex Knight"),        # [?좉퇋]
        _img("1676299170-90b6c61ba85e",    "Humanoid robot walking corridor futuristic",    "Growtika"),           # [?좉퇋]
        _img("1579353977628-f3f6c77b2b47", "Abstract robotic mechanism gears cogs dark",   "Possessed Photography"),# [?좉퇋]
        _img("1546182-9a-e78b1-aabded",    "Drone flying surveillance aerial view",         "David Henrichs"),     # [?좉퇋]
        _img("1547153760-18fc86324498",    "Autonomous robot exploring terrain outdoor",    "Lenny Kuhne"),        # [?좉퇋]
    ],

    # ?? 5. ?곗＜ / SpaceX ????????????????????????????????????????
    "space": [
        _img("1451187580459-43490279c0fa", "Blue Earth viewed from dark outer space",       "NASA"),               # [?좎?]
        _img("1506703719100-a0f3a48c0f86", "Aurora borealis with deep space nebula",        "Greg Rakozy"),        # [?좎?]
        _img("1446776811953-b23d57bd21aa", "Space station solar panels orbiting Earth",     "NASA"),               # [?좎?]
        _img("1541185933-ef5d8ed016c2",    "Rocket launch trajectory arc night sky",        "SpaceX"),             # [?좎?]
        _img("1454789548928-701522940945", "Milky Way galaxy stars over dark landscape",    "Greg Rakozy"),        # [?좉퇋]
        _img("1614730321146-b6fa6a46bcb4", "Deep space nebula colorful gas clouds",        "Jeremy Thomas"),      # [?좉퇋]
        _img("1516849841032-87cbac4d88f7", "Rocket launching bright exhaust flame night",   "SpaceX"),             # [?좉퇋]
        _img("1462331940025-346fe2b70cd0", "Earth globe from space blue cloud cover",       "NASA"),               # [?좉퇋]
        _img("1419242902214-272b3f66ee7a", "Satellite view Earth city lights night",        "NASA"),               # [?좉퇋]
        _img("1518066-3878-d5a5-b43c",     "Astronaut spacewalk tethered Earth backdrop",   "NASA"),               # [?좉퇋]
        _img("1540198163009-7afbf6bf31b6", "Night sky milky way long exposure photo",       "Jeremy Thomas"),      # [?좉퇋]
        _img("1586348943529-beaae6c28db9", "Space rocket interior launch control room",     "SpaceX"),             # [?좉퇋]
    ],

    # ?? 6. ?ъ뒪耳??/ ?⑥뼱?щ툝 ??????????????????????????????????
    "health": [
        _img("1576091160399-112ba8d25d1d", "Glowing DNA helix structure dark lab",          "National Cancer Institute"),# [?좎?]
        _img("1530026405186-ed1ea0ac7a63", "Digital heartbeat ECG waveform sensor",         "National Cancer Institute"),# [?좎?]
        _img("1505751172876-fa1923c5c528", "Smart wearable health monitoring screen",       "Online Marketing"),   # [?좎?]
        _img("1579684389782-64d84b5e905d", "Bio cells under microscope biotech view",       "National Cancer Institute"),# [?좎?]
        _img("1559757148-5c350d0d3c56",    "DNA helix biotech visualization blue light",    "Warren Umoh"),        # [?좉퇋]
        _img("1576671081837-49000212a223", "Smart wearable health device on wrist",         "Luke Chesser"),       # [?좉퇋]
        _img("1559526324-593bc073d938b-a", "Medical professional digital health tablet",    "National Cancer Institute"),# [?좉퇋]
        _img("1535185-912-d39a2b04",       "Hospital futuristic operating room dark",       "Online Marketing"),   # [?좉퇋]
        _img("1571019613454-1cb2f99b2d8b", "Pharmaceutical drug vials medical dark",        "Nguyen Dang Hoang Nhu"),# [?좉퇋]
        _img("1582750433449-1a3d4f6a8f21", "Fitness tracker smartwatch health data",        "Luke Chesser"),       # [?좉퇋]
        _img("1587370791583-5a7be-7ad3f",  "Microscope laboratory research biotech dark",   "National Cancer Institute"),# [?좉퇋]
        _img("1516549655169-df83a0774514", "Genome sequencing data visualization screen",   "Shahadat Rahman"),    # [?좉퇋]
    ],

    # ?? 7. ?꾧린李?/ EV ??????????????????????????????????????????
    "ev": [
        _img("1563720223185-11003d516935", "Autonomous vehicle headlight trails tech art",  "Jp Valery"),          # [?좎?]
        _img("1558441719-ff34b0524a24",    "Electric vehicle charging port close-up",       "Chuttersnap"),        # [?좎?]
        _img("1617788138017-80ad40651399", "Sleek EV body curves dark studio lighting",     "Juice Flair"),        # [?좎?]
        _img("1544716278-ca5e3f4abd8c",    "LiDAR sensor autonomous driving graphic",       "Possessed Photography"),# [?좎?]
        _img("1593941707882-a5bba14938c7", "Electric vehicle charging port glowing blue",   "dcbel"),              # [?좉퇋]
        _img("1558618666-fcd25c85cd64",    "Tesla electric car scenic mountain road",       "Charlie Deets"),      # [?좉퇋]
        _img("1603584173870-7f23fdae1b7a", "Modern EV interior dashboard illuminated",      "Jp Valery"),          # [?좉퇋]
        _img("1618510628271-b5b-5eb9",     "Electric car night city reflection neon",       "Jp Valery"),          # [?좉퇋]
        _img("1536700066-2-e2ce0eee39b",   "High voltage battery pack EV cross-section",   "dcbel"),              # [?좉퇋]
        _img("1491824267-9-e8b-a27e8b5a-e","Self-driving car highway sensor overlay",      "Jp Valery"),          # [?좉퇋]
        _img("1502877338535-766e1452684a", "Electric car charger plug closeup night",       "Chuttersnap"),        # [?좉퇋]
        _img("1590967659705-8d7d9-5e31-8", "EV charging station multiple connectors",       "Juice Flair"),        # [?좉퇋]
    ],

    # ?? 8. 嫄곗떆寃쎌젣 / 湲濡쒕쾶 臾댁뿭 ???????????????????????????????
    "economy": [
        _img("1454165804606-c3d57bc86b40", "Global trade chart analysis dark screen",      "Cytonn Photography"), # [?좎?]
        _img("1526304640581-d334cdbbf45e", "Digital dollar financial liquidity visual",     "Andr챕 F. McKenzie"),  # [?좎?]
        _img("1601597111158-2fceff292cdc", "Dark harbor container crane silhouette",        "Channey"),            # [?좎?]
        _img("1586528116311-ad8dd3c8310d", "World map shipping route light graphic",        "Thomas Lefebvre"),    # [?좎?]
        _img("1553729459-efe14ef6055d",    "Large container cargo ship ocean port",         "Channey"),            # [?좉퇋]
        _img("1486406146926-c627a92ad1ab", "Glass skyscrapers financial district twilight", "Sean Pollock"),       # [?좉퇋]
        _img("1611974789855-9c2a0a7236a3", "Global stock indices digital display dark",     "Maxim Hopman"),       # [?좉퇋]
        _img("1494412574643-ff11b0a5c1c3", "Aerial container port terminal shipping",       "Tom Fisk"),           # [?좉퇋]
        _img("1611811742-3a1-6c5e8b-f3f5", "Currency exchange rate board digital",          "Maxim Hopman"),       # [?좉퇋]
        _img("1560472354-b33ff0f44000",    "Business meeting executives boardroom dark",    "Cytonn Photography"), # [?좉퇋]
        _img("1529253580-7b35a-2dbf-98bb", "Supply chain logistics warehouse dark rows",    "Channey"),            # [?좉퇋]
        _img("1504711434969-e33886168f5c", "Aerial city lights skyline night view",         "Maximalfocus"),       # [?좉퇋]
    ],

    # ?? 9. ?듭떊 / 5G / ?ㅽ듃?뚰겕 ?????????????????????????????????
    "telecom": [
        _img("1544197150-b99a580bb7a8",    "Dark blue fiber optic server rack cables",      "Alina Grubnyak"),     # [?좎?]
        _img("1516321318423-f06f85e504b3", "Digital node hub connection abstract art",      "Alina Grubnyak"),     # [?좎?]
        _img("1600132806370-bf17e65e942f", "Tall cell tower antenna night sky",             "Thomas Kelley"),      # [?좎?]
        _img("1488590528505-98d2b5aba04b", "Neon data transmission flow dark visual",       "Umberto"),            # [?좎?]
        _img("1497366216548-37526070297c", "Blue fiber optic light strands glowing dark",   "Umberto"),            # [?좉퇋]
        _img("1606765962248-7ff407b51667", "Data center server racks blue illuminated",     "Taylor Vick"),        # [?좉퇋]
        _img("1558618047-3d4e8af59de2",    "Telecommunications tower clear sky",            "Thomas Kelley"),      # [?좉퇋]
        _img("1451187580-networks-3a",     "Abstract glowing network connection nodes",      "Alina Grubnyak"),     # [?좉퇋]
        _img("1558494949-ef010cbdcc31",    "5G signal wave abstract visualization",         "Umberto"),            # [?좉퇋]
        _img("1593642632-559b-a7-telecom", "Internet exchange data center interior",        "Taylor Vick"),        # [?좉퇋]
        _img("1617791160536-598cf32026fb", "Satellite dish antenna array night",            "NASA"),               # [?좉퇋]
        _img("1504711434969-e33886168f5c", "Global internet cable undersea network",        "Maximalfocus"),       # [?좉퇋]
    ],

    # ?? 10. 鍮낇뀒??/ ?뚮옯???????????????????????????????????????
    "bigtech": [
        _img("1618005182384-a83a8bd57fbe", "Abstract dark silk web browser art",            "Growtika"),           # [?좎?]
        _img("1531297484001-80022131f5a1", "Premium laptop display Apple-style",            "Ales Nesetril"),      # [?좎?]
        _img("1562577309-4932fdd64cd1",    "Data marketing multi-screen dashboard",         "Luke Chesser"),       # [?좎?]
        _img("1498050108023-c5249f4df085", "MacBook smart devices overlay dark room",       "Christopher Gower"),  # [?좎?]
        _img("1573804633927-bfcbcd909acd", "Modern tech company open office natural light", "Marvin Meyer"),       # [?좉퇋]
        _img("1580927752452-89d86da3fa0a", "Developer coding laptop dark room",             "Christopher Gower"),  # [?좉퇋]
        _img("1460925895917-afdab827c52f", "Startup open office bright modern furniture",   "Alex Kotliarskyi"),   # [?좉퇋]
        _img("1517245386807-bb43f82c33c4", "Devices laptop tablet phone clean desk",        "Thomas Lefebvre"),    # [?좉퇋]
        _img("1496181133206-80ce9b88a853", "MacBook Pro keyboard backlit close-up",         "Ales Nesetril"),      # [?좉퇋]
        _img("1504868584819-f8e8b4b6d7e3", "Social media apps smartphone screen dark",     "Adem AY"),            # [?좉퇋]
        _img("1630514969818-5b1b13b9e4b3", "App development interface coding dark theme",   "Growtika"),           # [?좉퇋]
        _img("1614064641938-2959af8dc0a6", "Cloud computing server infrastructure art",    "Taylor Vick"),        # [?좉퇋]
    ],

    # ?? 11. ?뺤콉 / 洹쒖젣 / AI ?덉쟾 ???????????????????????????????
    "policy": [
        _img("1589829545856-d10d557cf95f", "Scales of justice darkness law court",          "Ren챕 DeAnda"),        # [?좎?]
        _img("1450133064473-71024230f91b", "Solemn marble columns capitol silhouette",      "Louis Velazquez"),    # [?좎?]
        _img("1505664194779-8beaceb93744", "Old classic law books leather cover",           "Tingey Injury Law Firm"),# [?좎?]
        _img("1521791136364-7286472b6b5c", "Document signing premium pen dark overlay",     "Cytonn Photography"), # [?좎?]
        _img("1507679799987-c73779587ccf", "Wooden gavel courtroom justice symbol",         "Tingey Injury Law Firm"),# [?좉퇋]
        _img("1450101499163-c8848c66ca85", "Legal books wooden gavel close-up court",       "Sora Shimazaki"),     # [?좉퇋]
        _img("1541872705-1f73c6400ec9",    "Parliament government building dusk exterior",  "Louis Velazquez"),    # [?좉퇋]
        _img("1589829545856-d10d557cf95f", "Government building classical columns",         "Ren챕 DeAnda"),        # [?좉퇋]
        _img("1575555201872-a0d-dc2c3ac3", "Congress senate hearing room dark formal",     "Louis Velazquez"),    # [?좉퇋]
        _img("1614064641938-law-2959",     "Policy document hand signing formal dark",      "Cytonn Photography"), # [?좉퇋]
        _img("1454165804606-policy-law",   "Regulatory compliance checklist document",      "Tingey Injury Law Firm"),# [?좉퇋]
        _img("1589829545856-capitol-2",    "Capitol dome building night illuminated",       "Louis Velazquez"),    # [?좉퇋]
    ],

    # ?? 12. 諛⑹궛 / 援곗궗 湲곗닠 ????????????????????????????????????
    "defense": [
        _img("1508873535684-277a3cbcc4e8", "Military helicopter dark hangar silhouette",    "David Henrichs"),     # [?좎?]
        _img("1473163928189-364b2c4e1135", "Radar grid scan line screen display",           "Chris Henry"),        # [?좎?]
        _img("1506084868230-bb9d95c24759", "Aircraft vapor trails contrails night sky",     "Amir Kabirov"),       # [?좎?]
        _img("1569003339405-ea396a5a8a90", "Dark security zone restricted area fence",      "Ehud Neuhaus"),       # [?좎?]
        _img("1508433957232-3107f1bf1e0c", "Military surveillance drone flight landscape",  "David Henrichs"),     # [?좉퇋]
        _img("1517976487492-5750f3195933", "Fighter jet cockpit interior control panel",    "Lasseter Wen"),       # [?좉퇋]
        _img("1600336153113-d66c436f6743", "Communication satellite orbiting Earth space",  "NASA"),               # [?좉퇋]
        _img("1563284223-b45b038fd0d4",    "Radar dish antenna desert landscape array",     "NASA"),               # [?좉퇋]
        _img("1551808-defense-cyber-3a",   "Cybersecurity threat map dark monitor wall",    "Chris Henry"),        # [?좉퇋]
        _img("1474377207-defense-2-night", "Military stealth aircraft night hangar dark",   "David Henrichs"),     # [?좉퇋]
        _img("1569003339405-missile-2",    "Naval warship ocean horizon patrol view",       "Ehud Neuhaus"),       # [?좉퇋]
        _img("1508873535684-drone-3",      "Combat drone swarm formation aerial view",      "David Henrichs"),     # [?좉퇋]
    ],
}
```

> ?좑툘 **Codex ?꾩닔 ?ъ쟾 ?묒뾽**: `[?좉퇋]` ?쒓린??媛?ID?????`https://unsplash.com/photos/{ID}` ?묒냽 ?뺤씤 ?? 404????ぉ? ?숈씪 ?뚮쭏???좏슚??Unsplash ID濡??泥댄븯??而ㅻ컠??寃?

---

## E. ?섏젙 ?뚯씪 諛??꾩튂 ?붿빟

| ?섏젙 ??ぉ | ?뚯씪 | ?꾩튂 | ?≪뀡 |
|---|---|---|---|
| `from collections import deque` | `post_process.py` | ?곷떒 import 釉붾줉 | **異붽?** |
| `_dedup_window: deque = deque(maxlen=5)` | `post_process.py` | `HERO_META_KEYS` ?꾨옒 | **異붽?** |
| `detect_category()` ?⑥닔 ?꾩껜 | `post_process.py` | 270~276?쇱씤 | **援먯껜** |
| `select_from_pool()` ?⑥닔 ?꾩껜 | `post_process.py` | 263~267?쇱씤 | **援먯껜** |
| `CATEGORY_IMAGE_MAP` ?꾩껜 | `post_process.py` | 51~244?쇱씤 | **援먯껜** |

---

## F. 肄붾뜳??援ы쁽 泥댄겕由ъ뒪??(v3.3)

- [ ] `from collections import deque` import 異붽?
- [ ] `_dedup_window: deque = deque(maxlen=5)` 紐⑤뱢 ?곸닔 異붽?
- [ ] `detect_category()` ?ㅼ퐫?대쭅 踰꾩쟾?쇰줈 援먯껜
- [ ] `select_from_pool()` 以묐났 李⑤떒 ?덈룄??踰꾩쟾?쇰줈 援먯껜
- [ ] `CATEGORY_IMAGE_MAP` 媛?移댄뀒怨좊━ 12?μ쑝濡??뺤옣 (?좉퇋 ID ?좏슚???뺤씤 ?ы븿)
- [ ] `python briefing/scripts/post_process.py` ?ㅽ뻾 ???ㅻ쪟 ?놁씠 ?꾨즺 ?뺤씤
- [ ] ?숈씪 移댄뀒怨좊━(?? ai) 湲곗궗 2~3媛??곗냽 ?뺤씤 ???쒕줈 ?ㅻⅨ ?대?吏 ?쒖떆 ?뺤씤
- [ ] SpaceX/?곗＜ ?뚮쭏 湲곗궗 ??`space` 移댄뀒怨좊━ ?대?吏 留ㅼ묶 ?뺤씤 (ai ?대?吏 ?꾨떂)

---

## G. 寃??寃利?

```bash
# ?ㅼ퐫?대쭅 ?⑥닔 議댁옱 ?뺤씤
grep -n "best_score\|pos_weight\|finditer" briefing/scripts/post_process.py

# 以묐났 李⑤떒 ?덈룄??議댁옱 ?뺤씤
grep -n "_dedup_window\|deque" briefing/scripts/post_process.py

# 移댄뀒怨좊━???대?吏 ???뺤씤 (媛?12以??댁긽)
python -c "
import sys
sys.path.insert(0, 'briefing/scripts')
from post_process import CATEGORY_IMAGE_MAP
for k, v in CATEGORY_IMAGE_MAP.items():
    print(f'{k}: {len(v)}??)
"
```

---

*v3.3 ?ㅺ퀎 ?꾨즺 (2026-05-30). ?듭떖: detect_category ?ㅼ퐫?대쭅 援먯껜 + 以묐났 李⑤떒 ?덈룄??+ ?대?吏 ? 3諛??뺤옣.*

---

# CLCO_PRD.md ??4李??ы꽭??+ ?쒕㎤???대?吏 + ?쇱씠??紐⑤뱶 ?ㅺ퀎 (v3.4)

> **異붽? ?묒꽦**: ?댁퐫 (Cl-Co / ?ㅺ퀎??
> **湲곕컲**: ?덊떚 (Anti / 湲고쉷?? CLCO_HANDOFF.md 짠1~3 (4李??좉퇋)
> **?좎쭨**: 2026-05-30
> **?섏떊**: 肄붾뜳??(Codex / ?꾨Ц 肄붾뜑)

---

## ?ㅺ퀎 ?꾩젣 ??諛깆뿏???ㅽ궎留?怨좎젙 ?먯튃

| ?꾨뱶 | ?ㅼ젣 ?곗씠???뺤떇 | ??났??泥섎━ |
|---|---|---|
| `title` | `"湲곗궗A ?쒕ぉ \| 湲곗궗B ?쒕ぉ \| 湲곗궗C ?쒕ぉ"` | `\|` 遺꾪븷 ??媛쒕퀎 ?쒕ぉ 諛곗뿴 |
| `summary` | `"臾몄옣1. 臾몄옣2. 臾몄옣3. ..."` 以꾧? | `. ` 遺꾪븷 ??臾몄옣 諛곗뿴 ??鍮꾨? 留ㅽ븨 |

`briefings.json` ?ㅽ궎留덈뒗 ?덈? 蹂寃쏀븯吏 ?딆쓬. ?뚯떛? **100% ?대씪?댁뼵??JS**?먯꽌 泥섎━.

---

## A. ?ㅺ퀎 1 ???댁뒪 ?ы꽭 洹몃━???덉씠?꾩썐 (`index.html`)

### A-1. ?뚯떛 ?ы띁 ?⑥닔 (JS)

`renderLatest()` ?곷떒????媛쒖쓽 ?쒖닔 ?뚯떛 ?좏떥由ы떚瑜?癒쇱? ?뺤쓽?쒕떎.

```javascript
function parseTitles(rawTitle) {
    return rawTitle.split('|').map(t => t.trim()).filter(Boolean);
}

function parseSentences(rawSummary) {
    return rawSummary.split(/\.\s+/).map(s => s.trim()).filter(Boolean);
}

/**
 * 臾몄옣 諛곗뿴???쒕ぉ 媛쒖닔??鍮꾨? 遺꾨같?섏뿬 [{title, summary}, ...] 諛섑솚.
 * ?섎㉧吏 臾몄옣? 留덉?留??멸렇癒쇳듃??蹂묓빀. ?뺣낫 ?꾨씫 ?놁쓬.
 */
function buildSegments(titles, sentences) {
    const n = titles.length;
    if (n === 0) return [];
    if (sentences.length === 0) return titles.map(t => ({ title: t, summary: '' }));

    const perSlot   = Math.floor(sentences.length / n);
    const remainder = sentences.length % n;
    const segments  = [];
    let cursor = 0;

    titles.forEach((title, i) => {
        const count = perSlot + (i === n - 1 ? remainder : 0);
        const chunk = sentences.slice(cursor, cursor + count);
        segments.push({ title, summary: chunk.join('. ') + (chunk.length ? '.' : '') });
        cursor += count;
    });

    return segments;
}
```

### A-2. ?ы꽭 洹몃━??HTML ?쒗뵆由?(JS ??`renderLatest` ?꾩껜 援먯껜)

```javascript
function renderLatest(briefing) {
    const titles    = parseTitles(briefing.title);
    const sentences = parseSentences(briefing.summary);
    const segments  = buildSegments(titles, sentences);

    if (segments.length === 0) {
        document.getElementById('latest-container').innerHTML =
            '<div class="empty-state">釉뚮━?묒쓣 遺덈윭?????놁뒿?덈떎.</div>';
        return;
    }

    const baseLink = briefing._link || `archive/${briefing.date}.html`;
    const coverSrc = briefing.thumb_url
        ? briefing.thumb_url.replace('w=480','w=1200').replace('h=270','h=675')
        : '';
    const coverAlt = briefing.thumb_alt || '';

    // ?? Hero (1?쒖쐞) ??
    const hero = segments[0];
    const heroHTML = `
        <a href="${baseLink}" class="portal-hero">
            ${coverSrc ? `
            <div class="portal-hero-img">
                <img src="${coverSrc}" alt="${coverAlt}" loading="lazy" decoding="async">
                <div class="portal-hero-overlay"></div>
            </div>` : '<div class="portal-hero-no-img"></div>'}
            <div class="portal-hero-body">
                <div class="portal-meta">
                    <span class="portal-live-dot"></span>
                    <span class="portal-date">${briefing.date} KST</span>
                    <span class="portal-stats">${briefing.stats?.articles || 0} 湲곗궗</span>
                </div>
                <h2 class="portal-hero-title">${hero.title}</h2>
                ${hero.summary ? `<p class="portal-hero-summary">${hero.summary}</p>` : ''}
            </div>
        </a>`;

    // ?? Sub Grid (2~3?쒖쐞) ??
    const subs = segments.slice(1, 3);
    const subSrc = briefing.thumb_url
        ? briefing.thumb_url.replace('w=480','w=400').replace('h=270','h=225')
        : '';
    const subGridHTML = subs.length ? `
        <div class="portal-sub-grid">
            ${subs.map((seg, i) => `
            <a href="${baseLink}" class="portal-sub">
                ${subSrc ? `
                <div class="portal-sub-img">
                    <img src="${subSrc}" alt="${coverAlt}" loading="lazy" decoding="async">
                </div>` : ''}
                <div class="portal-sub-body">
                    <span class="portal-sub-index">${i + 2}</span>
                    <h3 class="portal-sub-title">${seg.title}</h3>
                    ${seg.summary ? `<p class="portal-sub-summary">${seg.summary}</p>` : ''}
                </div>
            </a>`).join('')}
        </div>` : '';

    // ?? More List (4?쒖쐞+) ??
    const moreItems = segments.slice(3);
    const moreHTML = moreItems.length ? `
        <ul class="portal-more-list">
            ${moreItems.map((seg, i) => `
            <li class="portal-more-item">
                <a href="${baseLink}">
                    <span class="portal-more-index">${i + 4}</span>
                    <span class="portal-more-title">${seg.title}</span>
                </a>
            </li>`).join('')}
        </ul>` : '';

    // ?? ?듦퀎 ?명꽣 ??
    const footerHTML = `
        <div class="portal-footer">
            <div class="portal-footer-stats">
                <span><strong>${briefing.stats?.articles || 0}</strong> 湲곗궗</span>
                <span><strong>${briefing.stats?.sections || 0}</strong> ?뱀뀡</span>
                ${briefing.stats?.picks ? `<span><strong>${briefing.stats.picks}</strong> Claude's Pick</span>` : ''}
            </div>
            <a href="${baseLink}" class="read-btn">?꾩껜 釉뚮━???쎄린 ??/a>
        </div>`;

    document.getElementById('latest-container').innerHTML = `
        <div class="portal-wrap">
            ${heroHTML}${subGridHTML}${moreHTML}${footerHTML}
        </div>`;
}
```

### A-3. ?ы꽭 洹몃━??CSS (`<style>` ?쒓렇 ?앹뿉 異붽?)

```css
/* ?? Portal Layout ???????????????????????????????????????? */
.portal-wrap {
    background: var(--bg-card);
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid var(--border-color);
}
.portal-hero {
    display: block; position: relative;
    text-decoration: none; color: inherit;
    min-height: 380px; overflow: hidden;
    transition: filter 0.2s ease;
}
.portal-hero:hover { filter: brightness(1.05); }
.portal-hero-img, .portal-hero-no-img {
    position: absolute; inset: 0;
    background: var(--bg-secondary);
}
.portal-hero-img img {
    width: 100%; height: 100%;
    object-fit: cover; object-position: center 40%; display: block;
}
.portal-hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(10,10,15,0.1) 0%, rgba(10,10,15,0.85) 100%);
}
.portal-hero-body {
    position: relative; padding: 2rem;
    height: 100%; display: flex; flex-direction: column; justify-content: flex-end;
}
.portal-meta { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem; }
.portal-live-dot {
    width: 8px; height: 8px; border-radius: 50%; background: var(--accent-red);
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.portal-date, .portal-stats {
    font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;
    color: rgba(255,255,255,0.75);
}
.portal-hero-title {
    font-size: 1.6rem; font-weight: 700; line-height: 1.3; color: #fff;
    text-shadow: 0 1px 4px rgba(0,0,0,0.6); margin-bottom: 0.75rem;
}
.portal-hero-summary {
    font-size: 0.9rem; color: rgba(255,255,255,0.8); line-height: 1.6;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}
.portal-sub-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 1px; background: var(--border-color);
    border-top: 1px solid var(--border-color);
}
.portal-sub {
    display: flex; flex-direction: column;
    text-decoration: none; color: inherit;
    background: var(--bg-card); overflow: hidden;
    transition: background 0.2s ease;
}
.portal-sub:hover { background: var(--bg-card-hover); }
.portal-sub-img { height: 130px; overflow: hidden; flex-shrink: 0; }
.portal-sub-img img {
    width: 100%; height: 100%; object-fit: cover; display: block;
    transition: transform 0.35s ease;
}
.portal-sub:hover .portal-sub-img img { transform: scale(1.05); }
.portal-sub-body { padding: 1rem 1.25rem; flex: 1; }
.portal-sub-index {
    display: inline-block; font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem; font-weight: 700; color: var(--accent-red);
    background: rgba(255,59,59,0.1);
    padding: 0.15rem 0.45rem; border-radius: 4px; margin-bottom: 0.5rem;
}
.portal-sub-title {
    font-size: 0.95rem; font-weight: 600; line-height: 1.4; color: var(--text-primary);
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden;
}
.portal-sub-summary {
    font-size: 0.8rem; color: var(--text-secondary);
    line-height: 1.5; margin-top: 0.4rem;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical; overflow: hidden;
}
.portal-more-list {
    list-style: none; border-top: 1px solid var(--border-color); padding: 0.5rem 0;
}
.portal-more-item { border-bottom: 1px solid var(--border-color); }
.portal-more-item:last-child { border-bottom: none; }
.portal-more-item a {
    display: flex; align-items: baseline; gap: 0.75rem;
    padding: 0.7rem 1.5rem; text-decoration: none; color: inherit;
    transition: background 0.15s ease;
}
.portal-more-item a:hover { background: var(--bg-card-hover); }
.portal-more-index {
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    font-weight: 700; color: var(--text-muted); flex-shrink: 0; width: 1.2rem;
}
.portal-more-title {
    font-size: 0.875rem; font-weight: 500; color: var(--text-secondary); line-height: 1.4;
}
.portal-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.5rem; border-top: 1px solid var(--border-color);
    background: var(--bg-secondary);
}
.portal-footer-stats { display: flex; gap: 1.25rem; font-size: 0.82rem; color: var(--text-muted); }
.portal-footer-stats strong { color: var(--text-secondary); }
@media (max-width: 768px) {
    .portal-hero { min-height: 260px; }
    .portal-hero-title { font-size: 1.2rem; }
    .portal-sub-grid { grid-template-columns: 1fr; }
    .portal-sub-img { height: 100px; }
    .portal-footer { flex-direction: column; gap: 0.75rem; }
}
@media (max-width: 480px) {
    .portal-hero-body { padding: 1.25rem; }
    .portal-hero-title { font-size: 1.05rem; }
}
```

---

## B. ?ㅺ퀎 2 ???쒕㎤???대?吏 誘몄꽭 ?쒓렇 留ㅼ묶 (`post_process.py`)

### B-1. `_img()` ?ы띁 ?쒓렇?덉쿂 ?뺤옣

```python
def _img(photo_id, alt, credit_name, tags=None):
    """tags: ?대?吏 ?곌? ?곷Ц ?뚮Ц???ㅼ썙??由ъ뒪??(5~10媛?沅뚯옣)."""
    return {
        "id":          photo_id,
        "alt":         alt,
        "credit_name": credit_name,
        "credit_url":  f"https://unsplash.com/photos/{photo_id}",
        "tags":        [t.lower() for t in (tags or [])],
    }
```

### B-2. `smart_pick_image()` ?좉퇋 ?⑥닔 (`select_from_pool` 諛붾줈 ?꾩뿉 異붽?)

```python
def smart_pick_image(pool: list, article_text: str) -> dict | None:
    """
    ? ???대?吏 tags? 湲곗궗 ?띿뒪???ㅼ썙??留ㅼ묶 鍮덈룄濡?理쒖쟻 ?대?吏 ?좊컻.
    留ㅼ묶 ?놁쑝硫?None 諛섑솚 ??caller媛 hash+dedup fallback ?ъ슜.
    """
    text_lower = article_text.lower()
    best_img, best_score = None, 0

    for img in pool:
        score = sum(1 for tag in img.get("tags", []) if tag in text_lower)
        if score > best_score:
            best_score = score
            best_img   = img

    if best_img and best_score > 0:
        _dedup_window.append(best_img["id"])
        return best_img

    return None
```

### B-3. `resolve_image()` ?섏젙 ??Smart Pick ?곗꽑 ?곸슜

```python
def resolve_image(soup, title, date_str, summary):
    article_text = title + " " + summary

    # Priority 1: 湲곗궗 蹂몃Ц ?대?吏
    art = find_article_image(soup)
    if art:
        return art, "article_image"

    # Priority 2: 移댄뀒怨좊━ ?먯?
    cat = detect_category(title, summary)
    if cat and cat in CATEGORY_IMAGE_MAP:
        pool = CATEGORY_IMAGE_MAP[cat]

        # Priority 2-A: ?쒕㎤???쒓렇 Smart Pick
        smart = smart_pick_image(pool, article_text)
        if smart:
            return smart, "smart_pick"

        # Priority 2-B: Hash + Dedup Fallback
        img = select_from_pool(pool, title, date_str)
        return img, "handpick_category"

    # Priority 3: Default Pool
    img = select_from_pool(DEFAULT_IMAGE_POOL, title, date_str)
    return img, "handpick_default"
```

### B-4. `CATEGORY_IMAGE_MAP` 24???뺤옣 援ъ“ (ai + space ?꾩쟾 ?덉떆)

> ?섎㉧吏 10媛?移댄뀒怨좊━???숈씪 ?⑦꽩?쇰줈 Codex媛 tags 遺?ы븯硫?24?μ쑝濡??뺤옣.

```python
CATEGORY_IMAGE_MAP = {

    "ai": [
        _img("1677442135703-1787eea5ce01", "Blue neural network visualization",     "Growtika",
             tags=["neural", "network", "ai", "data", "blue", "visualization"]),
        _img("1620712943543-bcc4688e7485", "Cybernetic virtual brain circuits",      "Possessed Photography",
             tags=["brain", "cybernetic", "ai", "robot", "humanoid", "mind"]),
        _img("1526374965328-7f61d4dc18c5", "Matrix binary code wall dark screen",   "Markus Spiske",
             tags=["code", "matrix", "binary", "hacking", "programming", "screen"]),
        _img("1507146426996-ef05306b995a", "Neon glowing abstract tech lines",       "Alina Grubnyak",
             tags=["neon", "abstract", "digital", "glow", "network", "lines"]),
        _img("1555066931-4365d14bab8c",    "Green matrix code rain screen",          "Markus Spiske",
             tags=["matrix", "code", "green", "hacking", "dark", "screen"]),
        _img("1485827404703-89b55fcc595e", "Robot hand touching digital interface",  "Alex Knight",
             tags=["robot", "hand", "touch", "interface", "ai", "finger"]),
        _img("1526378722484-bd91ca387e72", "Glowing robotic hand digital screen",    "Franck V.",
             tags=["robot", "glowing", "hand", "screen", "future", "digital"]),
        _img("1676299170-e7a43f29e74a",    "Abstract AI data processing art",        "Growtika",
             tags=["data", "processing", "abstract", "ai", "compute", "llm"]),
        _img("1675557009483-b2f86c2cb790", "AI circuit board glowing blue light",    "Growtika",
             tags=["circuit", "board", "blue", "glow", "chip", "hardware", "ai"]),
        _img("1664575261772-68bec93ea1a9", "Machine learning algorithm visual",      "Growtika",
             tags=["machine", "learning", "algorithm", "llm", "training", "model"]),
        _img("1531297484001-80022131f5a1", "Premium laptop display dark setup",      "Ales Nesetril",
             tags=["laptop", "coding", "developer", "dark", "screen", "software"]),
        _img("1580927752452-89d86da3fa0a", "Developer coding laptop dark room",      "Christopher Gower",
             tags=["coding", "developer", "programming", "dark", "laptop", "software"]),
        # Codex: 異붽? 12??(?숈씪 tags ?⑦꽩) ?????????????????
    ],

    "space": [
        _img("1451187580459-43490279c0fa", "Blue Earth from dark outer space",       "NASA",
             tags=["earth", "orbit", "planet", "space", "globe", "blue", "nasa"]),
        _img("1506703719100-a0f3a48c0f86", "Aurora borealis deep space nebula",      "Greg Rakozy",
             tags=["aurora", "nebula", "stars", "galaxy", "night", "space", "sky"]),
        _img("1446776811953-b23d57bd21aa", "Space station solar panels orbit",       "NASA",
             tags=["space station", "iss", "solar", "orbit", "nasa", "satellite"]),
        _img("1541185933-ef5d8ed016c2",    "Rocket launch trajectory night sky",     "SpaceX",
             tags=["rocket", "launch", "fire", "spacex", "night", "liftoff", "flame"]),
        _img("1454789548928-701522940945", "Milky Way galaxy stars landscape",       "Greg Rakozy",
             tags=["milky way", "galaxy", "stars", "landscape", "night sky", "cosmos"]),
        _img("1614730321146-b6fa6a46bcb4", "Deep space nebula colorful gas clouds", "Jeremy Thomas",
             tags=["nebula", "gas", "clouds", "colorful", "deep space", "cosmos"]),
        _img("1516849841032-87cbac4d88f7", "Rocket launching bright exhaust flame",  "SpaceX",
             tags=["rocket", "launch", "exhaust", "flame", "liftoff", "spacex", "fire"]),
        _img("1462331940025-346fe2b70cd0", "Earth globe from space blue clouds",     "NASA",
             tags=["earth", "globe", "blue", "clouds", "space", "planet", "nasa"]),
        _img("1419242902214-272b3f66ee7a", "Satellite view city lights night",       "NASA",
             tags=["satellite", "city lights", "night", "aerial", "view", "orbit"]),
        _img("1540198163009-7afbf6bf31b6", "Night sky milky way long exposure",      "Jeremy Thomas",
             tags=["night sky", "milky way", "exposure", "stars", "dark", "cosmos"]),
        _img("1586348943529-beaae6c28db9", "Space rocket launch control room",       "SpaceX",
             tags=["control room", "launch", "spacex", "mission", "rocket", "nasa"]),
        _img("1614064641938-2959af8dc0a6", "Starlink satellite constellation orbit", "SpaceX",
             tags=["starlink", "satellite", "constellation", "orbit", "spacex", "network"]),
        # Codex: 異붽? 12??(?숈씪 tags ?⑦꽩) ?????????????????
    ],

    # chip, finance, robot, health, ev, economy, telecom, bigtech, policy, defense:
    # v3.3 湲곗〈 ?대?吏 ?좎? + tags 諛곗뿴 遺??+ 媛?24?μ쑝濡??뺤옣
}
```

---

## C. ?ㅺ퀎 3 ???대옒??醫낆씠 紐⑤뱶 ?쇱씠???뚮쭏 ?좉?

### C-1. ?쇱씠???뚮쭏 CSS 蹂??(`index.html` + `archive.html` `<style>` 異붽?)

```css
/* ?? Classic Paper Mode (Light Theme) ???????????????????? */
body.light-mode {
    --bg-primary:     #faf8f3;
    --bg-secondary:   #f0ede5;
    --bg-card:        #ffffff;
    --bg-card-hover:  #f5f2ea;
    --text-primary:   #1c1c1e;
    --text-secondary: #44444f;
    --text-muted:     #8a8a9a;
    --border-color:   #dedad2;
    --accent-red:     #d62d2d;
    --accent-blue:    #1a6fc4;
    --accent-gold:    #b8860b;
    --gradient-fire:  linear-gradient(135deg, #d62d2d, #c9600a);
    --gradient-ai:    linear-gradient(135deg, #7c3aed, #1a6fc4);
}
body.light-mode .nav {
    background: rgba(250, 248, 243, 0.92);
    border-bottom-color: var(--border-color);
}
/* Hero ?대?吏 ???띿뒪?몃뒗 ?쇱씠??紐⑤뱶?먯꽌???곗깋 ?좎? */
body.light-mode .portal-hero-title { color: #ffffff; }
body.light-mode .portal-date,
body.light-mode .portal-stats { color: rgba(255,255,255,0.8); }

/* ?됱긽 ?꾪솚 ?몃옖吏??*/
body, .nav, .portal-wrap, .portal-sub,
.portal-footer, .portal-more-list {
    transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}
```

### C-2. GNB ?좉? 踰꾪듉 HTML (???섏씠吏 4媛???`<ul class="nav-links">` 諛붾줈 ?욎뿉 ?쎌엯)

```html
<button id="theme-toggle" class="theme-toggle-btn"
        onclick="toggleTheme()" aria-label="?뚮쭏 ?꾪솚">?뙔</button>
```

```css
.theme-toggle-btn {
    background: rgba(255,255,255,0.07);
    border: 1px solid var(--border-color);
    border-radius: 8px; padding: 0.35rem 0.6rem;
    font-size: 1rem; cursor: pointer; line-height: 1;
    transition: background 0.2s ease, transform 0.15s ease;
}
.theme-toggle-btn:hover {
    background: rgba(255,255,255,0.14); transform: scale(1.1);
}
body.light-mode .theme-toggle-btn {
    background: rgba(0,0,0,0.06); border-color: var(--border-color);
}
```

### C-3. ?뚮쭏 ?꾪솚 JS (???섏씠吏 4媛?`<script>` 理쒖긽?⑥뿉 異붽?)

```javascript
(function initTheme() {
    if (localStorage.getItem('jfnb-theme') === 'light') {
        document.body.classList.add('light-mode');
        document.addEventListener('DOMContentLoaded', function() {
            var btn = document.getElementById('theme-toggle');
            if (btn) btn.textContent = '?截?;
        });
    }
})();

function toggleTheme() {
    var isLight = document.body.classList.toggle('light-mode');
    localStorage.setItem('jfnb-theme', isLight ? 'light' : 'dark');
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = isLight ? '?截? : '?뙔';
}
```

> **?곸슜 踰붿쐞**: `index.html`, `archive.html`, `about.html`, `search.html` 4媛쒕쭔.
> `archive/*.html` 湲곗궗 ?뚯씪: ?ㅽ겕 ?곴뎄 怨좎닔 ????肄붾뱶 **?쎌엯 湲덉?**.

---

## D. 援ы쁽 泥댄겕由ъ뒪??(v3.4)

### Phase 1 ??`index.html` ?ы꽭 洹몃━??
- [ ] `parseTitles()`, `parseSentences()`, `buildSegments()` ?⑥닔 異붽?
- [ ] `renderLatest()` ?꾩껜 援먯껜 (A-2 肄붾뱶)
- [ ] A-3 CSS 釉붾줉 `<style>` ?앹뿉 異붽?
- [ ] ?뚯씠???ы븿 title ??Hero + Sub Grid + More List ?뺤긽 遺꾪븷 ?뺤씤
- [ ] ?뚯씠???녿뒗 ?⑥씪 title ??Hero 移대뱶留??⑤룆 ?쒖떆
- [ ] 紐⑤컮??375px ???⑥씪 ???덉씠?꾩썐 ?뺤씤

### Phase 2 ??`post_process.py` ?쒕㎤??留ㅼ묶
- [ ] `_img()` ?ы띁??`tags=None` ?뚮씪誘명꽣 異붽?
- [ ] `smart_pick_image()` ?⑥닔 異붽?
- [ ] `resolve_image()` Smart Pick ?곗꽑 ?곸슜?쇰줈 ?섏젙
- [ ] ?꾩껜 `CATEGORY_IMAGE_MAP` tags 遺??+ 24?μ쑝濡??뺤옣
- [ ] `python briefing/scripts/post_process.py` ??`src=smart_pick` 濡쒓렇 ?뺤씤

### Phase 3 ???쇱씠??紐⑤뱶 ?좉? (??4媛??뚯씪)
- [ ] `index.html`, `archive.html`, `about.html`, `search.html` ??CSS + 踰꾪듉 + JS 異붽?
- [ ] `archive/*.html` 湲곗궗 ?뚯씪???쇱씠??紐⑤뱶 肄붾뱶 ?놁쓬 ?뺤씤
- [ ] ?뙔 ?대┃ ??誘몄깋 ?쇱씠???뚮쭏, ?截?踰꾪듉 蹂寃?
- [ ] ?截??대┃ ???ㅽ겕 蹂듦?, ?뙔 踰꾪듉 蹂듦?
- [ ] ?덈줈怨좎묠 ???댁쟾 ?뚮쭏 ?좎? ?뺤씤

---

## E. 寃??紐낅졊??

```bash
grep -n "parseTitles\|buildSegments\|portal-hero\|portal-sub-grid" briefing/index.html
grep -n "smart_pick_image\|tags=\[" briefing/scripts/post_process.py
grep -n "light-mode\|jfnb-theme\|theme-toggle" briefing/index.html briefing/archive.html
```

---

*v3.4 ?ㅺ퀎 ?꾨즺 (2026-05-30). 3?몃옓: ?ы꽭 ?뚯꽌 ?덉씠?꾩썐 + ?쒕㎤??Smart Pick + ?대옒??醫낆씠 紐⑤뱶 ?좉?.*


---

# CLCO_PRD.md — 5차 포털 리디자인 + 세그먼트 고유 이미지 주입 (v3.5)

> **추가 작성**: 클코 (Cl-Co / 설계자)
> **기반**: 안티 (Anti / 기획자) CLCO_HANDOFF.md 5차 긴급
> **날짜**: 2026-05-31
> **수신**: 코덱스 (Codex / 전문 코더)

---

## 현황 진단

| 버그/문제 | 원인 | 해결 방향 |
|---|---|---|
| Hero 배경 이미지 위에 글씨 겹쳐 가독성 저하 | overlay형 레이아웃 | 좌측 이미지 + 우측 텍스트 2분할 grid |
| 서브 카드 폰트 작음 | 0.95rem/0.8rem | 1.15rem/0.93rem으로 확대 |
| 3개 카드 모두 동일한 우주 이미지 | subSrc = briefing.thumb_url 단일 소스 | 세그먼트별 빌드타임 이미지 독립 매칭 |

---

## A. CSS 교체 — Hero 2분할 그리드 + 서브 폰트 확대

### A-1. .portal-hero 관련 규칙 전면 교체

**교체 전 (찾을 코드 블록):**
```css
.portal-hero {
    display: block;
    position: relative;
    text-decoration: none;
    color: inherit;
    min-height: 380px;
    overflow: hidden;
    transition: filter 0.2s ease;
}
.portal-hero:hover { filter: brightness(1.05); }
.portal-hero-img,
.portal-hero-no-img {
    position: absolute;
    inset: 0;
    background: var(--bg-secondary);
}
.portal-hero-img img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 40%;
    display: block;
}
.portal-hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(10,10,15,0.1) 0%, rgba(10,10,15,0.85) 100%);
}
.portal-hero-body {
    position: relative;
    padding: 2rem;
    min-height: 380px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    min-width: 0;
}
```

**교체 후 (붙여넣을 코드 블록):**
```css
.portal-hero {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    min-height: 340px;
    text-decoration: none;
    color: inherit;
    transition: box-shadow 0.25s ease;
    overflow: hidden;
}
.portal-hero:hover {
    box-shadow: inset 0 0 0 2px rgba(255, 59, 59, 0.5);
}
.portal-hero-img {
    position: relative;
    overflow: hidden;
    background: var(--bg-secondary);
    min-height: 280px;
}
.portal-hero-no-img {
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
    min-height: 280px;
}
.portal-hero-img img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    display: block;
    transition: transform 0.4s ease;
}
.portal-hero:hover .portal-hero-img img {
    transform: scale(1.04);
}
.portal-hero-overlay { display: none; }
.portal-hero-body {
    padding: 2rem 1.75rem;
    background: var(--bg-card);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0;
    min-width: 0;
    border-left: 1px solid var(--border-color);
}
```

### A-2. .portal-date / .portal-stats 색상 교체

```css
/* 교체 후 */
.portal-date,
.portal-stats {
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-muted);
}
```

### A-3. .portal-hero-title 교체

```css
/* 교체 후 */
.portal-hero-title {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.35;
    color: var(--text-primary);
    text-shadow: none;
    margin-bottom: 0.75rem;
    overflow-wrap: anywhere;
    word-break: keep-all;
}
```

### A-4. .portal-hero-summary 교체

```css
/* 교체 후 */
.portal-hero-summary {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.6;
    overflow-wrap: anywhere;
    word-break: keep-all;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

### A-5. .portal-sub-title / .portal-sub-summary 폰트 확대 교체

```css
/* 교체 후 */
.portal-sub-title {
    font-size: 1.15rem;
    font-weight: 600;
    line-height: 1.4;
    color: var(--text-primary);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.portal-sub-summary {
    font-size: 0.93rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-top: 0.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
```

### A-6. 모바일 반응형 교체 (@media max-width: 768px 내부)

```css
/* 교체 후 */
    .portal-hero {
        grid-template-columns: 1fr;
        grid-template-rows: 220px auto;
        min-height: unset;
    }
    .portal-hero-body {
        border-left: none;
        border-top: 1px solid var(--border-color);
        padding: 1.25rem;
        justify-content: flex-start;
    }
    .portal-hero-title { font-size: 1.15rem; }
```

### A-7. 라이트 모드 hero 색상 override 삭제

아래 2개 규칙을 삭제한다 (CSS vars 자동 대응으로 불필요):
```css
body.light-mode .portal-hero-title { color: #ffffff; }
body.light-mode .portal-date,
body.light-mode .portal-stats { color: rgba(255,255,255,0.8); }
```

---

## B. renderLatest() JS 전체 교체 (index.html)

```javascript
function renderLatest(briefing) {
    const baseLink = briefing._link || `archive/${briefing.date}.html`;

    // 세그먼트 소스: JSON 우선, 클라이언트 파싱 폴백
    let segments;
    if (briefing.segments && briefing.segments.length > 0) {
        segments = briefing.segments;
    } else {
        const titles    = parseTitles(briefing.title);
        const sentences = parseSentences(briefing.summary);
        const baseSegs  = buildSegments(titles, sentences);
        const fallbackThumb = briefing.thumb_url || '';
        const fallbackAlt   = briefing.thumb_alt  || '';
        segments = baseSegs.map(seg => ({
            ...seg,
            thumb_url:  fallbackThumb,
            thumb_alt:  fallbackAlt,
        }));
    }

    if (segments.length === 0) {
        document.getElementById('latest-container').innerHTML =
            '<div class="empty-state">표시할 브리핑이 없습니다.</div>';
        return;
    }

    const hero    = segments[0];
    const heroSrc = hero.thumb_url
        ? hero.thumb_url.replace('w=480', 'w=700').replace('h=270', 'h=525')
        : '';
    const heroAlt = hero.thumb_alt || '';

    const heroHTML = `
        <a href="${baseLink}" class="portal-hero">
            ${heroSrc
                ? `<div class="portal-hero-img">
                       <img src="${heroSrc}" alt="${heroAlt}" loading="lazy" decoding="async">
                   </div>`
                : '<div class="portal-hero-no-img"></div>'}
            <div class="portal-hero-body">
                <div class="portal-meta">
                    <span class="portal-live-dot"></span>
                    <span class="portal-date">${briefing.date} KST</span>
                    <span class="portal-stats">${briefing.stats?.articles || briefing.stats?.clusters || 0} 건</span>
                </div>
                <h2 class="portal-hero-title">${hero.title}</h2>
                ${hero.summary ? `<p class="portal-hero-summary">${hero.summary}</p>` : ''}
                <a href="${baseLink}" class="read-btn" style="margin-top:1.25rem;display:inline-block;">브리핑 읽기 →</a>
            </div>
        </a>`;

    const subs = segments.slice(1, 3);
    const subGridHTML = subs.length ? `
        <div class="portal-sub-grid">
            ${subs.map((seg, i) => `
            <a href="${baseLink}" class="portal-sub">
                ${seg.thumb_url ? `
                <div class="portal-sub-img">
                    <img src="${seg.thumb_url}" alt="${seg.thumb_alt || ''}" loading="lazy" decoding="async">
                </div>` : ''}
                <div class="portal-sub-body">
                    <span class="portal-sub-index">${i + 2}</span>
                    <h3 class="portal-sub-title">${seg.title}</h3>
                    ${seg.summary ? `<p class="portal-sub-summary">${seg.summary}</p>` : ''}
                </div>
            </a>`).join('')}
        </div>` : '';

    const moreItems = segments.slice(3);
    const moreHTML = moreItems.length ? `
        <ul class="portal-more-list">
            ${moreItems.map((seg, i) => `
            <li class="portal-more-item">
                <a href="${baseLink}">
                    <span class="portal-more-index">${i + 4}</span>
                    <span class="portal-more-title">${seg.title}</span>
                </a>
            </li>`).join('')}
        </ul>` : '';

    const footerHTML = `
        <div class="portal-footer">
            <div class="portal-footer-stats">
                <span><strong>${briefing.stats?.articles || briefing.stats?.clusters || 0}</strong> 건</span>
                <span><strong>${briefing.stats?.sections || briefing.stats?.clusters || 0}</strong> 섹션</span>
                ${briefing.stats?.picks ? `<span><strong>${briefing.stats.picks}</strong> Claude's Pick</span>` : ''}
            </div>
            <a href="${baseLink}" class="read-btn">전체 읽기 →</a>
        </div>`;

    document.getElementById('latest-container').innerHTML = `
        <div class="portal-wrap">
            ${heroHTML}${subGridHTML}${moreHTML}${footerHTML}
        </div>`;
}
```

---

## C. post_process.py 확장 — 세그먼트별 빌드타임 이미지 주입

### C-1. 파싱 헬퍼 2개 추가 (detect_category 바로 위에 추가)

```python
def parse_title_segments(raw_title: str) -> list:
    """파이프(|) 분할 -> 개별 기사 제목 리스트."""
    return [t.strip() for t in raw_title.split('|') if t.strip()]


def parse_summary_sentences(raw_summary: str) -> list:
    """마침표+공백 분할 -> 문장 리스트."""
    return [s.strip() for s in re.split(r'\.\s+', raw_summary) if s.strip()]
```

### C-2. build_segments_with_images() 추가 (_process_list 바로 위에 추가)

```python
def build_segments_with_images(raw_title: str, raw_summary: str, date_str: str) -> list:
    """
    타이틀 파이프 분할 + 요약 비례 배분 + 세그먼트별 독립 이미지 매칭.
    반환: [{title, summary, thumb_url, thumb_url_xs, thumb_alt, thumb_category}, ...]
    """
    titles    = parse_title_segments(raw_title)
    sentences = parse_summary_sentences(raw_summary)

    if not titles:
        return []

    n        = len(titles)
    per_slot = len(sentences) // n if sentences else 0
    remain   = len(sentences) % n  if sentences else 0
    segments = []
    cursor   = 0

    for i, title in enumerate(titles):
        count   = per_slot + (remain if i == n - 1 else 0)
        chunk   = sentences[cursor:cursor + count]
        summary = '. '.join(chunk) + ('.' if chunk else '')
        cursor += count

        cat = detect_category(title, summary)

        if cat and cat in CATEGORY_IMAGE_MAP:
            pool     = CATEGORY_IMAGE_MAP[cat]
            smart    = smart_pick_image(pool, title + " " + summary)
            img_meta = smart if smart else select_from_pool(pool, title, date_str)
        else:
            img_meta = select_from_pool(DEFAULT_IMAGE_POOL, title, date_str)
            cat = "default"

        urls = make_urls(img_meta)
        segments.append({
            "title":          title,
            "summary":        summary,
            "thumb_url":      urls["thumb_url"],
            "thumb_url_xs":   urls["thumb_url_xs"],
            "thumb_alt":      img_meta.get("alt", ""),
            "thumb_category": cat or "default",
        })

    return segments
```

### C-3. _process_list() 수정 — item.update(meta) 줄 바로 다음에 추가

```python
        # 기존 코드
        meta = process_article(html_path, item)
        item.update(meta)

        # 아래 추가
        item.pop("segments", None)
        raw_title   = item.get("title",   "")
        raw_summary = item.get("summary", "")
        segs = build_segments_with_images(raw_title, raw_summary, date)
        if segs:
            item["segments"] = segs
        print(f"  -> {len(segs)} segments: {[s['thumb_category'] for s in segs]}")
```

---

## D. 구현 체크리스트 (v3.5)

### Phase 1 — CSS 교체 (index.html)
- [ ] A-1: .portal-hero 블록 -> 2분할 grid 버전 교체
- [ ] A-2: .portal-date/.portal-stats -> var(--text-muted) 교체
- [ ] A-3: .portal-hero-title -> var(--text-primary); text-shadow: none 교체
- [ ] A-4: .portal-hero-summary -> var(--text-secondary); -webkit-line-clamp: 4 교체
- [ ] A-5: .portal-sub-title 1.15rem / .portal-sub-summary 0.93rem 교체
- [ ] A-6: @media 768px hero 반응형 세로 스택 교체
- [ ] A-7: body.light-mode .portal-hero-title { color: #ffffff; } 등 2줄 삭제

### Phase 2 — JS 교체 (index.html)
- [ ] renderLatest() 함수 전체를 B 코드로 교체
- [ ] parseTitles, parseSentences, buildSegments 헬퍼 함수는 폴백으로 유지

### Phase 3 — post_process.py 확장
- [ ] parse_title_segments() 추가
- [ ] parse_summary_sentences() 추가
- [ ] build_segments_with_images() 추가
- [ ] _process_list() 내 세그먼트 빌드 코드 추가
- [ ] python briefing/scripts/post_process.py 실행
- [ ] 로그에서 -> N segments: ['space', 'chip', 'economy'] 확인
- [ ] briefings.json 최신 항목에 segments 배열 존재 확인

---

## E. 검수 명령어

```bash
grep -n "grid-template-columns: 1.2fr" briefing/index.html
grep -n "font-size: 1.15rem" briefing/index.html
grep -n "build_segments_with_images\|parse_title_segments" briefing/scripts/post_process.py
```

시각적 검증:
- Hero 좌측 이미지 | 우측 텍스트 명확 분할
- Sub 카드 1, 2: 서로 다른 이미지 (동일 이미지 없음)
- Hero + Sub 1 + Sub 2: 3개 모두 다른 이미지
- 모바일 375px: 상단 이미지 + 하단 텍스트 세로 스택
- 라이트 모드: Hero 우측 텍스트 밝은 배경 자연스럽게 전환

---

*v3.5 설계 완료 (2026-05-31). 핵심: Hero 2분할 그리드 + 세그먼트별 빌드타임 고유 이미지 주입 아키텍처.*
