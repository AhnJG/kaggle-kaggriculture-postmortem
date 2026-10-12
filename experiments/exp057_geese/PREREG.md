# EXP-057 사전등록 (Claude 09-29 KST 오후, 결과 전) — 거위(EGG) 비중 확대

## 근거 (결과 전 증거)
- SURVEY300 (analysis/survey300_20260929, 1,865 게임 추출 시점): top100 거위 수 egg shop 0/1/2+ 에서 4.5/5.3/5.9, 우리(Sian, d157/c26 hosted 347판) 1.5/2.4/2.3. EGG 판매 top100 155–207 개 vs Sian 46–77.
- 엔진: EGG 가격 곡선은 I0 위에서 log(target 0.2, T 332) → 공급이 늘어도 가격이 거의 안 떨어진다(실측 판매가 52–61). MILK(linear)·WOOL(sq)·STRAWBERRY(linear) 는 공급에 민감.
- 거위 1마리/일 ≈ 알 2(돌봄 시)×~55 + 비료 1 − 밀 1(~40). 값 300, COOP 건설 무료.
- d157 에는 거위를 다른 가축으로 바꾸는 층이 3개 있다: V9 HERD(yarn/milk shop 조건), HERD2(_HD2_OPTIONS 로 COW/SHEEP 전환), v44y(_Y_CFG yarngeese). 반대로 COWSWAP(_CS) 은 소→거위 전환을 'nomilk' 규칙과 비율 1.3·최소 이득 600 으로 제한한다. 이 문턱은 과거 48 seed 자체 연구(research/claude_20260913)로 정했다.

## 변형 (부모 = d157 releases/exp035-d157/main.py sha 94a46c11…, 부모 바이트 불변, 끝에 상수 덮어쓰기 + entry)
- G1 keep-geese: V9_HERD_MAX_EGG_SHOPS=-1, V9_HERD_MAX_EGG_SHOPS_COW=-1, _HD2_OPTIONS=(), _Y_CFG['yarngeese']=False (거위→다른 가축 전환 끔).
- G2 cow-to-goose: _CS_SHOP_RULE=None, _CS_RATIO=1.0, _CS_MIN_GAIN=0.0 (첫 소 구매를 거위 EV ≥ 소 EV 이면 거위로).
- G3 = G1 + G2.

## 평가
Stage 1 (현재 상대 집단 tape 269, experiments/exp051_curpop, 기준선 EXP-051 d157·c26 행):
  변형 − d157 paired 점추정 > +0.02 이고 상대 단위 bootstrap 95% 하한 > 0, 그리고 변형 − c26 점추정 ≥ 0. 3개 변형 다중성은 Holm 보정 없이 하한 기준만 쓰되, 통과가 여럿이면 Stage 2 는 점추정 최대 1개만.
  진단(판정 아님): 행동이 바뀐 판만의 Δ, 최종 거위 수, EGG 판매량.
Stage 2 (통과 1개): exp048 H219 와 exp049 F228 에서 d157 대비 Δ ≥ 0, 2400+ tape(top2400) 에서 d157 대비 Δ ≥ −0.01, family arena d157 대비 ≥ −0.02, closed-loop d157 직접 50판(seed 15000–15024 양 좌석) ≥ 0.5, D3 gate.
결과 후 기준·변형을 바꾸지 않는다(바꾸면 새 실험 번호). 제출은 사람만.
