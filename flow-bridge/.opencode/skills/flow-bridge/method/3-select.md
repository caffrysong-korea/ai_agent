# 3단계 — 디자인별 항목 선택

gate ①을 통과한 카드 중 **이 디자인에 무엇을 적용할지** 추천한다. 근거는 카드의 평가 결과표다.

## 입력
- gate ① 승인된 카드 목록
- 디자인별 design profile (SDC fingerprint, traits)

## 할 일 — 디자인 × 카드마다

- [ ] 카드 결과표에서 **이 디자인과 조건이 비슷한 행**을 찾는다 (target freq, util, traits). invalid 행은 제외
- [ ] 비슷하다고 본 이유를 한 줄로 쓰고 **행 id 인용** (`DTCO-0001#R-001`)
- [ ] 근거 레벨 결정

| 근거 레벨 | 조건 |
|---|---|
| `measured` | 비슷한 조건의 유효 결과 행이 있음 |
| `rule` | 카드의 이식 주의/순서 제약으로 판단 가능 (예: 전제조건 불충족) |
| `heuristic` | 휴리스틱만 있음 (상태 seed/candidate/promoted 표시) |
| `none` | 근거 없음 |

- [ ] 추천 결정

| 추천 | 조건 |
|---|---|
| `adopt` | measured + 비슷한 행들이 positive |
| `skip` | 비슷한 행이 negative, 또는 rule로 제외 |
| `experiment` | 그 외 전부 (heuristic / none이면 adopt 금지) |

- [ ] `3_select/select_<design>.yaml` (schema/contract/stage3_selection.schema.yaml) + validate

## gate ② — 사용자에게 보여줄 표 (디자인마다)

| 카드 | 추천 | 근거 레벨 | 근거 (행 id) | 이유 |
|---|---|---|---|---|

사용자가 포함/제외를 정한다. 포함된 항목만 4단계로 간다.

## 멈출 조건
- 모든 카드가 skip → 보고 후 멈춤 (4단계 불필요)
