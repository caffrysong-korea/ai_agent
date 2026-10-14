# 1단계 — 고객 flow 분석

flow-mapper가 수행한다. bridge-pilot은 위임하고 manifest를 받는다.

## 입력
- 고객 flow 루트 + 진입 스크립트
- 대상 디자인 목록 (디자인별 cfg / SDC 위치)
- 기존 flow_profile (같은 flow_version이면 재사용 → 디자인 profile만 새로 만든다)

## 할 일
- [ ] **관찰 가이드**(guides/observation-guide.md)를 먼저 읽고, 항목 순서대로 확인한다
- [ ] 진입점 → source 체인을 따라가며 stage를 abstract stage에 매핑 ($FB_ROOT/schema/stage_taxonomy.yaml)
- [ ] stage마다 hook 지점 기록 (공식 hook 슬롯 우선, 없으면 insert_line 후보)
- [ ] mode/attribute 설정을 전부 기록. approved 카드와 같은 설정이면 `matches_item`
- [ ] 디자인별 설정이 끼어드는 지점(design_override_points) 기록 — proc/조건 경유 포함
- [ ] 디자인마다: SDC fingerprint(clock, period, false/multicycle 수, uncertainty) + design override 설정
- [ ] 모든 위치에 citation. 확인 못한 것은 unresolved
- [ ] validate 통과
  - `python3 $FB_ROOT/tools/validate.py flow_profile 1_map/flow_profile.yaml`
  - `python3 $FB_ROOT/tools/validate.py design_profile 1_map/design_<id>.yaml`

## 출력
- `1_map/flow_profile.yaml` ($FB_ROOT/schema/flow_profile.schema.yaml)
- `1_map/design_<id>.yaml` ($FB_ROOT/schema/design_profile.schema.yaml)
- `1_map/manifest.yaml` ($FB_ROOT/schema/contract/stage1_mapping.schema.yaml)

## 멈출 조건
- 진입 스크립트를 찾을 수 없음 → 사용자에게 질문
- stage를 하나도 매핑하지 못함 → 보고 후 멈춤
- validate 실패가 해결되지 않음 → 보고 후 멈춤
- 관찰 가이드에 없는 새 패턴 발견 → 계속 진행하되 보고에 "새 패턴" 섹션으로 남김 (card-curator가 가이드에 추가할지 사용자 판단)
