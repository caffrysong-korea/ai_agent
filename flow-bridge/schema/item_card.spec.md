# DTCO item card — 본문 규격

카드 하나 = DTCO/DM 항목 하나. 사람이 읽는 설명서이자, flow-bridge가 판단 근거로 읽는 데이터다.
**섹션 이름과 순서, 평가 결과표 컬럼은 고정.** (tools/validate가 확인)

```
---
<frontmatter: item_card.schema.yaml>
---
# <item_id> <제목>

## 요약
## 설정
## 평가 결과
## 해석
## 고객 flow 이식 주의
## 질문
## 이력
```

## 섹션별 규칙

| 섹션 | 쓰는 것 | 규칙 |
|---|---|---|
| 요약 | 무엇을 바꾸는 항목인지 1~2줄 | 효과 주장 금지 (그건 해석에) |
| 설정 | 바뀐 커맨드 원문, 확인한 run과 파일:줄, 켜고 끄는 방식, stage 근거 | run diff로 확인된 것만 |
| 평가 결과 | 아래 표. **행 추가만, 수정/삭제 금지** (정정은 새 행 + 비고에 `R-xxx 정정`) | 숫자는 reports에서 읽은 값만 |
| 해석 | 어떤 조건에서 좋고 나빴는지 | **반드시 결과 행 id 인용** (`R-002, R-005 근거`). 행 수가 적으면 "근거 부족"이라고 쓴다 |
| 고객 flow 이식 주의 | REF 전용 의존성, 덮어쓰기 위험(sticky), 순서 제약 | |
| 질문 | 데이터로 알 수 없는 것 (의도, 미확인 조건) | 없으면 "없음" |
| 이력 | 날짜 · 무엇을 · 출처 | 한 줄씩 |

## 평가 결과표 (컬럼 고정)

```
| id | 날짜 | ver | 출처 | 디자인 | 조건 | fmax% | WNS | TNS | power% | area% | 판정 | run | 비고 |
|----|------|-----|------|--------|------|-------|-----|-----|--------|-------|------|-----|------|
```

| 컬럼 | 값 |
|---|---|
| id | `R-001`부터 증가 |
| ver | 평가 당시 카드 version |
| 출처 | `eval` (기존 평가 run 데이터) / `bridge` (flow-bridge 4단계 고객 flow 검증) |
| 조건 | target freq, util 등 비교에 필요한 최소 조건. 예) `2.0GHz, util 0.70` |
| fmax% / power% / area% | baseline 대비 % (+ = 증가). 없으면 `-` |
| WNS / TNS | baseline 대비 차이 (ns). 없으면 `-` |
| 판정 | `positive` / `neutral` / `negative` / `inconclusive` / `invalid` |
| run | baseline run → treatment run 경로 (사내 경로) |

### 판정 규칙

| 판정 | 조건 |
|---|---|
| invalid | run diff에 이 항목 외 다른 변경이 섞임 (confounded) · flow-bridge 검증에서 readback이 `applied`가 아님 · 둘 중 한 run 실패 |
| inconclusive | 주요 지표 delta가 노이즈 폭(config/env.yaml `policy.noise_band`) 이하 |
| positive / negative | 의도한 주 지표가 노이즈 폭 밖에서 개선 / 악화 |
| neutral | 주 지표는 노이즈 폭 이하인데 다른 지표가 노이즈 폭 밖에서 움직임 — 비고에 무엇이 움직였는지 |

- `invalid` 행도 지우지 않는다 (같은 실패 반복 방지). 해석에서는 제외.
- 절대값(fmax 2.1GHz 등)은 표에 쓰지 않는다. 디자인 간 비교가 안 되기 때문.

## 상태

| 상태 | 조건 |
|---|---|
| draft | 카드 생성 직후 |
| approved | 설정이 confounded 아닌 run diff로 1회 이상 확인됨 + settings에 빈 값 없음 + **사용자가 승인** (이력에 기록) |

- settings가 바뀌면 version +1, status는 draft로 돌아간다.
