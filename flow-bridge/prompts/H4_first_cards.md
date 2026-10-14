# H4 — 첫 카드 만들기

어떤 DTCO 항목 평가인지 알고 있는 기존 run 쌍 1~2개로 시작한다.

---

card-curator로 dtco-catalog-builder 스킬을 실행해서 DTCO 카드를 만들자.

입력 run 쌍:
- <항목 이름>: <baseline run 경로> → <항목 on run 경로>   (디자인: <이름>)
- (있으면 하나 더)

규칙:
- 반드시 card-curator 에이전트에게 위임해. 위임이 실패하면 대신하지 말고 실패를 보고해.
- 스킬의 method/build-card.md 절차 0~4만. approved 승격은 내가 따로 말할 때만.
- 카드는 $FB_ROOT/config/env.yaml의 `paths.item_cards`에만 쓴다.
- 끝나면 `python3 $FB_ROOT/tools/validate.py card <카드>` 통과 확인.

보고 형식 (스킬 보고 형식 그대로):
```
[처리] run 쌍 N개 → 카드 신규 N / 결과 추가 N
[결과 요약] 카드별 한 줄 (판정)
[invalid] N개 + 사유
[질문] 상위 3개
```

카드를 내가 확인한 뒤 "DTCO-xxxx 승인"이라고 하면 status를 approved로 바꿔.
