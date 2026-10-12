# releases — 우리가 만들고 검증·제출한 봇

각 폴더는 Kaggle 에 올린 바이트(또는 올리기 전 검증한 바이트) 그대로다. `main.py` 하나가 봇 전체이며,
`SHA256SUMS` 로 제출 원장([`evidence/HOSTED_LEDGER.md`](../evidence/HOSTED_LEDGER.md),
[`experiments/EXPERIMENT_LOG.md`](../experiments/EXPERIMENT_LOG.md) §3)의 artifact SHA 와 대조할 수 있다.
제출용 `submission.tar.gz` 는 용량 때문에 빼고 `main.py` 만 두었다.

## 최종 제출 (마감 시점 활성 두 슬롯)

| 슬롯 | 폴더 | submission ID | 설명 |
|---|---|---|---|
| A | [`exp062-L4p/`](exp062-L4p/) | 56709992 (L4pc, 사본) | d157 + glut lead K=4 — 과잉 구간에서 tape 가 계획한 판매를 4 step 앞당김 |
| B | [`exp035-d157/`](exp035-d157/) | 56709342 (d157c, 사본) | 공개 55be5d5f + `_S1002_PASSES` 34→35 |

## 전체 목록

| 폴더 | 실험 | 부모 계보 → 바꾼 것 | hosted (관측) |
|---|---|---|---|
| `v0/` | S4–S8 | 직접 짠 규칙기반 최소 봇 | 314.8 |
| `v1-20260910/` | EXP-001 | v0 + 땅·일꾼·당근 조정 | 343.9 |
| `f0-mirror-lead-exp014/` | EXP-014R | 공개 lynnsakurai v2 + `_ADV_LOOK` 3→4 | 미기록 |
| `f0-mirror-slot-exp015/` | EXP-015 | 공개 lynnsakurai v2 + SELL 가격 내림차순 | 미제출 (INVALID) |
| `f0-c1-adv-exp016/` | EXP-016 | 공개 pipe16 + V53 sale-advance 이식 | **2425.7 (대회 최고)** |
| `f0-omw-adv-exp017/` | EXP-017 | OneMoreWheat + sale-advance | 2100.2 |
| `mirror-screen-v171/` | EXP-023 | 127ed3e6 계열 + `_DP_H` 8→9 | 2337.5 |
| `round2-v074/` | EXP-024 | v171 + `V9_RACE_DEFAULT` 44→45 | 2215.9 |
| `exp035-d157/` | EXP-035 | 공개 55be5d5f + `_S1002_PASSES` 34→35 | 2400.9 (최고 약 150위) |
| `exp039-c26/` | EXP-039 | d157 + `_CA_MARGIN` −15→−26 | 1939.7 |
| `slot2r-Rc26_107/` | slot2-R | mirror 판이면 route 107, 아니면 c26 | 1658.1 |
| `exp062-L3p/` … `exp062-L6p/` | EXP-062 | d157 + glut lead K=3…6 | L4p 1800.5 · L5p 1713.7 (L3p·L6p 미제출) |

## 구조

공개 계보 파일을 **바이트 그대로 두고 끝에 wrapper 를 덧붙이는** 방식이다. 엔진은 파일의 마지막 callable 을 진입점으로 쓴다
(공개 TOP1 노트북이 마지막 callable 이 패치 함수라서 제출된 그대로면 아무 행동도 하지 않던 사례가 있다, 실험 로그 §6 "ANL · 09-27 기타").
예: `exp035-d157/main.py` 끝의 `exp029_entry`, `exp062-L4p/main.py` 끝의 `exp062_entry`.

## 실행

```bash
pip install kaggle-environments==1.32.7
python3 - <<'EOF'
from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 7})
env.run(["releases/exp062-L4p/main.py", "starter"])
print([round(s.reward) for s in env.steps[-1]])   # 최종 은행 잔고 [L4p, starter]
EOF
```

## 라이선스

`v0`·`v1` 을 뺀 모든 봇은 Apache-2.0 공개 Kaggle 노트북의 파생물이다. 원 저자 표기는 각 `main.py` 안에 그대로 있고,
라이선스 전문은 `main.py` 안 또는 같은 폴더의 `LICENSE.txt` 에 있다. `NOTICE.txt` 의 계보 설명 중 일부
(`exp062-L*`, `slot2r-Rc26_107`)는 d157 문구를 그대로 반복한다(실험 로그 §10-13).
