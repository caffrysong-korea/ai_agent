---
name: dtco-catalog-builder
description: infra팀 DTCO/DM reference 설정을 REF flow 분석과 infra 담당자 인터뷰 이터레이션으로 구조화해 flow-bridge용 승인 카탈로그(catalog item, knob registry, REF flow 구조 md, ledger seed)를 만들고 유지한다. "카탈로그 만들어", "REF flow 정리", "DTCO 항목 정리", "infra 답변 반영", "REF flow 바뀜" 류 요청에 사용.
# TODO(INHOUSE): 사내 opencode 스킬 frontmatter 규격(필수 키, description 길이 제한)에 맞게 정리
---

# dtco-catalog-builder

## 1. 정체성

- infra팀의 DTCO/DM 지식을 **flow-bridge가 읽을 수 있는 승인된 데이터**로 바꾸는 스킬이다.
- 산출물은 네 가지: REF flow 구조 md, catalog item, knob registry entry, ledger seed.
- flow-bridge 본체(고객 flow 포팅 1~4단계)는 이 스킬의 산출물을 **읽기만** 한다.
- 실행 주체: bridge-pilot (catalog 모드). sub-agent: flow-mapper(REF profile 생성), ledger-curator(ledger seed 기록).

## 2. 절대 규칙

1. **들은 만큼만 기록한다.** infra 담당자 답변이나 REF flow 인용으로 확인되지 않은 값은 `ASK`로 남긴다. 그럴듯한 추론으로 채우는 것은 실패다.
2. **binding은 REF script가 있는 tool variant만.** 없는 variant는 `absent`. 다른 툴 문법을 일반지식으로 만들어 넣지 않는다.
3. **모든 위치 주장에는 citation.** `{file, line, excerpt}` — excerpt는 그 줄에 실제로 있는 문자열이어야 한다.
4. **REF 전용 의존성 표시.** snippet이 REF flow에만 있는 proc/변수/파일을 쓰면 `requires`에 반드시 기록한다.
5. **상태는 조건을 만족할 때만 승격.** draft → reviewed → approved 조건은 method/interview-loop.md 를 따른다. approved는 infra 담당자의 명시적 승인 없이는 불가.
6. **원본 수정 금지.** REF flow, infra 스크립트는 읽기만 한다.
7. **요청한 모드만 수행.** 모드가 끝나면 결과를 보고하고 멈춘다. 다음 모드는 사용자 지시가 있을 때만.
8. **스키마 검증 필수.** 카탈로그/registry를 쓴 뒤 tools/validate로 검증한다. 실패하면 "완료"로 보고하지 않는다.
   <!-- TODO(INHOUSE): validate 실행 커맨드 확정 (P4 산출물, HANDOFF.md 참고) -->

## 3. 모드 라우팅

먼저 요청을 아래 표로 분류한다. 애매하면 사용자에게 어느 모드인지 묻는다 (추측 금지).

| 요청 신호 | 모드 | 읽을 method |
|---|---|---|
| REF flow 경로를 주며 "정리/분석/지도" | A. REF 매핑 | method/ref-mapping.md |
| REF map이 있고 "항목 뽑아/카탈로그 초안" | B. 항목 추출 | method/item-extraction.md |
| "질문지", "infra 답변 왔어", "승인 받았어" | C. 인터뷰 루프 | method/interview-loop.md |
| "REF flow 업데이트됨", "infra 스크립트 바뀜" | D. 유지보수 | method/maintenance.md |
| 카탈로그 현황 질문 (몇 개 approved? ASK 남은 것?) | 조회 | 카탈로그 파일을 읽고 바로 답한다. 모드 진입 없음 |

모드 간 선행 조건:
- B는 A의 REF map이 있어야 한다. 없으면 A부터 하자고 제안하고 멈춘다.
- C는 draft 항목이 있어야 한다.
- D는 기존 REF map + 카탈로그가 있어야 한다.

## 4. 위임 규약

### flow-mapper (모드 A, D)
- 호출: `task(subagent_type="flow-mapper", prompt=...)`
  <!-- TODO(INHOUSE): 사내 opencode의 실제 sub-agent 호출 문법으로 교체. H2 단계에서 실호출 확인 -->
- 넘길 것: REF flow 루트, entry script, `flow_kind: reference`, 산출 파일 저장 위치.
- 받을 것: stage1 contract 형식의 manifest (flow_profile 경로 + status + unresolved 수).
- **모사 금지.** flow-mapper 호출이 실패하면 bridge-pilot이 직접 profile을 만들지 않는다.
  실패 사유를 작업 notes에 기록하고 사용자에게 보고한 뒤 멈춘다.

### ledger-curator (모드 C)
- 호출: `task(subagent_type="ledger-curator", prompt=...)`  <!-- TODO(INHOUSE): 위와 동일 -->
- 넘길 것: ledger entry 초안(들) — source는 `seed_interview` 또는 `infra_ref`.
- **ledger 파일을 bridge-pilot이 직접 쓰지 않는다.** 호출 실패 시 초안을 작업 notes에 보관하고 보고.

## 5. 산출물 위치

모두 config/env.yaml 의 `paths.*` 키로 결정한다. 경로를 하드코딩하지 않는다.

| 산출물 | env 키 | 쓰기 권한 |
|---|---|---|
| REF flow 구조 md | `paths.ref_flow_maps` | bridge-pilot (catalog 모드) |
| REF flow profile | `paths.workspace` 하위 | flow-mapper |
| catalog item / knob registry | `paths.catalog_store` | bridge-pilot (catalog 모드) |
| ledger seed | `paths.ledger_store` | ledger-curator |
| 질문지 / 이터레이션 기록 | `paths.workspace` 하위 | bridge-pilot |

## 6. 보고 형식 (모드 종료 시)

```
[모드] A/B/C/D  [대상] <REF flow id 또는 항목 범위>
[결과] 3줄 이내
[상태 현황] draft N / reviewed N / approved N, 남은 ASK N
[unresolved] 상위 3개
[다음 제안] 한 줄 (실행하지 않음)
```
