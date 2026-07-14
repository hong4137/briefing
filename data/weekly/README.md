# data/weekly

주간 브리핑 메타데이터의 **단일 진실 소스**입니다.

- 파일명: `weekly-YYYY-MM-DD.json` (하이픈, 언더스코어 금지)
- 발행 = `archive/weekly-YYYY-MM-DD.html` + 이 파일을 **한 커밋**으로 푸시
- `sync-drive.yml`이 이 디렉터리를 읽어 `briefings.json`의 `weekly[]`를 생성
- Google Sheet의 `weekly` 탭은 더 이상 사용하지 않음 (2026-07-14 이관)

## 무결성 가드
`archive/weekly-*.html`이 있는데 대응하는 JSON이 없으면 워크플로우가 실패합니다.
HTML만 커밋하고 메타데이터를 빠뜨려 목록에서 조용히 사라지는 사고를 막기 위함입니다.
