---
name: dtco-catalog-builder
description: 이미 돌린 PnR/PPA 평가 run 데이터(어떤 DTCO/DM 항목의 평가인지 알고 있는 run들)를 읽어 항목별 아이템 카드(md)를 만들거나 결과를 누적한다. "DTCO 카드 만들어", "평가 결과 정리해", "이 run들 카드에 반영" 류 요청에 사용.
# TODO(INHOUSE): 사내 opencode 스킬 frontmatter 규격에 맞게 정리
---

# dtco-catalog-builder

## 하는 일 (한 줄)

**평가 run 데이터 → DTCO 항목별 카드(md).** 카드가 없으면 만들고, 있으면 평가 결과를 한 줄 추가한다.
flow-bridge는 이 카드를 읽어서 고객 flow에 무엇을 어디에 넣을지 판단한다.

```
baseline run ─┐
              ├─ ① 설정 diff (무엇이 바뀌었나) ─┐
item-on run ──┤                                 ├─▶ ③ 카드 생성 / 결과 행 추가
              └─ ② QoR delta (결과가 어땠나) ───┘
```

- 실행 agent: **card-curator** (카드 쓰기 권한은 card-curator에만 있다)
- 절차: method/build-card.md
- 카드 규격: 카드 템플릿 templates/item_card.md, 상세 규칙은 flow-bridge 스키마의 item_card.spec.md

## 규칙 5개

1. **데이터에 있는 것만 쓴다.** 설정은 run diff로, 숫자는 report로 확인된 것만. 모르는 건 "질문" 섹션에.
2. **결과 행은 추가만.** 기존 행 수정/삭제 금지. invalid 행도 남긴다.
3. **diff에 다른 변경이 섞이면 invalid.** 그 run 쌍의 결과는 이 항목의 효과로 볼 수 없다.
4. **해석은 결과 행 id를 인용해서만.** 행이 적으면 "근거 부족"이라고 쓴다.
5. **요청한 run만 처리하고 멈춘다.** approved 승격은 사용자가 승인할 때만.

## 입력 받는 방법 (셋 중 아무거나)

| 방법 | 예 |
|---|---|
| 사용자가 직접 알려줌 | "blkA_base vs blkA_uskew 는 useful skew 평가야" |
| 다른 루프의 run 목록 파일 | config/env.yaml `run_data.run_manifest_hint` 형식 |
| 디렉토리 이름에서 추정 | `*_base`, `*_<항목>_on` 등 → **추정한 짝을 표로 보여주고 확인받은 뒤 진행** |

## 보고 형식

```
[처리] run 쌍 N개 → 카드 신규 N / 결과 추가 N
[결과 요약] 카드별 한 줄 (판정)
[invalid] N개 + 사유
[질문] 데이터로 알 수 없던 것 상위 3개
```
