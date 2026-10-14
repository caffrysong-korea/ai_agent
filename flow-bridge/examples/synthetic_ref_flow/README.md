# synthetic_ref_flow (가상 infra REF flow)

dtco-catalog-builder 모드 A/B 예시용 **가상** REF flow. 실제 infra 스크립트가 아니다.

의도적으로 넣은 요소:
- 플래그 변수 + if 패턴 toggle (`dtco_flags.tcl`)
- REF 전용 proc 의존 (`ref_dont_use_weak` → 고객 flow에 없으면 overlay가 깨짐)
- REF 주석 ("timing 개선용") → intent 확인 질문 대상
