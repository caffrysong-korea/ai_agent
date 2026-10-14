# synthetic_runs (가상 평가 run 데이터)

dtco-catalog-builder 예시용 **가상** run 데이터. 실제 run이 아니며 수치도 가상이다.
파일명(innovus.cmd, qor_summary.txt)은 예시이고 사내 실제 이름은 config/env.yaml `run_data.*`에서 정한다.

| run 쌍 | 평가 항목 | 의도한 결과 |
|---|---|---|
| blkA_base → blkA_uskew_on | useful skew | **clean** diff (useful skew 한 줄만 다름) |
| blkB_base → blkB_uskew_on | useful skew | **confounded** (cong effort도 같이 바뀜 → invalid) |
