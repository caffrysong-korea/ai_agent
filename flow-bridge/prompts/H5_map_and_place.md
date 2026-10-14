# H5 — 고객 flow 분석 + 반영 위치 (1~2단계)

툴 실행 없이 파일만 읽는 단계. 결과는 gate ① 표.

---

bridge-pilot으로 flow-bridge 스킬 **1~2단계만** 진행하자. 3단계 이후로 넘어가지 마.

입력:
- 고객 flow 루트: <경로>, 진입 스크립트: <파일>
- 디자인: <이름> (cfg: <경로>, SDC: <경로>)
- 카드: `paths.item_cards`의 approved 카드 전부

규칙:
- 1단계는 반드시 flow-mapper에 위임. 실패하면 대신하지 말고 보고.
- 고객 flow 원본 수정 금지. 산출물은 작업 폴더(`paths.workspace/<run_id>/`)에만.
- 1단계 산출물과 placement는 validate 통과 필수.
- 2단계가 끝나면 **gate ① 표를 보여주고 멈춰.**

보고 형식:
```
[1단계] stage N개 매핑 / hook N개 / unresolved N개 (상위 3개)
[새 패턴] 관찰 가이드에 없던 것 (없으면 없음)
[2단계] 카드 N개 → placeable N / already_present N / conflict N / 기타 N
[덮어쓰기 위험] confirmed N / suspected N
```
+ gate ① 표
