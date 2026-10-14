# flow-bridge

infra팀이 만든 DTCO / PnR DM reference 설정을 **고객 설계팀의 자체 PnR flow**에 정확히 반영하고,
디자인별로 적합한 DTCO knob을 PnR 검증까지 거쳐 추천하는 agent 스킬 묶음.

```
고객 flow ─┐
           ├─▶ 1. 고객 flow 분석 ─▶ 2. infra 설정 반영 위치 ─▶ 3. 디자인별 항목 선택 ─▶ 4. PnR 검증
REF flow ──┘     (flow/design        (tool-agnostic,              (amenability,            (ablation +
DTCO 카탈로그      profile)             override 탐지)               유저 gate)                readback)
                                                                                              │
                                     ◀──────────── effect ledger 축적 ◀────────────────────────┘
```

최종 산출물: **고객 flow 수정안(overlay 방식)** + **디자인별 knob 추천(근거 레벨 포함)**.

---

## 설계 원칙

1. **판단은 LLM, 검증은 기계.**
   flow 구조 파악, 반영 위치 판단, 적합성 분류는 md 가이드를 읽은 LLM이 수행한다.
   Python은 아이템/flow를 모르는 기계적 검증 3종(validate / readback / ledger)만 담당한다.
   *새 아이템이나 새 flow 패턴 때문에 Python 코드를 고쳐야 한다면 설계가 틀린 것이다.*
2. **지식은 데이터에.** DTCO 항목 지식은 카탈로그(yaml), flow 관찰 노하우는 가이드(md),
   실측 결과는 ledger에 둔다.
3. **툴의 말이 최종.** override 판정은 파싱 추론이 아니라 stage 종료 시점 readback(툴이 보고하는 실효값)으로 확정한다.
4. **인용 없는 주장은 무효.** LLM이 "file:line에 knob이 있다"고 하면 그 줄에 실제로 해당 문자열이 있어야 한다.
5. **고객 flow 비침습.** 수정안은 stage hook에 `source` 한 줄 + overlay 파일 방식. 원본 로직은 고치지 않는다.
6. **모르면 ASK.** 카탈로그/ledger의 모르는 필드는 추론으로 채우지 않는다.
   reference script가 없는 툴의 binding은 생성하지 않는다(`absent`).

## 구성

| 구분 | 이름 | 역할 |
|---|---|---|
| 메인 스킬 | `flow-bridge` | 4단계 flow 라우팅 (thin router) |
| 카탈로그 스킬 | `dtco-catalog-builder` | infra와 이터레이션해 DTCO 카탈로그 + REF flow 구조 md 작성 |
| main agent | `bridge-pilot` | 전체 flow 진행, 유저 gate 3개, 결과 분석 |
| sub-agent | `flow-mapper` | 고객 flow / design 읽기 → profile 생성 (read-only) |
| sub-agent | `ledger-curator` | ledger + 관찰 가이드 쓰기 전담 (writer 1인) |
| sub-agent (재사용) | `pnr-rundori` | ablation run 실행/폴링 (기존 구현 연결) |

## 디렉토리

```
flow-bridge/
├── README.md
├── HANDOFF.md                  # 사내 opencode 작업 가이드            (P5)
├── prompts/                    # 사내 opencode 단계별 프롬프트 H0~H6  (P5)
├── config/env.yaml             # 환경 의존값 단일 집약
├── schema/                     # 정규화 스키마 (Step 0)
│   ├── stage_taxonomy.yaml
│   ├── knob.schema.yaml
│   ├── catalog_item.schema.yaml
│   ├── flow_profile.schema.yaml
│   ├── design_profile.schema.yaml
│   ├── ledger_entry.schema.yaml
│   ├── common.schema.yaml      # citation 등 공용 정의
│   └── contract/               # 단계 간 handoff 포맷
├── examples/                   # 가상 데이터 예시 (실제 고객/infra 데이터 금지)
├── .opencode/                  # 스킬 + 에이전트                      (P2, P3)
├── tools/                      # validate / readback / ledger         (P4)
└── tests/                      # 가상 fixture 기반 테스트             (P4)
```

## 마커 규칙 (사내 작업용)

| 마커 | 의미 | 처리 |
|---|---|---|
| `TODO(INHOUSE): <무엇을, 왜>` | 사내 환경 지식이 있어야 확정 가능한 곳 | `grep -rn "TODO(INHOUSE)"`로 목록화 → 사내 opencode가 채움 |
| `ASK` | 사람(infra 담당자 / 유저)의 답이 필요한 데이터 필드 | 추론으로 채우기 금지. 답을 받으면 교체 |
| `absent` | 해당 툴 binding이 의도적으로 없음 | 그 툴의 reference script가 생기면 그때 채움 |

## 보안 규칙

- 이 repo에는 **가상 데이터만** 둔다. 실제 고객 flow, infra 스크립트, 디자인 정보, 카탈로그 실내용은 사내에만 둔다.
- 실데이터 저장 위치는 `config/env.yaml`의 `paths.*`로 지정(사내 경로).

## 진행 상태

| Phase | 내용 | 상태 |
|---|---|---|
| P1 | 골격 + Step 0 스키마 | 완료 |
| P2 | dtco-catalog-builder | 예정 |
| P3 | flow-bridge 스킬 + 에이전트 + 관찰 가이드 | 예정 |
| P4 | Python validate / readback / ledger | 예정 |
| P5 | HANDOFF + 프롬프트 H0~H6 | 예정 |
