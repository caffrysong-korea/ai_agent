# 고객 flow 관찰 가이드 (Innovus)

1단계에서 고객 flow를 읽을 때 **"여기는 꼭 확인하라"** 는 체크리스트.
초안은 일반적인 Innovus flow 지식으로 작성했다. 실제 고객 flow에서 새 패턴을 만나면 아래 "추가된 패턴"에 쌓는다.

- 수정: card-curator만 (사용자 승인 후)
- 고객 이름/경로 같은 식별 정보는 쓰지 않는다. 패턴만 쓴다.

## 기본 체크리스트

| # | 확인할 것 | 찾는 신호 | 왜 중요한가 |
|---|---|---|---|
| 1 | 진입점과 실행 방식 | csh/LSF 래퍼, `innovus -init/-files` 류 실행 줄, 진입 tcl | stage 순서의 출발점. 4단계 run 방식과도 연결 |
| 2 | UI 모드 | legacy(`setXxxMode`, `getXxxMode`) vs stylus(`set_db`, `get_db`), 혼용 여부 | 카드의 어떤 variant 문법을 쓸지 결정 |
| 3 | source 체인 | 변수로 조립된 경로, `glob`, `if` 안의 `source`, env var | 놓치면 설정 위치를 못 찾음 |
| 4 | 템플릿 생성 | `__PLACEHOLDER__` 류 토큰, python/csh가 tcl을 생성 | 템플릿만 보면 값이 없음 → 생성 결과물도 확인 |
| 5 | stage 경계 | 파일 분할, `saveDesign`/`restoreDesign` 같은 checkpoint | stage가 **별도 Innovus 세션**이면 설정이 다음 세션에 이어지는지 확실치 않음 → readback으로 확인 대상 |
| 6 | hook 슬롯 | `run_hook`, pre/post 사용자 스크립트 디렉토리, user proc 슬롯 | 고객 flow를 안 고치고 overlay를 넣을 수 있는 자리 |
| 7 | 디자인별 override | design cfg, 블록별 tcl, `apply_*override*` 류 proc | 같은 flow라도 디자인마다 설정이 바뀌는 지점. 덮어쓰기 1순위 의심 |
| 8 | 일괄 설정 | `foreach` + 옵션 목록, dict/array 순회 | grep으로 옵션 이름만 찾으면 실제 적용 줄을 놓침 |
| 9 | 조건 분기 | `if {$TECH ...}`, corner/mode/버전 분기 | 어떤 조건에서 어떤 값이 걸리는지 갈림 |
| 10 | timing 설정 재정의 | stage별 derate, uncertainty, MMMC 재로딩 | SDC가 stage 중간에 바뀌면 design profile의 SDC fingerprint와 다를 수 있음 |
| 11 | 설정 초기화 | mode reset/초기화 커맨드, 설정 파일 재-source | 앞에서 넣은 overlay가 지워질 수 있음 |
| 12 | 툴 버전 분기 | 버전 체크 후 다른 커맨드 사용 | 카드 커맨드가 그 버전에서 동작하는지 (verified 여부) |

## 막혔을 때

- 경로가 런타임에만 결정됨 → 가능한 값을 unresolved에 쓰고, 4단계 readback으로 확인 대상 표시
- 설정이 proc 깊숙이 숨어 있음 → 찾은 데까지 인용하고 `via: proc`, 덮어쓰기 위험은 `suspected`
- 파일이 너무 많음 → 진입점부터 실제 source되는 파일만 따라간다 (디렉토리 전체 스캔 금지)

## 추가된 패턴

새 고객 flow에서 위 체크리스트로 잡히지 않은 패턴을 발견하면 아래 형식으로 추가한다.

| 날짜 | 패턴 | 찾는 신호 | 왜 중요한가 | 처음 발견한 flow 유형 (식별 정보 제외) |
|---|---|---|---|---|
