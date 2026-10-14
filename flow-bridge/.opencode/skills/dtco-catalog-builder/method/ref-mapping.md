# Mode A — REF 매핑

목표: REF flow를 읽고 **"REF flow 구조 + DTCO toggle 지도"(REF map md)** 를 만든다.
이 문서는 모드 B(항목 추출)의 유일한 입력이고, 사람이 읽어도 REF flow 구조를 파악할 수 있어야 한다.

---

## A1. 입력 확인

시작 전에 아래가 모두 확보됐는지 확인한다. 하나라도 없으면 사용자에게 묻고 멈춘다.

| 입력 | 비고 |
|---|---|
| REF flow 루트 경로 | 읽기 전용 |
| entry script | flow가 시작되는 파일 |
| tool / ui_mode | 첫 타겟은 Innovus. legacy / stylus / mixed |
| REF flow 버전 식별자 | 커밋, 릴리즈 태그, 디렉토리 날짜 등. 모드 D 비교 기준 |
| (있으면) infra 설명 자료 | 항목 목록, 슬라이드, 메일 등. **REF flow와 다르면 REF flow를 사실로 보고 차이를 unresolved에 기록** |

## A2. REF profile 생성 (flow-mapper 위임)

- SKILL.md 4절 규약대로 flow-mapper를 호출한다. `flow_kind: reference`.
- manifest의 status가 `failed`면 멈추고 보고. `partial`이면 unresolved를 REF map 7절에 그대로 옮긴다.

## A3. Toggle 메커니즘 탐색

REF flow가 DTCO 항목을 켜고 끄는 방식을 찾는다. **이 방식이 곧 "항목 하나"의 경계다.**
아래 패턴을 순서대로 확인하고, 발견한 패턴은 전부 기록한다 (한 REF flow에 여러 패턴이 섞일 수 있다).

| 패턴 | 찾는 신호 | 기록할 것 |
|---|---|---|
| 플래그 변수 + if | `if {$<FLAG>}`, `if {[info exists <FLAG>] && ...}` | 플래그 이름, 정의 위치, 기본값 |
| 항목별 파일 조건부 source | `if {...} { source <item>.tcl }` | 파일 목록, 조건 |
| 활성 목록 순회 | `foreach item $<LIST>` + 항목별 분기 | 목록 정의 위치, 분기 방식 |
| proc 인자 | `proc apply_xxx {enable}` | proc 정의 위치, 호출 위치 |
| 주석 토글 | 주석 처리된 설정 블록 + "enable/disable" 류 주석 | 수동 토글로 표시 |
| 환경변수 | `$env(<VAR>)` 분기 | 변수 이름 |
| **템플릿 생성** | `__PLACEHOLDER__` 토큰, python/csh가 TCL을 생성 | 템플릿 파일 + 치환 값 출처(config) + 생성 결과물 위치 |

**템플릿 생성 flow 주의**: 실제 실행되는 TCL은 생성 결과물이다. 템플릿만 읽으면 값이 없고, 결과물만 읽으면 어디서 바꾸는지 모른다.
둘 다 확인하고, 생성 결과물이 없으면 unresolved에 "생성 결과물 미확인"으로 남긴다.

## A4. 항목 후보 정리

toggle 하나(=infra가 켜고 끄는 단위)마다 후보 하나를 만든다. 한 toggle이 여러 설정을 걸면 후보 하나에 설정 여러 줄.

후보마다 확인할 것:
1. **설정 줄**: toggle이 켜졌을 때 실행되는 커맨드 전부 (citation)
2. **stage**: profile의 stage_map 기준 abstract_stage
3. **sticky 여부**: mode/attribute 설정이면 sticky, 특정 커맨드 옵션이면 per_command, 모르면 unknown
4. **REF 전용 의존성(requires)**: 설정 줄이 쓰는
   - proc → REF flow 안에 `proc <이름>` 정의가 있으면 REF 전용
   - 변수 → REF flow 안에서 `set <이름>`으로 정의되면 REF 전용
   - 파일 → REF flow 디렉토리 안의 파일을 source/read하면 REF 전용
   툴 내장 커맨드인지 REF 정의 proc인지 확신이 없으면 unresolved에 남긴다.
5. **REF 주석**: 설정 근처 주석에 의도/효과가 적혀 있으면 원문 그대로 인용 (모드 C에서 확인 질문으로 사용)

## A5. 항목 간 관계

- 같은 knob을 다른 값으로 거는 후보 쌍 → 충돌 후보
- 한 후보가 다른 후보의 플래그/변수에 의존 → 순서 의존
- 동시에 켜지지 않도록 막는 로직(else 분기, 상호 배제 체크) → 상호 배제

## A6. REF map 작성

- templates/ref_flow_map.md 를 복사해 채운다. 섹션 순서와 표 컬럼은 바꾸지 않는다.
- 저장 위치: `paths.ref_flow_maps` / `<flow_id>__<버전>.md`
- 모든 위치 정보에 citation. 표 셀에 `file:line` 형식으로 넣는다.

## A7. 자기 점검 (보고 전 필수)

- [ ] A3에서 찾은 toggle 수 = A4 후보 수 (다르면 이유를 7절에 기록)
- [ ] 모든 후보에 stage 지정 (매핑 불가는 unresolved)
- [ ] requires 판정이 모든 후보에 있음 (없음 = 빈 목록으로 명시)
- [ ] REF profile의 validate 통과 (flow-mapper manifest의 validate_passed)
- [ ] infra 설명 자료와 REF flow의 차이를 기록했음

## A8. 보고

SKILL.md 6절 형식. [결과]에는 toggle 패턴 종류, 후보 수, REF 전용 의존성이 있는 후보 수를 넣는다.
