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
