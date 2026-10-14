# HANDOFF — 사내 opencode에서 이어가기

이 repo에는 **골격과 규칙**만 있다. 사내 환경 값, 실제 데이터, 문법 확정은 사내 opencode가 아래 순서로 채운다.
프롬프트는 `prompts/` 폴더의 파일을 **순서대로 하나씩** 붙여넣는다. 한 단계가 끝나면 결과를 확인하고 다음으로 간다.
프롬프트 안의 `$FB_ROOT`는 `<AGENT_HOME>/flow-bridge` 실제 경로로 바꿔서 붙여넣는다.

## 순서

| 단계 | 프롬프트 | 하는 일 | 끝난 기준 |
|---|---|---|---|
| H0 | prompts/H0_inspect.md | 점검: TODO 목록, 테스트, 기존 에이전트 공간과 차이 | 리포트 받음 (수정 0건) |
| H1 | prompts/H1_bind_env.md | 환경 값, frontmatter, 경로 채우기 | `grep -rn "TODO(INHOUSE)"` 중 H1 대상 0건 |
| H2 | prompts/H2_registration.md | 에이전트 등록 + 위임 실호출 | 3개 에이전트 모두 실제 호출 성공 (모사 아님) |
| H3 | prompts/H3_readback_check.md | readback 커맨드 사내 Innovus 검증 | 카드 템플릿/예시 readback `verified: true` 또는 수정됨 |
| H4 | prompts/H4_first_cards.md | 기존 평가 run으로 첫 카드 | 카드 1개 이상 approved |
| H5 | prompts/H5_map_and_place.md | 고객 flow 1개로 1~2단계 | gate ① 표 받음 |
| H6 | prompts/H6_select_and_verify.md | 3~4단계 라이브 | report.md + 카드에 `bridge` 행 추가 |

## 설치 (H0 전에 한 번)

opencode는 지금처럼 **스킬/에이전트를 모아둔 공간(이하 AGENT_HOME)** 에서 실행한다.
flow-bridge는 그 공간에 **추가(append)만** 한다. 기존 `.opencode` 내용을 갈아끼우지 않는다.

```
<AGENT_HOME>/                      ← 여기서 opencode 실행 (기존 그대로)
├── .opencode/
│   ├── skills/  ← 기존 스킬 + flow-bridge/, dtco-catalog-builder/ 추가
│   └── agents/  ← 기존 에이전트 + bridge-pilot.md, flow-mapper.md, card-curator.md 추가
└── flow-bridge/                   ← 나머지 (config, schema, tools, examples, tests, prompts) = $FB_ROOT
```

```csh
# 받은 zip/clone 위치와 AGENT_HOME을 실제 경로로
set SRC = ~/work/ai_agent-main/flow-bridge
set AH  = <AGENT_HOME>

# 1) 이름 충돌 먼저 확인 ("No such file"만 나오면 정상. 이미 있다고 나오면 멈추고 이름 확인)
ls -d $AH/.opencode/skills/{flow-bridge,dtco-catalog-builder} $AH/.opencode/agents/{bridge-pilot,flow-mapper,card-curator}.md

# 2) 스킬/에이전트만 골라서 추가 (-n: 같은 이름 파일이 있으면 덮어쓰지 않음)
cp -rn $SRC/.opencode/skills/flow-bridge          $AH/.opencode/skills/
cp -rn $SRC/.opencode/skills/dtco-catalog-builder $AH/.opencode/skills/
cp -n  $SRC/.opencode/agents/{bridge-pilot,flow-mapper,card-curator}.md $AH/.opencode/agents/

# 3) 나머지는 flow-bridge 폴더로 (.opencode는 빼고)
mkdir -p $AH/flow-bridge
cp -rn $SRC/{config,schema,tools,examples,tests,prompts,README.md,HANDOFF.md} $AH/flow-bridge/

# 4) 확인
python3 $AH/flow-bridge/tests/test_tools.py
```

- 스킬/에이전트 폴더 이름이 `skills`/`agents`가 아니면 기존 공간의 이름에 맞춰 넣는다.
- 그다음 두 SKILL.md의 "위치"에 있는 `FB_ROOT` 한 줄을 `$AH/flow-bridge`의 절대경로로 바꾼다 (H1에서 함께 처리해도 됨).

## 미리 준비할 것

- 기존 공간에서 참고할 것: 동작이 확인된 agent `.md` 1개, pnr-rundori 입력 형식, QoR 요약 파일 형식
- H4용: 어떤 DTCO 항목 평가인지 알고 있는 run 쌍 1~2개 (baseline + 항목 on)
- H5용: 고객 flow 1개 + 디자인 1개

## 단계마다 지킬 것

- **요청한 것만 한다.** 다음 단계 진행, 리팩토링, 추가 테스트 금지. 개선 아이디어는 보고에 "제안"으로만.
- **AGENT_HOME의 기존 스킬/에이전트 파일은 수정하지 않는다.** pnr-rundori 등은 호출만.
- **실데이터는 이 repo(public)로 되돌려 보내지 않는다.** 사내 위치에만 둔다.
- 각 단계 끝에 `python3 $FB_ROOT/tests/test_tools.py`가 계속 통과하는지 확인.

## TODO(INHOUSE) 분류

`grep -rn "TODO(INHOUSE)" $FB_ROOT/ <AGENT_HOME>/.opencode/skills/{flow-bridge,dtco-catalog-builder} <AGENT_HOME>/.opencode/agents/{bridge-pilot,flow-mapper,card-curator}.md` 결과를 아래처럼 나눠서 처리한다.

| 분류 | 위치 예 | 처리 단계 |
|---|---|---|
| 환경 값 (모델, 경로, 래퍼, run_data) | config/env.yaml | H1 |
| frontmatter / permission 문법 | .opencode/agents/*, SKILL.md | H1 |
| `FB_ROOT` 경로 | 두 SKILL.md "위치" | H1 (설치 직후 해도 됨) |
| 위임 호출 문법 | SKILL.md 위임 규약 | H2 |
| readback 커맨드 검증 | 카드 템플릿, 예시 카드 | H3 |
| pnr-rundori 연결, noise band, ppa-booster 연결 | env.yaml execution/policy, 4-verify.md | H6 직전 |
