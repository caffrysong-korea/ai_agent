# 카드 만들기 절차

## 0. run 쌍 표 확정

처리 전에 아래 표를 만들어 사용자에게 보여주고 확인받는다. (다른 루프의 목록 파일로 받았으면 표만 보여주고 바로 진행)

| 항목 | 디자인 | baseline run | treatment run | 조건 (freq, util 등) |
|---|---|---|---|---|

- 항목이 기존 카드와 같은지 판단이 안 되면 묻는다. (같은 항목인데 카드를 두 개 만들면 결과가 흩어진다)

## 1. 설정 diff — 무엇이 바뀌었나

run 쌍마다 baseline과 treatment를 비교한다. 소스 우선순위:

1. **툴 커맨드 로그** (실제로 실행된 커맨드 기록, env `run_data.cmd_log`) — 가장 정확
2. run 스크립트 / 템플릿으로 생성된 tcl
3. run 설정 파일 (yaml/csv 등)

비교할 때 무시할 것: 경로, run 이름, 날짜, 호스트, 랜덤 seed 같은 run마다 다른 값.

결과 판정:

| diff 결과 | 처리 |
|---|---|
| 항목 설정만 다름 | **clean** → settings에 기록 (커맨드 원문, 파일:줄) |
| 항목 설정 + 다른 변경 | **confounded** → 결과 행 판정 `invalid`, 비고에 섞인 변경 기록 |
| 차이 없음 | 설정이 안 걸린 것 → 결과 행 `invalid`, 비고 "diff 없음" |

clean diff에서 같이 확인할 것:
- **stage**: 바뀐 커맨드가 어느 stage에서 실행됐나 (schema/stage_taxonomy.yaml 기준)
- **sticky**: mode/attribute 설정이면 `yes`, 특정 커맨드 옵션이면 `no`, 모르면 `unknown`
- **requires**: 커맨드가 run 쪽에서 정의된 proc/변수/파일을 쓰면 기록 (고객 flow 이식 위험)
- **readback**: 같은 툴에서 실효값을 묻는 커맨드. 확실할 때만 초안으로 쓰고 `verified: false`

## 2. QoR delta — 결과가 어땠나

- env `run_data.qor_summary`의 QoR 파일에서 fmax, WNS, TNS, power, area를 읽는다.
- baseline 대비 delta로 기록 (fmax/power/area는 %, WNS/TNS는 ns 차이). 절대값은 쓰지 않는다.
- 판정은 schema/item_card.spec.md 판정 규칙 + env `policy.noise_band`.
- QoR 파일이 없거나 run이 실패했으면 `invalid`.

## 3. 카드 쓰기

**카드 없음 → 새로 만들기**
- templates/item_card.md 복사. item_id는 기존 최대 + 1 (삭제된 번호 재사용 금지).
- status: draft, version: 1.
- index.md에 한 줄 추가.

**카드 있음 → 결과 추가**
- 평가 결과표에 새 행 추가 (`R-` 번호 이어서). 기존 행은 건드리지 않는다.
- 이번 diff의 settings가 카드와 다르면: settings 갱신 + version +1 + status → draft + 이력 기록.
- 해석 섹션을 결과표 전체 기준으로 다시 쓴다 (행 id 인용).

## 4. 검증

- 카드 검증: `python3 tools/validate.py card <카드 파일>` (frontmatter, 섹션 순서, 결과표, 해석 인용)
- 실패하면 고치고 다시. 통과 전에는 "완료" 보고 금지.

## 5. approved 승격 (사용자 요청 시에만)

조건: clean diff 결과 행이 1개 이상 + settings에 빈 값 없음 + 사용자 승인.
→ status: approved, 이력에 "YYYY-MM-DD 사용자 승인".
