# Mode C — 인터뷰 루프

목표: draft 항목의 `ASK`를 infra 담당자 답변으로 채우고, 조건을 만족한 항목을 reviewed / approved로 승격한다.
한 번에 끝나지 않는다. **질문지 생성 → 답변 반영 → 검증 → 승격**을 라운드 단위로 반복한다.

```
 ┌──────────────┐   질문지    ┌──────────┐   답변(텍스트)   ┌──────────────┐
 │ C1 질문 생성 │ ──────────▶ │ infra 담당 │ ───────────────▶ │ C2 답변 반영 │
 └──────────────┘             └──────────┘                  └──────┬───────┘
        ▲                                                         │
        │            남은 ASK / 후속 질문                          ▼
        └──────────────────────────────────── C4 승격 판정 ◀── C3 검증
```

사용자(bridge 운영자)가 질문지를 infra 담당자에게 전달하고 답변을 다시 붙여넣는 구조다. agent가 infra 담당자에게 직접 연락하지 않는다.

---

## C1. 질문지 생성

### 대상
1. ASK가 남은 필드
2. enum이라 생략된 필드 (category 등)
3. REF 주석 기반 확인 질문 (모드 B)
4. owner 미정
5. REF map unresolved 중 infra만 답할 수 있는 것

### 우선순위 (높은 순)
| 순위 | 필드 | 이유 |
|---|---|---|
| 1 | owner | 승인권자가 없으면 approved 불가 |
| 2 | intent, abstract_stage 확인 | 반영 위치(2단계) 판단의 기준 |
| 3 | preconditions | 잘못 넣으면 고객 flow에서 깨짐 |
| 4 | requires 관련 (REF 전용 proc의 역할) | 이식 가능성 판단 |
| 5 | expected_effect | 4단계 결과 해석 기준 |
| 6 | amenability_hints | 3단계 판단 근거 (없어도 approved 가능) |
| 7 | evidence_refs, 실험 결과 | ledger seed |

### 분량
- 한 라운드 최대 10문항 (기본값).  <!-- TODO(INHOUSE): infra 담당자 부담에 맞게 조정 -->
- 같은 질문에 "모름"을 두 번 받으면 더 묻지 않는다 (review_log로 판단).

### 형식
templates/question_sheet.md 를 쓴다. 문항마다:
- 왜 묻는지(이 답이 무엇을 결정하는지) 한 줄
- 가능하면 선택지 + "모름" 선택지
- 자유 서술이 필요한 문항은 예시 답변 한 줄

## C2. 답변 반영

| 상황 | 처리 |
|---|---|
| 명확한 답 | 해당 필드 갱신 + review_log `{date, by: "<담당자> (Q-id)", change: "<필드>: <요약>"}` |
| "모름" | ASK 유지 + review_log에 "Q-id 모름" 기록 |
| 애매한 답 ("보통은 켜요") | **해석해서 채우지 않는다.** 후속 질문을 다음 라운드에 추가 |
| 답이 질문 범위보다 넓음 | 질문한 필드만 반영. 나머지 정보는 notes에 보관하고 관련 필드가 있으면 다음 라운드 확인 질문 |
| 답이 REF flow와 모순 | REF flow 인용을 첨부해 확인 질문. 임의로 한쪽을 택하지 않음 |
| 실험 결과/수치 언급 | C2-1 ledger seed 초안 작성 |

**들은 만큼만**: "fmax에 좋아요" → expected_effect.fmax = "+" 까지만. power/area는 건드리지 않는다.

### C2-1. ledger seed
- 담당자가 실측 근거(run 위치, 리포트)를 줬으면 `source: infra_ref`, 말로만 전한 결과면 `source: seed_interview`.
- `readback_status: not_run`. delta는 말한 수치만. design_fp는 아는 만큼(최소 design_id).
- 초안을 ledger-curator에 위임 (SKILL.md 4절). bridge-pilot이 ledger에 직접 쓰지 않는다.

## C3. 검증

tools/validate 통과 필수. 실패 시 수정 후 재검증.  <!-- TODO(INHOUSE): 커맨드 -->

## C4. 승격 판정

| 전이 | 조건 (전부 만족) | 누가 |
|---|---|---|
| draft → reviewed | intent / expected_effect / preconditions에 ASK 없음 · category 존재 · 모든 binding에 REF citation · validate 통과 · **사용자에게 변경 요약을 보여주고 확인받음** | 사용자 확인 |
| reviewed → approved | owner의 명시적 승인 ("DTCO-0007 승인") 을 사용자가 전달 · review_log에 승인 기록 | infra 담당자 |
| reviewed/approved → draft | 내용이 바뀌는 답변이 새로 들어옴 (version +1) | 자동 |

- 승격은 항목 단위. 일괄 승인 요청이 오면 대상 항목 목록을 보여주고 확인받은 뒤 반영.
- approved에서 amenability_hints / evidence_refs가 ASK여도 승격 가능. 대신 보고에 "근거 없는 approved: N개"로 표시.
- knob registry 항목도 같은 규칙. 그 knob을 쓰는 catalog item이 approved가 되려면 knob이 최소 reviewed여야 한다.

## C5. 보고

SKILL.md 6절 형식 + 라운드 번호, 이번 라운드 반영 문항 수 / 모름 수 / 후속 질문 수.
