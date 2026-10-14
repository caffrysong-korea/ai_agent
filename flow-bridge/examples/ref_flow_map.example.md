# REF flow map — synth_ref_v1 (example)

> 작성: dtco-catalog-builder 모드 A / 2026-10-14  (**가상 예시** — 모드 A 산출물의 기대 수준을 보여주기 위한 샘플)
> REF profile: (예시에서는 생략)
> 규칙: 위치는 모두 `file:line` 형식. 확인 못한 것은 7절에. 섹션 순서/컬럼 변경 금지.

## 1. 개요

| 항목 | 값 |
|---|---|
| flow_id | synth_ref_v1 |
| 버전 식별자 | example |
| tool / ui_mode | innovus / legacy |
| entry script | run_ref.tcl |
| 템플릿 생성 여부 | 아니오 |
| 참고한 infra 자료 | 없음 |

## 2. Stage 지도

| abstract_stage | REF stage 이름 | 시작 (file:line) | 끝 (file:line) | 주요 파일 |
|---|---|---|---|---|
| init | flags + procs | run_ref.tcl:3 | run_ref.tcl:4 | dtco_flags.tcl, ref_procs.tcl |
| floorplan | (없음) | — | — | — |
| place | place | stages/place.tcl:2 | stages/place.tcl:5 | stages/place.tcl |
| cts | cts (ccopt) | stages/cts.tcl:2 | stages/cts.tcl:2 | stages/cts.tcl |
| post_cts | cts (postCTS opt) | stages/cts.tcl:3 | stages/cts.tcl:6 | stages/cts.tcl |
| route | (없음) | — | — | — |
| post_route | (없음) | — | — | — |

## 3. DTCO toggle 메커니즘

| 패턴 | 이름 | 정의 위치 | 기본값 | 비고 |
|---|---|---|---|---|
| 플래그 변수 + if | DTCO_USKEW | dtco_flags.tcl:2 | 1 | 사용처 stages/cts.tcl:3 |
| 플래그 변수 + if | DTCO_DONTUSE_D0 | dtco_flags.tcl:3 | 1 | 사용처 stages/place.tcl:2 |

## 4. 항목 후보

| # | 후보 이름 | toggle | stage | 설정 줄 (file:line) | sticky | requires | REF 주석 |
|---|---|---|---|---|---|---|---|
| 1 | useful skew | DTCO_USKEW | post_cts | stages/cts.tcl:4 | sticky | 없음 | "useful skew - timing 개선용" (dtco_flags.tcl:2) |
| 2 | D0 don't use | DTCO_DONTUSE_D0 | place | stages/place.tcl:3 | unknown | ref_dont_use_weak | 없음 |

### 4.1 useful skew

```tcl
# stages/cts.tcl:4
setOptMode -usefulSkew true
```

- 의존 proc/변수/파일: 없음 (툴 내장 커맨드)
- 다른 후보와의 관계: 없음
- 위치 특징: `ccopt_design`(cts.tcl:2) 이후, `optDesign -postCTS`(cts.tcl:6) 이전 → post-CTS opt에 영향을 주려는 배치

### 4.2 D0 don't use

```tcl
# stages/place.tcl:3
ref_dont_use_weak *D0*
# ref_procs.tcl:3 (proc 본체)
setDontUse $pattern true
```

- 의존 proc/변수/파일: `ref_dont_use_weak` (ref_procs.tcl:2에 정의된 REF 전용 proc)
- 다른 후보와의 관계: 없음
- sticky 판정 unknown 사유: don't use 속성이 이후 stage에서 해제되는지 REF 안에서 확인 불가

## 5. 항목 간 관계

| 관계 | 후보 A | 후보 B | 근거 (file:line) |
|---|---|---|---|
| (없음) | | | |

## 6. REF 전용 전제

| 요소 | 종류 | 정의 위치 | 쓰는 후보 |
|---|---|---|---|
| ref_dont_use_weak | proc | ref_procs.tcl:2 | #2 |
| DTCO_USKEW / DTCO_DONTUSE_D0 | 변수 | dtco_flags.tcl:2-3 | #1, #2 (toggle 자체이므로 고객 flow에는 불필요) |

## 7. unresolved

| 무엇 | 왜 | 다음 조치 |
|---|---|---|
| #2의 의도와 대상 cell 범위 | REF에 주석/자료 없음 | 모드 C 질문 |
| #2 don't use 지속 여부 | REF 내 해제 로직 확인 불가 | 4단계 readback 또는 infra 질문 |
| floorplan / route / post_route stage 부재 | 예시 REF flow 범위 한정 | 실제 REF에서는 해당 없음 |
