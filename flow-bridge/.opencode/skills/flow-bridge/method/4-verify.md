# 4단계 — PnR 검증

선택된 항목을 고객 flow로 실제로 돌려서 **① 적용됐는지(readback) ② 효과가 있는지(QoR)** 확인한다.
run 실행과 폴링은 pnr-rundori가 한다.

## 입력
- gate ② 선택 결과 (디자인별 항목 목록)
- 2단계 overlay / readback 파일

## 할 일

### run 계획
- [ ] 디자인마다 run 목록 작성

| run | 항목 |
|---|---|
| baseline | 없음 (고객 flow 원본 그대로) |
| all_on | 선택 항목 전부 |
| loo_<항목> | 선택 항목 중 하나만 뺌 (항목이 2개 이상일 때) |

- [ ] 총 run 수가 `policy.ablation.max_runs` 초과 → 사용자에게 줄일 항목을 묻는다
- [ ] `4_verify/plan.yaml` ($FB_ROOT/schema/contract/stage4_ablation.schema.yaml)

### 실행
- [ ] plan을 pnr-rundori 입력 형식으로 변환해 위임  <!-- TODO(INHOUSE): $FB_ROOT/config/env.yaml execution.runner_contract 참고. 실행/폴링 방식은 pnr-rundori 구현을 그대로 따른다 -->
- [ ] 완료 대기는 pnr-rundori의 polling 방식. bridge-pilot이 blocking wait 하지 않는다

### 확인
- [ ] **readback 먼저.** run마다 판정 (applied / overridden / missing)
  - `python3 $FB_ROOT/tools/readback.py judge --expect 2_place/readback/expect.yaml --log <run 로그> --out 4_verify/readback_<run>.yaml`
  - overridden → 그 항목 결과는 `invalid`. 2단계의 덮어쓰기 위험을 다시 확인할 지점으로 보고
- [ ] **QoR delta** (applied인 항목만)
  - 항목 1개: all_on − baseline
  - 항목 여러 개: 항목 효과 = all_on − loo_<항목>, 전체 효과 = all_on − baseline
- [ ] 판정은 $FB_ROOT/schema/item_card.spec.md 판정 규칙 + `policy.noise_band`
- [ ] (선택) 결과 분석이 더 필요하면 ppa-booster 분석 규칙을 champ run에 적용  <!-- TODO(INHOUSE): DELTA ppa-booster 연결 방식 -->

## 출력 — `4_verify/report.md`

1. **고객 flow 수정안**: 넣을 `source` 줄(위치 포함) + overlay 파일 목록. readback으로 applied 확인된 항목만
2. **디자인별 knob 추천표**: 항목 · 추천(적용/보류) · 효과(delta) · 근거(run, 행 id)
3. **문제 목록**: overridden / invalid / 실패 run과 원인
4. **카드에 추가될 결과 행 초안** (출처 `bridge`)

## gate ③
- report를 보여주고 "카드에 결과를 추가할지" 승인받는다
- 승인 → card-curator에 결과 행 초안 위임 (bridge-pilot이 카드를 직접 쓰지 않는다)

## 멈출 조건
- baseline run 실패 → 비교 불가. 보고 후 멈춤
- 모든 항목이 overridden / missing → 2단계로 돌아가자고 보고
