# H3 — readback 커맨드 검증

readback이 틀리면 4단계 판정 전체가 틀린다. 라이브 전에 사내 Innovus에서 한 번 확인한다.

---

flow-bridge의 readback 동작을 사내 Innovus에서 확인하자.

1. `flow-bridge/examples/cards/DTCO-0001_useful_skew.md`의 settings에 있는 `set` / `readback` 커맨드가 우리 Innovus 버전에서 동작하는지 확인할 방법을 계획해줘.
   - 기존 저장 db를 restore하는 등 **가장 가벼운 방법**으로. 새 PnR run을 돌리지 마.
   - Innovus 실행은 우리 실행 래퍼/pnr-rundori 방식만. 직접 호출 금지.
2. 내가 승인하면 실행해서 아래를 확인해:
   - `set` 실행 후 `readback` 출력값
   - `python3 flow-bridge/tools/readback.py gen ...`으로 만든 `readback_<stage>.tcl`을 source했을 때 로그에 `FB_READBACK|...|OK|...` 줄이 찍히는지
   - 그 로그로 `readback.py judge`가 `applied`를 내는지
3. 결과에 따라 템플릿/예시 카드의 readback 커맨드를 고치거나 `verified: true`로 바꾸는 계획을 보여줘 (수정은 승인 후).

보고 형식:
```
[set/readback] 동작함/안 함 (출력값)
[FB_READBACK 줄] 찍힘/안 찍힘
[judge] applied / 기타
[수정 계획] 한 줄
```
