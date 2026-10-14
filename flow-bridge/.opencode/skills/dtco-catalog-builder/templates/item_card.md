---
item_id: DTCO-XXXX
name: short_name
version: 1
status: draft
category: dm            # dtco / dm (모르면 이 줄 삭제)
stage: post_cts
settings:
  - variant: invs_legacy
    set: "<커맨드 원문>"
    readback: "<실효값 출력 커맨드, 모르면 이 줄 삭제>"
    expect: "<켜졌을 때 readback 출력>"
    sticky: "yes"       # yes / no / unknown
    requires: []
    verified: false
conflicts_with: []
---
# DTCO-XXXX <제목>

## 요약
<무엇을 바꾸는 항목인지 1~2줄>

## 설정
```tcl
# <run 경로>/<파일>:<줄>
<커맨드 원문>
```
- 켜고 끄는 방식: <플래그 / 별도 파일 / 기타>
- stage 근거: <어느 커맨드 앞/뒤에서 실행됐는지>
- 확인한 run: <baseline → treatment>

## 평가 결과
| id | 날짜 | ver | 출처 | 디자인 | 조건 | fmax% | WNS | TNS | power% | area% | 판정 | run | 비고 |
|----|------|-----|------|--------|------|-------|-----|-----|--------|-------|------|-----|------|

## 해석
근거 부족 (결과 행 N개)

## 고객 flow 이식 주의
- REF 전용 의존성: <없음 / 목록>
- 덮어쓰기 위험: <sticky면 이후 stage 재설정 여부 확인 필요>

## 질문
- <데이터로 알 수 없는 것, 없으면 "없음">

## 이력
- YYYY-MM-DD 카드 생성 (<run 쌍>)
