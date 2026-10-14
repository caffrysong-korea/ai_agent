# Mode B — 항목 추출

목표: REF map의 항목 후보를 **catalog item(draft)** 과 **knob registry entry(draft)** 로 변환한다.
원칙: REF map에 인용으로 확인되는 것만 채운다. 나머지는 `ASK`. 모드 C의 질문지가 ASK를 채운다.

---

## B1. 선행 확인

- REF map이 있는가 (모드 A 산출물). 없으면 멈추고 모드 A를 제안.
- 기존 카탈로그를 읽는다. 이미 같은 REF 위치를 가리키는 항목이 있으면 새로 만들지 않는다 (중복 생성 금지).

## B2. 항목 단위

- **REF map의 후보 하나 = catalog item 하나.** infra가 켜고 끄는 단위를 쪼개거나 합치지 않는다.
- item_id: 기존 최대 번호 + 1. **삭제된 번호도 재사용 금지** (ledger가 item_id로 결과를 묶기 때문).

## B3. 필드별 채우는 규칙

| 필드 | 채우는 근거 | 근거 없을 때 |
|---|---|---|
| title | 후보 이름 | — |
| category (dtco / dm) | REF 디렉토리 구조, infra 자료에 명시된 경우만 | **필드 생략** + 질문지에 추가 (enum 필드라 ASK 불가) |
| intent | infra 자료에 명시된 경우만. REF 주석은 "확인 필요"로 질문지에 올림 | `ASK` |
| abstract_stage | REF map 4절 stage | 매핑 불가면 항목 생성 보류, unresolved |
| order_dep | REF flow 내 실행 순서 (citation 근거) | 생략 |
| actions | B4 참고 | — |
| preconditions | stage 순서로 자명한 것만 (`check: stage_order`) | `ASK` |
| expected_effect | infra 자료 명시분만 | `ASK` |
| amenability_hints | infra 자료 명시분만 | `ASK` |
| conflicts_with | REF map 5절 | 빈 목록 |
| evidence_refs | infra 자료에 실험 결과 위치가 있으면 | `ASK` |
| ref_flow_location | REF map 4절 설정 줄 citation | — (필수) |
| ref_toggle | REF map 3절 | — |
| owner | 사용자에게 받은 infra 담당자 | `TODO`로 두고 질문지 맨 앞에 |
| review_log | `{date, by: dtco-catalog-builder, change: "REF map <버전>에서 초안 추출"}` | — |

**REF 주석 처리**: 주석에 "타이밍 개선용" 같은 문구가 있어도 intent에 바로 넣지 않는다.
질문지에 "REF 주석에 '...'라고 되어 있는데 이 항목의 의도가 맞나요?" 형태의 확인 질문으로 올린다.

## B4. actions 결정

설정 줄마다 아래 순서로 판단한다.

```
설정 줄
 ├─ 단일 mode/attribute 설정인가? (예: setXxxMode -opt val / set_db attr val)
 │    ├─ knob registry에 같은 의미의 knob_id가 있음 → kind: knob_set (기존 knob 재사용)
 │    │     └─ 이 tool variant binding이 absent면 REF 줄로 binding 추가 (verified: false)
 │    └─ 없음 → registry에 새 knob 추가(status: draft) → kind: knob_set
 └─ 그 외 (cell 목록, NDR/rule 정의, proc 호출, 여러 줄 블록)
      → kind: snippet
        - code: REF 원문 그대로 복사 (수정/정리 금지)
        - requires: REF map 4절 requires 그대로
        - readback: 적용 여부를 툴에 물을 방법이 명확할 때만 초안. 아니면 생략
        - verified: false
```

### knob registry 새 항목 규칙
- knob_id: `<category>.<의미>` 소문자 snake_case. tool 문법이 아니라 의미로 짓는다.
  예) `-usefulSkew` → `opt.useful_skew` (O) / `opt.usefulskew_mode` (X, 문법 흔적)
- `set`: REF 줄에서 값 부분만 `__VALUE__`로 치환.
- `readback`: 같은 tool variant의 getter. **초안이므로 verified: false**. 확신이 없으면 비워두고 notes에 "readback 미정".
- 다른 tool variant: `absent`. (같은 Innovus라도 REF가 legacy면 stylus는 absent)
- persistence: REF map 4절 sticky 판정 그대로.

## B5. 검증

- tools/validate로 카탈로그 파일과 registry 파일을 검증한다.
  <!-- TODO(INHOUSE): validate 커맨드 (P4) -->
- 실패하면 고친 뒤 재검증. 통과 전에는 "완료" 보고 금지.

## B6. 보고

SKILL.md 6절 형식. [결과]에 추가로:
- 생성 항목 수 (knob_set / snippet 비율)
- 새 knob registry 항목 수
- requires가 있는 항목 수 (고객 flow 이식 위험 신호)
- 남은 ASK 수와 가장 많은 필드
