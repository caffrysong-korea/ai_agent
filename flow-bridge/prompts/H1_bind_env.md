# H1 — 환경 값 채우기

H0 리포트를 받은 뒤 붙여넣는다. **2단계로 나눠서 진행한다 (계획 → 승인 → 수정).**

---

H0에서 찾은 TODO(INHOUSE) 중 **H1 대상만** 처리하자. 먼저 계획만 보여주고, 내가 승인하면 수정해.

대상:
1. `$FB_ROOT/config/env.yaml`의 TODO(INHOUSE) — 모델 바인딩(DELTA와 같은 방식), 경로(workspace, item_cards), run_data(run 루트, cmd 로그 파일명, QoR 요약 파일명), python 경로
2. AGENT_HOME에 추가한 flow-bridge 에이전트 3개와 스킬 2개의 frontmatter, permission 문법을 기존 에이전트 형식에 맞추기
3. 두 SKILL.md의 "위치"에 있는 `FB_ROOT`를 flow-bridge 폴더의 실제 절대경로로 바꾸기 (HANDOFF.md "설치" 참고)

규칙:
- 위 대상 외 파일은 건드리지 마. AGENT_HOME의 기존 스킬/에이전트 파일 수정 금지.
- 값을 모르면 추측하지 말고 계획에 "확인 필요"로 적어.
- 수정 후 `python3 $FB_ROOT/tests/test_tools.py` 통과 확인.

1차 보고 (계획):
```
[수정할 파일] N개 (파일 · 바꿀 내용 한 줄씩)
[확인 필요] 내가 답해야 할 것 목록
[FB_ROOT] 바꿀 경로 한 줄
```

2차 보고 (수정 후):
```
[수정] N개 파일   [남은 H1 TODO] N개
[테스트] 통과/실패
```
