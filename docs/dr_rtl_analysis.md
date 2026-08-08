# Dr_RTL 분석 → PnR PPA 에이전트 구조 이식안

대상: `hkust-zhiyao/Dr_RTL` (ICCAD'26, *Autonomous Agentic RTL Optimization through Tool-Grounded Self-Improvement*)
목적: Dr_RTL의 에이전트/스킬 구조 중 **PnR PPA 분석·최적화에 그대로 쓸 수 있는 것**과 **반드시 바꿔야 하는 것**을 분리한다.

---

## 1. Dr_RTL 실제 구조 (파일 기준)

```
Dr_RTL/
├── CLAUDE.md                       # 오케스트레이터 규칙 = 루프/스코어/종료조건 (162줄)
├── .claude/agents/                 # 서브에이전트 5종
│   ├── rtl-timing-analyzer.md      # 진단 전용 (opus)
│   ├── rtl-optimizer.md            # 처방 전용 (opus)
│   ├── rtl-synthesis-evaluator.md  # 실행 전용 (haiku, 32줄)
│   ├── rtl-opt-skill-extractor.md          # 크로스 디자인 스킬 추출
│   └── rtl-opt-skill-extractor-per-design.md
├── .claude/skill/rtl-opt/skill.md  # 지식 스킬 팩 (803줄, 47개 패턴)
├── rtl_dataset/                    # 베이스라인 RTL 20종 (aes, tv80, pcie, i2c, arm_cpu...)
├── syn_flow/                       # 로컬 루프 작업 디렉토리
│   ├── rtl/  log/  history/  output/
│   └── run_remote.py               # paramiko+scp로 EDA 서버에 던지는 래퍼
└── syn_flow_eda/                   # EDA 머신에서 도는 쪽
    ├── run_design.py               # dc_shell → fm_shell → jaspergold 오케스트레이션 + 리포트 파싱
    └── scr/{syn,fm,sec}.tcl
```

핵심은 **1개의 오케스트레이터 CLAUDE.md + 5개의 좁은 서브에이전트 + 1개의 지식 스킬 + 2종류의 JSON 메모리**다.
코드는 얇고(`run_design.py` 424줄이 전부), 무게중심은 전부 마크다운 계약서에 있다.

---

## 2. 그대로 훔쳐올 것 (High value, PnR에 직결)

### 2.1 진단 / 처방 / 실행의 3분할

가장 중요한 설계 결정. 세 에이전트의 경계가 칼같이 그어져 있다.

| 에이전트 | 모델 | 역할 | 명시적 금지사항 |
|---|---|---|---|
| `rtl-timing-analyzer` | opus | **왜/어디서** 실패하는지만 | "Do NOT run any tools" |
| `rtl-optimizer` | opus | **어떻게** 고칠지만 | "Do NOT predict SEC or PPA results" |
| `rtl-synthesis-evaluator` | **haiku** | 명령 1줄 실행만 | "Do NOT read any files / summarize / interpret / retry" |

실행 에이전트가 haiku이고 32줄인 게 포인트다. 툴을 돌리는 놈이 결과를 **해석하지 못하게 막아서**, 해석은 반드시 파일에 기록된 실측치를 통해서만 일어나게 강제한다. LLM이 "타이밍이 개선된 것 같습니다"라고 말할 경로 자체를 구조적으로 제거한 것.

> **PnR 이식**: `pnr-run-executor`(haiku, Innovus/ICC2 실행만) / `pnr-bottleneck-analyzer`(진단) / `pnr-recipe-optimizer`(처방). 특히 PnR은 런 1회가 수 시간이라 "돌려보지도 않고 좋아졌다고 말하는" 실패 모드가 RTL보다 훨씬 치명적이다.

### 2.2 신뢰도 4단계 + 안티패턴이 1급 시민인 스킬 라이브러리

`skill.md` 47개 패턴의 구성:

- **High-confidence** (1–12): 조건 사전계산, one-hot 프리디코드, CSE, 팬아웃 복제
- **Medium-confidence** (13–28): mux/트리 재구성, case 평탄화
- **Low-confidence** (29–34): 공격적 산술 재구성 — "한 번에 하나씩 실험으로만"
- **Do not use** (35–47): 13개. 카운터 방향 뒤집기, priority 체인을 상호배타 보장 없이 평탄화, 타이밍만 보고 셀렉터 프리레지스터링 등

각 항목은 `<pattern, strategy, example>` 3종 세트 + before/after Verilog 스니펫.

**Do-not-use 섹션이 전체 47개 중 13개(28%)**라는 게 핵심이다. LLM은 PnR에서도 그럴듯하고 틀린 처방을 잘 낸다 — "utilization 타겟 올려라", "버퍼 더 박아라", "그냥 라우팅 effort high로". 안티패턴을 증거와 함께 명시적으로 박아두는 게 지식 스킬의 절반 이상의 가치다.

마지막 "Practical usage notes"의 원칙 두 줄이 특히 이식 가치가 높다:
> prefer **pre-computation over restructuring**, and **local simplification over architectural rewrites**.

PnR 버전으로 번역하면: **레시피 조정 > 플로어플랜 재설계**, **국소 수정 > 전역 재구성**.

### 2.3 Amenability 분류 (진단이 처방의 범위를 미리 자름)

analyzer가 각 패스를 4단계로 라벨링한다:

| 분류 | optimizer 액션 |
|---|---|
| combinational | 고칠 수 있음 |
| sequential-safe (레이턴시 불변) | 고칠 수 있음 |
| sequential-unsafe (레이턴시 변경 필요) | **skip** |
| out-of-scope (제약/재설계 필요) | **skip** |

진단자가 "이건 네 권한 밖"이라고 미리 잘라주기 때문에, optimizer가 아키텍처를 건드리는 폭주를 막는다.

> **PnR 이식**이 가장 자연스러운 부분. PnR 병목의 amenability:
> - `placement-fixable` — 셀 배치/리전 제약으로 해결
> - `cts-fixable` — 클럭 스큐/스큐 그룹 조정
> - `route-fixable` — NDR, 레이어 승격, 디투어 제거
> - `constraint-issue` — SDC 자체가 틀림 (false path 누락, 과도한 마진) → **PnR 밖, 리포트만**
> - `rtl-issue` — 로직 깊이 자체 문제 → **PnR 밖, RTL 팀에 에스컬레이션**
>
> PnR 엔지니어의 실무 시간 상당량이 "이건 내 문제가 아니다"를 증명하는 데 들어간다. 이 라벨링을 에이전트가 자동으로 붙이면 그 자체로 가치가 있다.

### 2.4 파일 기반 메모리 (에이전트 컨텍스트 아님)

CLAUDE.md에 못 박혀 있다: **"Sub-agents have no memory between invocations."**

메모리는 전부 두 종류의 JSON이다.

- `log/<design>.<version>.iter.json` — 시도 1회의 전체 기록: diversity 전략, 선택된 크리티컬 패스 K개(각각 slack/startpoint/endpoint/root_cause/amenability/적용된 최적화), 실행 결과, 스코어 분해
- `history/<design>.history.json` — 디자인 단위 누적: baseline PPA, best_version, major 라운드별 minor 목록과 promote 여부, end_reason

에이전트는 매번 백지에서 시작해서 필요한 JSON만 읽는다. 컨텍스트 오염도 없고, 나중에 스킬 추출기가 통째로 마이닝할 수 있는 정형 데이터가 공짜로 쌓인다.

> **PnR 이식**: 이게 PnR에서 오히려 더 값지다. 런 1회가 수 시간이므로 **모든 런의 메타데이터를 구조화해서 남기는 것**이 곧 자산이다. `run.json`(런 1회) + `block_history.json`(블록 단위 누적).

### 2.5 자기개선 플라이휠 — 스킬 추출기

`rtl-opt-skill-extractor`가 완료된 궤적을 마이닝해서 `skill.md`를 갱신한다. 하드 제약이 훌륭하다:

```
- Only extract patterns with >= 3 occurrences
- Include both successes AND failures
- Do NOT invent patterns without evidence
- Always cite evidence (design, version)
```

per-design 버전은 승격/미승격을 비교해서 anti-pattern 판정 기준까지 수치로 정의한다:
- **winning**: promotion ≥ 1회, 또는 SEC pass rate ≥ 80% AND avg score < -0.1
- **anti-pattern**: SEC fail rate ≥ 50%, 또는 never promoted AND avg score > 0

그리고 diversity 전략 자체도 promotion rate로 랭킹해서, 다음 라운드의 탐색 전략을 데이터로 고른다.

> **PnR 이식**: 그대로. 다만 occurrence 임계값 3은 런 비용 때문에 채우기 어려우므로 **디자인 간(cross-block) 집계**를 전제로 해야 한다. 블록 1개로는 절대 3회를 못 채운다.

### 2.6 단일 스칼라 스코어 + 페널티

```
score = 0.5·WNS_norm + 0.35·TNS_norm + 0.15·Area_norm + penalty
penalty = 0.5 if Area_norm > 0.10 else 0
```

모두 baseline(v0) 대비 정규화. 낮을수록 좋음. 다목적 문제를 **단일 스칼라 + 하드 페널티**로 눌러서 "best-of-5 고르기"를 단순 비교로 만든 게 핵심이다. Area는 가중치 0.15로 작지만 10% 넘으면 0.5짜리 절벽 페널티 — 소프트 가중치와 하드 가드레일을 섞었다.

---

## 3. 그대로 쓰면 안 되는 것 (PnR에서 깨지는 부분)

### 3.1 SEC(형식 등가검증) 게이트는 PnR에 대응물이 없다 — 그리고 필요도 없다

Dr_RTL의 correctness gate는 Jasper SEC이다. RTL을 **텍스트로 고쳐쓰기** 때문에 기능이 깨질 수 있고, 그래서 매 시도마다 등가성 증명이 필수다.

PnR은 다르다. 플로어플랜/제약/툴 옵션을 바꿔도 **논리 기능은 정의상 안 바뀐다**. 대신 게이트가 물리적 제약으로 바뀐다:

| Dr_RTL | PnR 대응 |
|---|---|
| SEC pass/fail | DRC = 0 AND LVS clean |
| (없음) | max_tran / max_cap / max_fanout 위반 = 0 |
| (없음) | congestion overflow < 임계값 |
| (없음) | IR drop / EM 게이트 |

**게이트를 통과 못 하면 score = null, 승격 후보에서 제외** — 이 구조는 그대로 유지한다.

### 3.2 런 비용이 100~1000배 — 탐색 스케줄을 통째로 다시 짜야 한다

Dr_RTL: 10 major × 5 minor = **최대 50회 합성**. 소형 디자인 DC 합성은 분 단위라 성립한다.
PnR: 풀 P&R 1회가 수 시간~수일. 50회는 불가능하다.

이식할 때의 재설계:

**(a) 스테이지 조기종료(early-abort) 계층화**
```
Tier 0  place만 (30분~1시간)  → congestion / placement WNS로 사전 스크리닝
Tier 1  place + CTS           → 스큐/클럭 파워 확인
Tier 2  full route + signoff  → 최종 스코어링
```
Tier 0에서 명백히 진 후보는 Tier 1로 안 올린다. Dr_RTL의 "5개 다 돌리고 best 고르기"를 **"5개를 싸게 돌려 2개로 줄이고, 2개만 비싸게 돌리기"**로 바꾼다.

**(b) 체크포인트 재시작**
라우팅 옵션만 바꾸는 minor는 post-CTS DB에서 restart. 전체 재실행 금지. → minor의 정의를 "**어느 스테이지부터 다시 도는가**"로 재정의해야 한다.

**(c) minor 개수 축소 + 병렬화**
5 minor 순차 → 3 minor 병렬(LSF/SGE 큐). Dr_RTL은 순차 실행을 전제하지만 PnR은 잡 스케줄러가 있으므로 병렬이 자연스럽다. 대신 오케스트레이터가 잡 상태 폴링을 해야 한다.

**(d) major 라운드 10 → 3~4**
현실적인 tapeout 일정에서 블록당 PnR 반복은 그 정도다.

### 3.3 최적화의 "단위"가 다르다 — 소스가 아니라 레시피

Dr_RTL의 optimizer는 `<design>.v0.1.v` 라는 **전체 RTL 파일**을 쓴다 ("Output full RTL file, not diff/patch").

PnR의 optimizer가 쓰는 건 **레시피**다:
- Tcl 옵션 델타 (place effort, congestion effort, opt 스위치)
- 플로어플랜 델타 (매크로 위치, 블로케지, 리전/펜스)
- 제약 델타 (MCMM 시나리오, uncertainty, path group 가중치)
- NDR / 레이어 룰

→ **출력물은 파일 전체가 아니라 baseline 대비 명시적 델타**여야 한다. 그래야 "무엇을 바꿔서 좋아졌는가"가 스킬 추출기에서 마이닝 가능해진다. Dr_RTL이 전체 파일을 쓰는 건 RTL은 diff가 의미론적으로 위험해서인데, PnR 레시피는 정반대다 — **델타가 곧 지식 단위**다.

### 3.4 탐색 공간이 이산 텍스트가 아니라 수치 노브 — DOE/BO를 섞을 수 있다

Dr_RTL의 diversity 전략은 순전히 LLM이 정한다 (path selection 6종 × optimization focus 3종). PnR은 상당수가 연속/이산 수치 파라미터(utilization, effort level, uncertainty, aspect ratio)라 **고전적 DOE나 베이지안 최적화가 LLM보다 잘한다**.

권장 하이브리드:
- **수치 노브** → 스크립트 기반 sweep/BO. LLM이 범위만 정한다.
- **구조적 판단** (매크로 배치 방향, 어느 path group을 밀 것인가, 어떤 병목 유형인가) → LLM 에이전트.

LLM에게 utilization 0.72 vs 0.74를 고르게 하는 건 낭비다.

### 3.5 스코어 가중치를 PnR용으로 다시 짜야 한다

Dr_RTL은 타이밍 85% + 면적 15%. PnR PPA는 파워가 1급 목표이고, 물리적 게이트가 추가된다.

제안 (블록 성격에 따라 조정):

```
score = 0.35·WNS_norm + 0.25·TNS_norm + 0.25·Power_norm + 0.15·Area_norm
      + penalty_congestion + penalty_util

penalty_congestion = 0.5 if overflow > 0.5%      else 0
penalty_util       = 0.5 if util > util_target + 0.03 else 0

하드 게이트 (미통과 시 score = null, 승격 불가):
  DRC == 0
  LVS clean
  max_tran / max_cap 위반 == 0
```

`X_norm = (X - X_baseline) / |X_baseline|`, 낮을수록 좋음 — Dr_RTL 규약 유지.

---

## 4. 제안 구조

### 4.1 스킬 2개로 분리 (지식 vs 도구)

현재 `pnr-python-util`은 **생성기 스킬**이다 — SVG 카드뉴스 + Python 뼈대 코드를 뽑는다. Dr_RTL의 `rtl-opt/skill.md`는 **지식 스킬**이다 — 패턴→전략→예제 사전이고 코드를 생성하지 않는다.

이 둘은 성격이 완전히 다르므로 **합치면 안 된다**. `pnr-python-util`은 그대로 두고, Dr_RTL 스타일 지식 스킬을 새로 판다.

```
~/.claude/skills/
├── pnr-python-util/       (기존 유지 — 파서/시각화 코드 생성)
└── pnr-ppa-opt/           (신규 — Dr_RTL rtl-opt 이식)
    ├── SKILL.md           신뢰도 4단계 인덱스 + 사용 원칙
    └── references/
        ├── timing.md      타이밍 병목 패턴 → 레시피
        ├── congestion.md  혼잡/라우터빌리티 패턴
        ├── power.md       파워 패턴
        └── antipatterns.md  "쓰지 말 것" + 증거
```

`SKILL.md`는 인덱스만 두고 상세는 references로 분리한다 — Dr_RTL은 803줄을 한 파일에 넣었는데, 이건 매번 전량 로드되므로 컨텍스트 낭비다. 이 부분은 **개선해서 이식**할 것.

각 항목 포맷은 Dr_RTL 규약 유지:
```markdown
### <병목 패턴>, <레시피 전략>, <예시>
- **Pattern**: 리포트에서 이렇게 보인다 (구체적 수치/시그니처)
- **Strategy**: 이렇게 바꾼다
- **Expected**: WNS +Xps, Power ±Y%, 런타임 영향
- **Risk**: low / medium / high
- **Evidence**: <block>.<run_id> 목록
- **Example**: before/after Tcl 또는 제약 스니펫
```

### 4.2 에이전트 5종

```
.claude/agents/
├── pnr-ppa-parser.md         (haiku) 리포트 → 정형 JSON. 해석 금지.
├── pnr-run-executor.md       (haiku) 잡 제출/폴링만. 파일 읽기·해석 금지.
├── pnr-bottleneck-analyzer.md (opus) 진단 + amenability 라벨링. 툴 실행 금지.
├── pnr-recipe-optimizer.md   (opus) 레시피 델타 생성. 결과 예측 금지.
└── pnr-skill-extractor.md    (opus) 궤적 → 스킬 갱신. 증거 없는 패턴 생성 금지.
```

Dr_RTL 대비 추가한 것은 `pnr-ppa-parser`다. Dr_RTL은 파싱을 `run_design.py`(Python)가 하는데, PnR은 툴/버전마다 리포트 포맷이 제각각이라 파싱 자체에 적응력이 필요하다. 단, **파싱만 하고 판단은 안 하도록** 계약을 좁게 쓴다.

각 에이전트 md의 필수 섹션 (Dr_RTL 규약):
`Inputs` → `Methodology` → `Output (JSON 스키마 전문)` → `Hard Constraints`
특히 **Hard Constraints에 금지사항을 명령형으로** 쓰는 게 Dr_RTL이 잘한 부분이다.

### 4.3 데이터 스키마

`log/<block>.<run_id>.run.json`
```json
{
  "block": "core_top",
  "base_run": "r0",
  "target_run": "r0.1",
  "stage_reached": "route",
  "recipe_delta": {
    "source": "learned",
    "changes": [
      {"category": "placement", "key": "congestion_effort", "from": "medium", "to": "high"},
      {"category": "floorplan", "key": "macro_u_dsp0.orient", "from": "R0", "to": "MY"}
    ]
  },
  "bottlenecks": [
    {
      "id": 1, "type": "timing", "slack": -0.083,
      "path_group": "reg2reg", "startpoint": "...", "endpoint": "...",
      "root_cause": "detour routing through congested region (x:120-180, y:340-390)",
      "amenability": "route-fixable"
    }
  ],
  "gates": {"drc": 0, "lvs": "clean", "max_tran_viol": 0},
  "metrics": {"wns": -0.083, "tns": -14.2, "power_mw": 412, "area_um2": 1.83e6,
              "util": 0.71, "overflow_pct": 0.3},
  "scoring": {"wns_norm": -0.31, "power_norm": 0.02, "penalty": 0, "score": -0.19},
  "runtime_h": 5.2
}
```

`history/<block>.history.json` — Dr_RTL `history.json`과 동형. baseline / best_run / major 라운드별 minor 목록 + promoted 플래그 + end_reason.

`recipe_delta`와 `bottlenecks[].amenability`가 스킬 추출기의 입력이 되는 지점이다. 이 두 필드가 구조화돼 있어야 플라이휠이 돈다.

### 4.4 오케스트레이터 CLAUDE.md 스켈레톤

Dr_RTL CLAUDE.md 162줄이 좋은 템플릿이다. PnR용 필수 섹션:

1. **Workflow** — major/minor 루프, 단 Tier 0/1/2 조기종료 포함
2. **Budget** — 최대 런 수, 최대 wall-clock, 큐 동시 실행 수 (Dr_RTL에 없는 항목, PnR엔 필수)
3. **Diversity Strategy** — 카테고리 목록(floorplan / placement / cts / route / constraint)과 "minor 간 카테고리 중복 금지" 규칙
4. **Scoring Formula** — §3.5
5. **Hard Gates** — DRC/LVS/max_tran
6. **Version Control** — r0 → r0.1..r0.3 → r1
7. **End Criteria** — max_major / no_improvement / **budget_exhausted**(추가)
8. **Agent Rules** — "오케스트레이터는 직접 툴을 돌리지 않는다", "서브에이전트는 호출 간 메모리가 없다"

---

## 5. 우선순위

지금 당장 가치 대비 비용이 좋은 순서:

1. **`pnr-ppa-opt` 지식 스킬** — 에이전트 루프 없이도 단독으로 유용하다. 특히 안티패턴 섹션. 실제 EDA 환경 연동이 전혀 필요 없다.
2. **`run.json` / `history.json` 스키마 + 파서** — 이미 돌린 런들을 소급해서 정형화해 두면 나중에 플라이휠의 연료가 된다. `pnr-python-util` 스킬로 파서를 뽑으면 된다.
3. **`pnr-bottleneck-analyzer` 에이전트** — amenability 라벨링만으로도 실무 가치가 크고, 읽기 전용이라 안전하다.
4. **루프 오케스트레이션** — EDA 잡 스케줄러 연동이 필요하므로 마지막. 여기서 Dr_RTL의 `run_remote.py`(paramiko+scp) 패턴이 직접 참고가 된다.
5. **스킬 추출기** — 2번이 데이터를 충분히 쌓은 뒤에.

---

## 6. 한 줄 요약

Dr_RTL에서 가져올 것은 RTL 최적화 지식이 아니라 **"진단/처방/실행을 분리하고, 실측만 믿고, 파일에 정형 궤적을 남기고, 그 궤적에서 증거 기반으로 스킬을 다시 뽑는" 루프 아키텍처**다.
반대로 SEC 게이트, 10×5 탐색 스케줄, 전체 파일 출력 규약은 PnR에서 그대로 쓰면 깨진다 — 각각 물리 게이트, 계층적 조기종료, 레시피 델타로 치환해야 한다.
