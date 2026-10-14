# flow-bridge

infra팀이 만든 DTCO / PnR DM 설정을 **고객 설계팀의 자체 PnR flow**에 정확히 반영하고,
디자인별로 적합한 DTCO knob을 PnR 검증까지 거쳐 추천하는 agent 스킬 묶음.

```
[평가 run 데이터] ──▶ dtco-catalog-builder ──▶ DTCO 아이템 카드 (항목별 md: 설정 + 평가 결과)
                                                        │ 읽기
                                                        ▼
[고객 flow] ──▶ flow-bridge:  1. 고객 flow 분석 ─▶ 2. 반영 위치 ─▶ 3. 항목 선택(유저 gate) ─▶ 4. PnR 검증
                                                                                              │
                                                  카드 평가 결과표에 검증 결과 추가 ◀──────────┘
```

최종 산출물: **고객 flow 수정안(overlay 방식)** + **디자인별 knob 추천(근거 포함)**.

---

## 설계 원칙

1. **판단은 LLM, 검증은 기계.** flow 구조 파악, 반영 위치, 적합성 판단은 md 가이드를 읽은 LLM이 한다.
   Python은 아이템/flow를 모르는 기계적 검증(validate / readback)만 담당한다.
   *새 아이템이나 새 flow 패턴 때문에 Python을 고쳐야 한다면 설계가 틀린 것이다.*
2. **지식은 카드에.** DTCO 항목 하나 = 카드(md) 하나. 설정, 평가 결과, 이식 주의가 모두 한 파일에 쌓인다.
3. **툴의 말이 최종.** 덮어쓰기 판정은 stage 종료 시점 readback(툴이 보고하는 실효값)으로 확정한다.
4. **인용 없는 주장은 무효.** "file:line에 있다"고 하면 그 줄에 실제로 그 문자열이 있어야 한다.
5. **고객 flow 비침습.** 수정안은 stage hook에 `source` 한 줄 + overlay 파일. 원본 로직은 고치지 않는다.
6. **데이터에 없는 건 쓰지 않는다.** 모르는 것은 카드의 "질문" 섹션이나 profile의 unresolved에 남긴다.

## 구성

| 구분 | 이름 | 역할 |
|---|---|---|
| 메인 스킬 | `flow-bridge` | 고객 flow 포팅 4단계 (thin router) |
| 카드 스킬 | `dtco-catalog-builder` | 평가 run 데이터 → DTCO 아이템 카드 생성/누적 |
| main agent | `bridge-pilot` | 4단계 진행, 유저 gate 3개, 결과 분석 |
| sub-agent | `flow-mapper` | 고객 flow / design 읽기 → profile 생성 (read-only) |
| sub-agent | `card-curator` | dtco-catalog-builder 실행 + 카드 쓰기 전담 (writer 1인) |
| sub-agent (재사용) | `pnr-rundori` | 검증 run 실행/폴링 (기존 구현 연결) |

## 디렉토리

```
flow-bridge/
├── README.md
├── HANDOFF.md                  # 사내 opencode 작업 가이드            (P5)
├── prompts/                    # 사내 opencode 단계별 프롬프트         (P5)
├── config/env.yaml             # 환경 의존값 단일 집약
├── schema/
│   ├── stage_taxonomy.yaml     # 툴 무관 stage 정의
│   ├── item_card.schema.yaml   # 카드 frontmatter
│   ├── item_card.spec.md       # 카드 본문 규격 (섹션, 결과표, 판정 규칙)
│   ├── flow_profile.schema.yaml
│   ├── design_profile.schema.yaml
│   ├── common.schema.yaml
│   └── contract/               # flow-bridge 단계 간 handoff
├── examples/                   # 가상 데이터만
│   ├── synthetic_runs/         #   평가 run 예시 (clean / confounded)
│   ├── cards/                  #   위 run으로 만든 카드 예시
│   └── synthetic_flow/ + *_profile.example.yaml   # 가상 고객 flow + profile 예시
├── .opencode/                  # 스킬 + 에이전트                      (P2 완료, P3)
├── tools/                      # validate / readback                   (P4)
└── tests/                                                              (P4)
```

## 마커 규칙 (사내 작업용)

| 마커 | 의미 | 처리 |
|---|---|---|
| `TODO(INHOUSE): <무엇을, 왜>` | 사내 환경 지식이 있어야 확정 가능한 곳 | `grep -rn "TODO(INHOUSE)"`로 목록화 → 사내 opencode가 채움 |
| `ASK` | 사람의 답이 필요한 profile 필드 | 추론으로 채우기 금지 |

## 보안 규칙

- 이 repo(public)에는 **가상 데이터만** 둔다. 실제 고객 flow, run 데이터, 카드 실내용, 사내 경로/모델명은 사내에만 둔다.
- 실데이터 위치는 `config/env.yaml`의 `paths.*`, `run_data.*`로 지정.

## 진행 상태

| Phase | 내용 | 상태 |
|---|---|---|
| P1 | 골격 + 스키마 | 완료 (P2 재설계 반영) |
| P2 | dtco-catalog-builder (run 데이터 → 카드) | 완료 |
| P3 | flow-bridge 스킬 + 에이전트 + 관찰 가이드 | 예정 |
| P4 | Python validate / readback | 예정 |
| P5 | HANDOFF + 프롬프트 | 예정 |
