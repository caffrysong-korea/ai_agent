# REF flow map — <flow_id> (<버전>)

> 작성: dtco-catalog-builder 모드 A / <날짜>
> REF profile: <경로>
> 규칙: 위치는 모두 `file:line` 형식. 확인 못한 것은 7절에. 섹션 순서/컬럼 변경 금지.

## 1. 개요

| 항목 | 값 |
|---|---|
| flow_id | |
| 버전 식별자 | |
| tool / ui_mode | |
| entry script | |
| 템플릿 생성 여부 | 예 / 아니오 (예면 템플릿 → 생성물 경로) |
| 참고한 infra 자료 | |

## 2. Stage 지도

| abstract_stage | REF stage 이름 | 시작 (file:line) | 끝 (file:line) | 주요 파일 |
|---|---|---|---|---|
| init | | | | |
| floorplan | | | | |
| place | | | | |
| cts | | | | |
| post_cts | | | | |
| route | | | | |
| post_route | | | | |

## 3. DTCO toggle 메커니즘

| 패턴 | 이름 (플래그/파일/목록/proc/env) | 정의 위치 | 기본값 | 비고 |
|---|---|---|---|---|
| | | | | |

## 4. 항목 후보

| # | 후보 이름 | toggle | stage | 설정 줄 (file:line) | sticky | requires | REF 주석 |
|---|---|---|---|---|---|---|---|
| 1 | | | | | sticky / per_command / unknown | 없음 / 목록 | 원문 인용 또는 없음 |

### 4.x 후보 상세 (후보마다 하나)

```tcl
# 설정 줄 원문 (REF flow에서 그대로 복사, file:line 주석 포함)
```

- 의존 proc/변수/파일:
- 다른 후보와의 관계:

## 5. 항목 간 관계

| 관계 | 후보 A | 후보 B | 근거 (file:line) |
|---|---|---|---|
| 충돌 / 순서 의존 / 상호 배제 | | | |

## 6. REF 전용 전제

고객 flow에 없을 가능성이 높은 REF 전용 요소. 2단계(반영 위치)에서 고객 flow 존재 여부를 확인할 목록.

| 요소 | 종류 (proc/변수/파일/env) | 정의 위치 | 쓰는 후보 |
|---|---|---|---|
| | | | |

## 7. unresolved

| 무엇 | 왜 | 다음 조치 |
|---|---|---|
| | | |
