# 🤝 [2차 지시 - 안티 ➡️ 클코] PWA 완전 제거 및 리드와이즈 리더 테마 설계 요청서

수신: **클코 (Cl-Co / 설계자)**
발신: **안티 (Anti / 계획자)**
날짜: 2026-05-27
버전: **v2.0 (피드백 반영)**

유저의 긴급 피드백을 반영하여 설계 방향을 전면 수정합니다.

현재 캐시 충돌 및 웹 성능 혼선을 일으키는 **PWA(Progressive Web App)를 아예 전면 제거**하고, 롤백 상태인 워크스페이스에 **'리드와이즈 리더(Readwise Reader)'** 테마를 가장 완벽하고 충돌 없는 방식으로 재설계해 주시기 바랍니다.

---

## 🛠️ 클코 2차 설계 핵심 요구사항

### 1. PWA 완전 제거 (PWA Strip & Unregister)
* **파일 삭제 명세**:
  - `manifest.json` [DELETE]
  - `sw.js` [DELETE]
* **HTML 소스 정리**:
  - `index.html`, `archive.html`, `about.html`, `search.html` 내부에 존재하는 `<link rel="manifest"...>`, `<meta name="theme-color"...>` 등 PWA 관련 메타 태그를 전부 제거합니다.
  - 기존 서비스 워커를 등록하는 자바스크립트 블록(`if ('serviceWorker' in navigator) { ... }`)을 완전히 삭제합니다.
* **클라이언트 강제 캐시 제거 스크립트 설계**:
  - 이미 기존 서비스 워커가 브라우저에 등록된 방문자들의 캐시 충돌을 막기 위해, 메인 페이지 로드 시 기존 등록된 서비스 워커를 **강제로 등록 해제(Unregister)**하는 안전 스크립트를 설계해 주세요:
    ```javascript
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(function(registrations) {
            for(let registration of registrations) {
                registration.unregister();
            }
        });
    }
    ```

### 2. 스타일 격리 및 타이포그래피 재설계
* ** theme-modern.css 격리 설계**:
  - 기사 본문 페이지(`archive/*.html`)의 원래 본문 스타일이 깨지는 것을 막기 위해 `body.reader-mode` 하위 선택자 네임스페이스 격리 구조를 엄격하게 설계합니다.
  - 셸 페이지(`index.html`, `archive.html`, `about.html`)는 `body.shell-page` 네임스페이스를 사용하여 기존 레이아웃이 무너지지 않도록 조율합니다.
* **가독성 사양**: Coal Dark 테마 컬러(#121214), 680px 본문폭 정렬, Noto Sans KR + Outfit 가독성 폰트 매핑.

### 3. 고화질 헤더 이미지 자동 연동 파이프라인
* `scripts/post_process.py` 후처리기 설계: 기사 제목을 분석해 Unsplash Free API를 호출하는 로직 및 기사 내에 업로드된 이미지를 1순위로 자동 승격시키는 하이브리드 알고리즘 설계.

---

## 🏁 아웃풋 파일 생성 요청
* 설계를 마치면 프로젝트 루트 디렉토리에 **`CLCO_PRD.md`** 파일명으로 PWA 제거 및 스타일 개편에 관한 아키텍처 최종 사양을 작성해 주세요.
* 작성이 완료되면 유저님이 그 설계도를 전문 코더인 **코덱스(Codex)**에게 전달할 수 있도록 친절히 보고해 주시기 바랍니다.

---

# 🤝 [3차 지시 - 안티 ➡️ 클코] 메인 화면 개선 및 GNB 네비게이션 일관성 확보 요청서

수신: **클코 (Cl-Co / 설계자)**
발신: **안티 (Anti / 계획자)**
날짜: 2026-05-30
버전: **v3.0 (신규 피드백 반영)**

유저님의 최신 피드백을 수렴하여 메인 화면의 레이아웃 단순화 및 GNB의 사용성 오류 수정을 위한 설계와 리팩토링을 요청합니다. 다음 세 가지 핵심 항목에 맞춰 정밀하게 재설계해 주세요.

---

## 🛠️ 클코 3차 설계 핵심 요구사항

### 1. `Essential NEWS` 영역 전면 제거 및 최신 브리핑의 'Hero'화
* **수정 대상**: `index.html` 및 관련 스타일
* **작업 가이드**:
  - `index.html` 상단의 불필요한 히어로 영역(`<section class="hero"><h1>Essential NEWS</h1></section>`)을 완전히 제거합니다.
  - 최신 브리핑 영역(`section.latest`)이 네비게이션 바로 아래에 밀착하도록 여백(Padding/Margin)을 조정해 주세요.
  - `renderLatest` 함수가 랜더링하는 최신 브리핑 카드(`.latest-card`)의 커버 썸네일 해상도 매개변수를 기존 `w=800`에서 16:9 메인 비율에 맞춰 `w=1200`, `h=675` 또는 `fit=crop`에 최적화된 URL로 연계해 프리미엄 커버 비주얼을 만들어 줍니다.
  - 최신 브리핑이 메인의 압도적인 Hero 대접을 받도록 호버 트랜지션 및 보더 라이팅 효과를 세련되게 다듬어 주세요.

### 2. 좌측 상단 로고 일관화 (`JFNB`) 및 홈 링크 경로 검증
* **수정 대상**: `index.html`, `archive.html`, `about.html`, `search.html`
* **작업 가이드**:
  - 현재 아카이브(`archive.html`) 및 소개(`about.html`) 페이지의 좌측 상단 로고명이 `Jae's Briefing` 등으로 불일치합니다. 이를 **`JFNB`**로 전면 일괄 통일해 주세요.
  - 로고 클릭 시 홈 화면(`index.html`)으로 매끄럽고 일관되게 이동할 수 있도록 GNB HTML 마크업의 href를 교정해 주세요.

### 3. GNB '홈' 링크의 새 탭 열림 방지 및 정상 연결
* **수정 대상**: `index.html`, `archive.html`, `about.html`, `search.html` 및 `scripts/post_process.py` 내 `GNB_HTML`
* **작업 가이드**:
  - 우상단 GNB 메뉴 중 '홈' 링크 클릭 시 새로운 브라우저 탭이 불필요하게 활성화되는 현상이 있습니다.
  - 각 HTML 문서의 GNB 영역 및 `post_process.py` 내부의 `GNB_HTML` 상수 내에 `target="_blank"` 속성이 존재하는지 철저히 전수 조사하여 제거해 주세요.
  - 사용자가 자연스럽게 동일 탭에서 홈 화면으로 이동할 수 있게 보장합니다.

### 4. 주간 브리핑 및 특별판 상세페이지 GNB/푸터 완전 누락 버그 해결
* **수정 대상**: `scripts/post_process.py`의 `main()` 함수 리팩토링 및 관련 파이프라인
* **작업 가이드**:
  - 주간 브리핑(`archive/weekly-*.html`) 및 특별판 상세페이지 진입 시 상단 GNB와 하단 푸터가 아예 사라지는 치명적 사용성 버그가 발생하고 있습니다.
  - 원인은 `post_process.py` 내 `main()` 함수가 `briefings.json`에 담긴 일일 브리핑 리스트(`data["briefings"]`)만 반복해서 후처리(`process_article`)하고 있기 때문입니다.
  - `data["weekly"]`와 `data["specials"]`에 해당하는 주간 및 특별판 상세 HTML 파일들에 대해서도 루프를 적용하여 `process_article`이 강제 호출되도록 파이프라인을 확장 설계해 주세요.
  - 이를 통해 모든 유형의 브리핑 상세 페이지에 `JFNB` 로고 및 '홈/아카이브/소개' 메뉴 바와 푸터가 일관되게 주입되도록 설계합니다.

---

## 🏁 아웃풋 파일 생성 및 다음 단계 요청
* 설계를 마친 뒤 **`CLCO_PRD.md`**에 이 3차 개편안에 대한 기술 명세를 보완해 주시기 바랍니다.
* 작업 완료 후 유저님이 코더인 **코덱스(Codex)**에게 이 사양을 넘길 수 있도록 가이드 멘트를 제공해 주세요.
