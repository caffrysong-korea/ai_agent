# Mode D — 유지보수 (REF flow 변경 반영)

목표: infra가 REF flow를 바꿨을 때 카탈로그를 갱신한다. **기존 지식(승인 이력, ledger)을 잃지 않는 것**이 최우선.

---

## D1. 새 REF map 생성

- 모드 A를 새 버전 식별자로 수행한다. 기존 REF map은 덮어쓰지 않는다 (`<flow_id>__<새버전>.md`로 별도 저장).

## D2. 차이 분석

이전 REF map과 새 REF map의 4절(항목 후보) / 3절(toggle) / 6절(REF 전용 전제)을 비교한다.

| 변화 유형 | 판정 기준 |
|---|---|
| 위치만 이동 | 설정 줄 내용 동일, file:line만 바뀜 |
| 값 변경 | 같은 커맨드/옵션, 값이 다름 |
| 내용 변경 | 커맨드 추가/삭제, snippet code 변경 |
| stage 이동 | abstract_stage가 바뀜 |
| 신규 후보 | 이전에 없던 toggle |
| 삭제 후보 | 새 REF에서 사라진 toggle |
| 전제 변경 | requires 대상 proc/변수의 정의가 바뀜 |

## D3. 항목별 처리

| 변화 | catalog item 처리 | version | status |
|---|---|---|---|
| 위치만 이동 | ref_flow_location citation만 갱신 | 유지 | 유지 |
| 값 변경 / 내용 변경 / stage 이동 | 필드 갱신 | **+1** | **draft로 강등** (재검토 필요) |
| 전제 변경 | requires 갱신 + 확인 질문 추가 | +1 | draft |
| 신규 후보 | 모드 B로 새 항목 생성 | 1 | draft |
| 삭제 후보 | **삭제하지 않는다.** 질문지에 "폐기 여부" 확인 질문 추가. review_log에 "REF <버전>에서 사라짐" 기록 | 유지 | 유지 (답변 후 결정) |

- version이 오른 항목의 이전 version ledger 결과는 그대로 둔다. ledger는 item_id+version 단위라 섞이지 않는다.
- knob registry는 binding의 `set` 문법이 바뀐 경우에만 갱신 (verified를 false로 되돌림).

## D4. 검증 및 보고

- tools/validate 통과 필수.
- 보고: SKILL.md 6절 형식 + 변화 유형별 개수, draft로 강등된 항목 목록, 폐기 확인이 필요한 항목 목록.
- 강등된 항목이 있으면 [다음 제안]에 "모드 C 질문지 생성"을 넣는다 (실행하지 않음).
