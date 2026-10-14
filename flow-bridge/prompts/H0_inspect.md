# H0 — 점검 (읽기 전용)

아래를 그대로 붙여넣는다.

---

flow-bridge 폴더를 점검해줘. **파일 수정, 생성, 삭제는 하지 마.** 읽기와 아래 명령 실행만 허용.

1. `$FB_ROOT/README.md`와 `$FB_ROOT/HANDOFF.md`를 읽고 구조를 파악해.
2. `grep -rn "TODO(INHOUSE)" $FB_ROOT/` 결과를 HANDOFF.md의 "TODO(INHOUSE) 분류" 표 기준으로 분류해서 표로 만들어.
3. `python3 $FB_ROOT/tests/test_tools.py`를 실행해. 실패하면 원인(파이썬 버전, PyYAML 없음 등)만 적고 고치지 마.
4. 스킬/에이전트를 모아둔 우리 공간(AGENT_HOME)의 기존 `.opencode` 구조(agent `.md` frontmatter 형식, skill frontmatter 형식, sub-agent 호출 방식)와 받은 flow-bridge의 `.opencode/` 파일(스킬 2개, 에이전트 3개)을 비교해서 **다른 점만** 표로 정리해. 이름이 겹치는 스킬/에이전트가 있는지도 확인해.
5. pnr-rundori의 입력 형식과 QoR 요약 파일 형식이 어디에 정의돼 있는지 위치만 찾아.

보고 형식 (이 형식 그대로, 5줄 + 표 2개):
```
[테스트] 통과 N / 실패 N (실패 원인 한 줄)
[TODO] 총 N개 (H1 N / H2 N / H3 N / H6 N)
[AGENT_HOME과 차이] N건 (표) / 이름 충돌 N건
[pnr-rundori] 입력 형식 위치 / QoR 형식 위치
[막힌 것] 없음 또는 한 줄
```
