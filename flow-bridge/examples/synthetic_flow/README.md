# synthetic_flow (가상 고객 flow)

flow-bridge 예시/테스트용으로 만든 **가상** Innovus(legacy UI) flow. 실제 고객 flow가 아니며,
커맨드는 구조 설명용 예시다 (옵션 정확성은 보장하지 않음).

의도적으로 넣은 함정:
- `stages/05_route.tcl`에서 `apply_design_overrides` proc 호출 → design override 파일이
  post_route 직전에 `setOptMode -usefulSkew`를 덮어씀 (override 탐지 예시).
- `common/settings.tcl`의 foreach 루프로 여러 mode를 일괄 설정 (loop 경유 설정 예시).
- `hooks/` 디렉토리 기반 공식 hook 슬롯 (official_hook 예시).
