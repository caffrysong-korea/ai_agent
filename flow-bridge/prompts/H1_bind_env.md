# H1 — 환경 값 채우기

H0 리포트를 받은 뒤 붙여넣는다. **2단계로 나눠서 진행한다 (계획 → 승인 → 수정).**

---

H0에서 찾은 TODO(INHOUSE) 중 **H1 대상만** 처리하자. 먼저 계획만 보여주고, 내가 승인하면 수정해.

대상:
1. `flow-bridge/config/env.yaml`의 TODO(INHOUSE) — 모델 바인딩(DELTA와 같은 방식), 경로(workspace, item_cards), run_data(run 루트, cmd 로그 파일명, QoR 요약 파일명), python 경로
2. `.opencode/agents/*.md`와 두 `SKILL.md`의 frontmatter, permission 문법을 우리 DELTA 형식에 맞추기
3. flow-bridge 설치 위치 결정: `.opencode/` 아래 skill/agent를 어디에 둘지, 그때 SKILL.md 상단의 "경로 기준" 안내(`schema/…`는 flow-bridge 루트 기준)가 맞는지

규칙:
- 위 대상 외 파일은 건드리지 마. DELTA 기존 파일 수정 금지.
- 값을 모르면 추측하지 말고 계획에 "확인 필요"로 적어.
- 수정 후 `python3 flow-bridge/tests/test_tools.py` 통과 확인.

1차 보고 (계획):
```
[수정할 파일] N개 (파일 · 바꿀 내용 한 줄씩)
[확인 필요] 내가 답해야 할 것 목록
[설치 위치안] 한 줄
```

2차 보고 (수정 후):
```
[수정] N개 파일   [남은 H1 TODO] N개
[테스트] 통과/실패
```
