# 부검 — v0 vs boatlee, seed 1000 `[LOCAL]`

재현: `python tools/postmortem.py --a main.py --b opponents/public/boatlee.py --seed 1000`
도구 sha256 `7612e9ab5b20d309b6f904c6b03c5c374f81d62e40f083ac4f3659372ddef024`

```
최종 은행잔고  A(우리)=19,040   B(boatlee)=115,678   마진 -96,638
분기일  day 7 (gap +1,996) — 이후 gap 이 그 값의 20% 이내로 다시 돌아오지 못함
격차 역전 day 10 · 최악의 날 day 20(Δ-17,361), 21, 24, 22, 10
```

## 핵심 — 액션 **양**이 아니라 **구성**의 차이다

| 액션 | 우리(v0) | boatlee |
|---|---|---|
| WATER | **1,003** | **1,010** |
| CARE | **0** | 967 |
| COLLECT_FERTILIZER | **0** | 296 |
| FEED | **0** | 290 |
| PICKUP | **0** | 135 |
| BUY_PRODUCT | **0** | 99 |
| FERTILIZE | **0** | 72 |
| BUILD_PASTURE | **0** | 13 |
| BUY_ANIMAL | **0** | 6 |
| PASS | 451 | 324 |

**물 주는 횟수는 사실상 동일하다(1,003 vs 1,010).**
같은 물주기 트레드밀 위에서 우리는 그것만 하고, boatlee 는 그 위에 동물·비료 레이어를 얹는다.
6.1배 격차는 작물 효율 차이가 아니라 **레이어 하나가 통째로 없는 것**이다.
→ `BRIEF_exp002_animals.md` (KAGRI-013) 의 직접 근거.

## 부수 발견 2가지

1. **boatlee 는 딸기를 판다.** day 20 에 `SELL STRAWBERRY 16`, `SELL STRAWBERRY 20`.
   우리 계획 문서에 남아 있는 "딸기는 함정" 서술은 근거가 없다.
   `evidence/HYPOTHESES.md` 에 H16(딸기 라인)으로 등재하고 EXP-003 후보로 둔다.
   **EXP-002 에는 섞지 않는다 — 한 번에 한 축.**
2. **우리 농부는 720턴 중 451턴(63%)을 PASS 한다.** boatlee 는 324턴.
   일꾼 액션을 빼고 농부 단독으로만 봐도 유휴가 크다.

## 관측 필드 (팀 공용, 추측 금지)

- 은행: `env.steps[i][p].observation['farms'][k]['money']` — `farms` 는 절대 player id 0/1 로 색인.
  양쪽 관측 구조에 동일하게 채워지며 시점 회전이 없다. 종료 시 `reward` 와 정확히 일치.
- 액션: `env.steps[i][p].action == {'farmer':[OP,*args], 'hands':[[OP,*args],...], 'market':[[OP,*args],...]}`
- `observation['day']*24 + observation['hour'] == observation['step']` (정확히 성립)
- ⚠️ player 1 의 `observation['step']` 이 `None` 인 스텝이 있다. **인덱싱에 쓰지 마라.**
- ⚠️ `reward` 는 마지막 스텝을 빼면 항상 0 이다. 실시간 뱅크 신호가 아니다.
