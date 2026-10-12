[역할] 너는 2인 시뮬레이션 게임 봇의 전략 연구자다. 판단과 가설만 내라. 코드는 쓰지 마라. 모르면 UNSURE라고 써라.

[게임: Kaggle Kaggriculture, 2인, 720 step(30일×24턴), 보상 = 최종 money(시작 3000). 순위는 두 봇의 보상 비교(승/무/패).]
시장 메커닉(엔진 원문 요약):
- 품목마다 공유 inventory I(시작 I0=10000). 가격 = I<I0 이면 base + amp·f_below(I0−I), I≥I0 이면 base − amp·f_above(I−I0), amp = target·base/f(T), 가격 하한 1.
- SELL 1단위 → I+1(가격 하락). BUY_PRODUCT(WHEAT/FERTILIZER만) → I−1. 한 step 안에서 두 좌석 주문을 슬롯 순서대로 1단위씩 lockstep 처리하고, 두 좌석 모두 같은 체결 전 I로 견적한다. 주문은 턴당 최대 10개.
- 도시 소비: 4 step마다 해금된 shop 인스턴스가 품목별 I를 1 줄인다(단일 품목 shop은 2). 24 step마다 town center가 FERTILIZER를 뺀 모든 품목을 1 줄인다. shop은 3일마다 1개가 해금되고(복원 추출, 최대 8개) seed로 결정된다.
  SHOPS: BAKERY[EGG,WHEAT], PIZZA[MILK,TOMATO,WHEAT], BRUNCH[EGG,WHEAT,STRAWBERRY], YARN_STORE[WOOL], ICE_CREAM[STRAWBERRY,MILK,WHEAT], PET_CAFE[CARROT], SMOOTHIE[STRAWBERRY,MILK], FARMERS_MARKET[WHEAT,CARROT,TOMATO,STRAWBERRY]
- 파라미터(base, T, above_func, above_target): WOOL(200,105,sq,3.2), MILK(160,122,linear,1.6), STRAWBERRY(120,100,linear,1.6), TOMATO(60,200,sqrt,0.6), MELON(250,300,sq,3.6), EGG(50,332,log,0.2), CARROT(35,450,sqrt,0.7), WHEAT(25,400,log,0.2), FERTILIZER(100,200,linear,0.4).
- shed(창고) 용량 100. 게임 끝에 남은 재고는 0원.

[우리 상황] 우리 봇 d157(공개 커널 계열에서 파생)은 LB ~2345이다. 상위 2400+ 팀을 상대로 승률은 0.40이다. 평가는 tape(상위 팀의 실제 행동을 재생하고, 상대 좌석에 우리 봇을 넣는 open-loop)로 했고, 과거 실전 결과를 100% 재현한다. 상위 팀은 생산 구성과 최종 money가 우리와 거의 같다(~98–100k). 판은 근소하게 갈린다: 패배 margin 중앙값 −987, 승리 +1449, margin sd 9.0k.
이미 실패한 시도: 상수 ±1 탐색, 공개 봇 30개 교체(oracle), WHEAT 대량 매수·매도 순환 흉내, WHEAT 주문 순서 교환, 관측 기반 front-run(이미 구현돼 있음).

[새 증거 EXP-044: 상위 19팀 tape 594판, 우리−상대 순현금을 품목별로 분해, reward=Σ현금흐름으로 정확히 일치]
- 품목별 순현금 차이와 margin의 상관: WHEAT r=+0.01(무관). MILK +0.49, WOOL +0.48, STRAWBERRY +0.40, TOMATO +0.33, FERT +0.15, CARROT +0.12, EGG +0.11, MELON −0.05.
- 판매 수량은 패배판과 승리판에서 거의 같다. 다른 것은 단가다(형식: 우리 수량@단가 / 상대 수량@단가).
  WOOL Q3(마지막 1/4): 패배 60.2@78.7 / 56.1@79.6, 승리 62.5@114.0 / 54.7@93.2. WOOL Q2: 패배 60.5@117.3 / 58.7@119.9, 승리 61.5@133.3 / 56.2@116.1.
  MILK Q3: 패배 71.0@88.8 / 71.4@88.9, 승리 73.4@92.0 / 72.8@78.5. MILK Q2: 패배 76.0@82.0 / 72.0@84.0, 승리 77.1@88.9 / 76.1@81.2.
  STRAWBERRY Q2: 패배 141.5@148.2 / 139.0@154.2, 승리 141.6@149.0 / 137.3@150.9.
  TOMATO(우리는 거의 안 키움) Q3: 패배 우리 10.6@242 / 상대 25.2@163, 승리 11.5@194 / 19.3@116.
- 패배−승리 평균 차이(우리−상대 순현금): WOOL −3.8k, MILK −1.8k, TOMATO −1.8k, STRAWBERRY −1.7k, CARROT −0.8k, WHEAT −0.3k.
- 팀별 우리 승률: 최약 juliencst 0.20, thisray 0.24 … 최강 Dlyra 0.60.

[질문]
1) 이 증거가 가리키는 승패 메커니즘을 3줄 이내로 설명하라(예: 두 판매자가 같은 수요를 나눠 가질 때 판매 시점과 순서).
2) d157에 넣을 단일 요인 변경 가설을 5개 이하로 내고 순위를 매겨라. 각 가설에 다음을 붙여라.
   (a) 변경 내용(규칙 수준), (b) 기대 기전, (c) tape 평가의 함정(open-loop라서 과대평가될 위험), (d) 결과 전에 고정할 판정 지표 1개.
3) 우리가 놓치고 있을 가능성이 큰 것 3개. 예: seed로 미래 shop 해금을 예측하는 것, 재고를 쌓았다가 파는 것, 상대 재고나 판매 패턴을 관측하는 것 등.
전체 답은 600단어 이내로 써라.
