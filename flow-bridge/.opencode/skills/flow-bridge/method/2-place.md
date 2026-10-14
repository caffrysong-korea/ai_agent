# 2단계 — 반영 위치

카드마다 "고객 flow의 어디에 넣나"를 정한다. **툴 문법이 아니라 stage와 의미로 판단**하고, 문법은 overlay를 만들 때만 카드의 settings에서 가져온다.

## 입력
- 1단계 profile (flow + 디자인들)
- approved 카드 전부 (paths.item_cards)

## 할 일 — 카드마다 순서대로

- [ ] **툴 맞음?** 카드 settings에 고객 flow ui_mode의 variant가 없음 → `no_binding`
- [ ] **REF 의존성?** settings.requires의 proc/변수/파일이 고객 flow에 있는지 grep → 없으면 `needs_human`
- [ ] **이미 있음?** profile에 같은 `matches_item` 설정이 있으면
  - 값 같음 → `already_present`
  - 값 다름 → `conflict` (고객이 의도적으로 바꿨을 수 있음 → 사용자 판단)
- [ ] **어디에?** 카드 stage와 같은 stage의 hook 중
  - 공식 hook 슬롯 우선
  - 그 stage의 주 커맨드(opt/route 등)보다 **앞에서** 걸려야 효과가 있으면 `before_main_cmd` 위치
  - 결정 → `placeable` + hook_point id
- [ ] **덮어쓰기 위험?** 삽입 지점 이후 stage에서 같은 설정을 다시 거는 곳 (flow + 디자인 override 둘 다)
  - 직접 보임 → `confirmed`
  - proc / 조건 / 변수 경유라 확실치 않음 → `suspected`
- [ ] **readback 지점**: sticky=yes면 삽입 stage 끝 + 이후 모든 stage 끝, no면 삽입 stage 끝만

## 산출물 만들기
- [ ] `2_place/overlay/<stage>_<hook>.tcl` : 해당 hook에 들어갈 설정 줄. 줄마다 주석 `# DTCO-xxxx v<ver>`
- [ ] `2_place/readback/` 생성: `python3 $FB_ROOT/tools/readback.py gen --placement 2_place/placement.yaml --cards <paths.item_cards> --out 2_place/readback`
  - 생성된 `readback_<stage>.tcl`을 각 readback 지점 stage 끝에서 source하는 줄을 patch_lines에 추가
- [ ] insert_line hook이면 고객 flow에 넣을 `source` 한 줄을 patch_lines에 기록 (적용은 하지 않음)
- [ ] `2_place/placement.yaml` ($FB_ROOT/schema/contract/stage2_placement.schema.yaml)
  - `python3 $FB_ROOT/tools/validate.py stage2 2_place/placement.yaml --root <flow_root>`

## gate ① — 사용자에게 보여줄 표

| 카드 | 판정 | 위치 (file:line) | 덮어쓰기 위험 | 비고 |
|---|---|---|---|---|

conflict / needs_human / suspected 위험은 표 위쪽에 따로 강조한다. 승인된 카드만 3단계로 간다.

## 멈출 조건
- approved 카드가 0개 → dtco-catalog-builder로 카드를 먼저 만들자고 제안
- 모든 카드가 placeable이 아님 → 표를 보고하고 멈춤
