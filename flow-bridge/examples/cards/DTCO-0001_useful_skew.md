---
item_id: DTCO-0001
name: useful_skew
version: 1
status: draft
category: dm
stage: post_cts
settings:
  - variant: invs_legacy
    set: "setOptMode -usefulSkew true"
    readback: "getOptMode -usefulSkew"
    expect: "true"
    sticky: "yes"
    requires: []
    verified: false
conflicts_with: []
---
# DTCO-0001 post-CTS useful skew

## 요약
post-CTS optimization 전에 useful skew를 켠다. (**가상 예시 카드** — examples/synthetic_runs 기반)

## 설정
```tcl
# examples/synthetic_runs/blkA_uskew_on/innovus.cmd:9
setOptMode -usefulSkew true
```
- 켜고 끄는 방식: 미확인 (cmd log에는 실행 결과만 남음 → 질문 Q1)
- stage 근거: `ccopt_design`(줄 8) 다음, `optDesign -postCTS`(줄 10) 전에 실행 → post_cts
- 확인한 run: blkA_base → blkA_uskew_on (clean diff, 경로/날짜 차이 외 위 한 줄만 다름)

## 평가 결과
| id | 날짜 | ver | 출처 | 디자인 | 조건 | fmax% | WNS | TNS | power% | area% | 판정 | run | 비고 |
|----|------|-----|------|--------|------|-------|-----|-----|--------|-------|------|-----|------|
| R-001 | 2026-10-14 | 1 | eval | blkA | 2.0GHz, util 0.70 | +2.05 | +0.012 | +0.90 | +1.00 | 0.00 | positive | blkA_base → blkA_uskew_on | |
| R-002 | 2026-10-14 | 1 | eval | blkB | 1.5GHz, util 0.65 | - | - | - | - | - | invalid | blkB_base → blkB_uskew_on | confounded: place_global_cong_effort medium→high 동시 변경 |

## 해석
근거 부족 (유효 결과 행 1개: R-001).
- R-001: 고주파 블록(blkA)에서 fmax +2.05%, power +1.00%. 한 디자인뿐이라 일반화 불가.
- R-002는 다른 설정이 섞여 해석에서 제외.

## 고객 flow 이식 주의
- REF 전용 의존성: 없음 (툴 내장 커맨드)
- 덮어쓰기 위험: sticky 설정. 고객 flow가 post_route 등 이후 stage에서 `-usefulSkew`를 다시 설정하는지 확인 필요

## 질문
- Q1. REF flow에서 이 항목을 켜고 끄는 방식 (플래그 이름 등)
- Q2. blkB를 useful skew 단독으로 다시 평가할 수 있는지 (R-002 invalid)

## 이력
- 2026-10-14 카드 생성 (blkA_base → blkA_uskew_on, blkB_base → blkB_uskew_on)
