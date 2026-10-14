# H6 — 항목 선택 + PnR 검증 (3~4단계, 라이브)

**붙여넣기 전 확인:** $FB_ROOT/config/env.yaml의 `execution.*`(pnr-rundori 연결)과 `policy.noise_band`가 채워져 있어야 한다.

---

H5에서 승인한 gate ① 결과로 flow-bridge **3~4단계**를 진행하자.

gate ① 승인 항목: <DTCO-xxxx, ...>

규칙:
- 3단계가 끝나면 **gate ② 표를 보여주고 멈춰.** 내가 포함/제외를 정하면 4단계로.
- 4단계 run 실행과 폴링은 반드시 pnr-rundori에 위임. Innovus를 직접 띄우지 마. blocking wait 금지.
- run 수가 `policy.ablation.max_runs`를 넘으면 실행 전에 나에게 물어.
- 판정은 readback 먼저 (`$FB_ROOT/tools/readback.py judge`), applied인 항목만 QoR 비교.
- report.md를 만들고 **gate ③에서 멈춰.** 내가 승인하면 card-curator에 결과 행 추가를 위임.

gate ② 보고:
```
[디자인] 카드별 추천 (adopt/experiment/skip) + 근거 레벨 + 근거 행 id
```

4단계 보고:
```
[run] 계획 N / 완료 N / 실패 N
[readback] applied N / overridden N / missing N
[효과] 항목별 한 줄 (delta, 판정)
[수정안] 넣을 source 줄 N개 / overlay 파일 N개
```
