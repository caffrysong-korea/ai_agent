---
name: flow-bridge
description: infra팀 DTCO/DM 설정(아이템 카드)을 고객 설계팀의 자체 Innovus flow에 반영한다. 고객 flow 분석 → 반영 위치 → 디자인별 항목 선택 → PnR 검증을 거쳐 고객 flow 수정안과 디자인별 knob 추천을 낸다. "고객 flow에 DTCO 넣어줘", "이 flow 분석해서 어디 넣을지", "flow-bridge 돌려" 류 요청에 사용.
# TODO(INHOUSE): 사내 opencode 스킬 frontmatter 규격에 맞게 정리
---

# flow-bridge

> 문서 안의 `schema/…`, `tools/…`, `config/…` 경로는 **flow-bridge 루트** 기준이다. `method/…`, `guides/…`, `templates/…`는 이 스킬 폴더 기준.
> <!-- TODO(INHOUSE): 사내에 설치한 위치에서 두 기준 경로가 맞는지 확인 (H1) -->

## 하는 일

```
1. 분석 ─▶ 2. 위치 ─[gate①]─▶ 3. 선택 ─[gate②]─▶ 4. 검증 ─[gate③]─▶ 수정안 + knob 추천
```

| 단계 | 한 줄 | 읽을 method | 누가 |
|---|---|---|---|
| 1. 분석 | 고객 flow와 디자인을 읽어 profile을 만든다 | method/1-map.md | flow-mapper |
| 2. 위치 | 카드마다 어디에 넣을지, 덮어쓰기 위험은 없는지 판단한다 | method/2-place.md | bridge-pilot |
| 3. 선택 | 디자인별로 어떤 항목을 적용할지 카드 결과표를 근거로 추천한다 | method/3-select.md | bridge-pilot |
| 4. 검증 | PnR을 돌려 실제 적용과 효과를 확인한다 | method/4-verify.md | bridge-pilot + pnr-rundori |

- **gate에서는 반드시 멈추고 사용자 승인을 받는다.** 승인 없이 다음 단계로 가지 않는다.
- 사용자가 특정 단계만 요청하면 그 단계만 한다 (예: "분석만 해줘" → 1단계 후 멈춤).
- 이전 단계 산출물이 없으면 그 단계부터 하자고 제안하고 멈춘다.

## 규칙 7개

1. **고객 flow 원본은 수정하지 않는다.** 수정안은 overlay 파일 + `source` 한 줄로만 제안한다.
2. **위치 주장에는 인용** (`file:line` + 그 줄에 실제 있는 문자열). 인용 없는 주장은 무효.
3. **approved 카드만 사용한다.** draft 카드는 "후보"로만 보고에 언급.
4. **덮어쓰기 판정은 readback이 최종.** 파일을 읽고 내린 추정은 "의심"으로만 표시.
5. **확인 못한 것은 unresolved에.** 추측으로 채우지 않는다.
6. **카드는 card-curator만 쓴다.** bridge-pilot은 카드를 읽기만.
7. **job 실행은 pnr-rundori만.** Innovus/PT를 직접 띄우지 않는다.

## 위임 규약

| 대상 | 언제 | 호출 |
|---|---|---|
| flow-mapper | 1단계 | `task(subagent_type="flow-mapper", ...)` |
| pnr-rundori | 4단계 run 실행/폴링 | `task(subagent_type="pnr-rundori", ...)` |
| card-curator | gate③ 승인 후 카드 결과 추가 | `task(subagent_type="card-curator", ...)` |

<!-- TODO(INHOUSE): 사내 opencode의 실제 sub-agent 호출 문법으로 교체. H2 단계에서 실호출 확인 -->

- **모사 금지.** 위임이 실패하면 bridge-pilot이 그 일을 대신하지 않는다. 실패 사유를 notes에 기록하고 사용자에게 보고한 뒤 멈춘다.

## 작업 폴더

`paths.workspace/<run_id>/` 아래에 단계별 산출물을 둔다. (config/env.yaml)

```
<run_id>/
├── 1_map/      flow_profile.yaml, design_<id>.yaml, manifest.yaml
├── 2_place/    placement.yaml, overlay/, readback/
├── 3_select/   select_<design>.yaml
├── 4_verify/   plan.yaml, results.yaml, report.md
└── notes.md    진행 기록, 위임 실패, 사용자 결정
```

## 진행 보고 (단계 끝날 때마다)

```
[단계] N/4 <이름> 완료   [다음] <gate 또는 다음 단계>
[결과] 3줄 이내
[unresolved] 상위 3개
```
