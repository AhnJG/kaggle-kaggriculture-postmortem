# EXP-046 진단 — 공개 55be 가 상위 팀의 판매를 예측하는가 (Claude 09-29 00:05 KST)
방법: select 19팀 × 10판 = 190판 hosted 원본. 상위 팀 좌석의 기록된 관측(비공개 shed 포함)을 매 step 55be5d5f exact 에 넣고, 나온 SELL 주문을 그 팀의 실제 다음 action 과 비교(diag46.py). 비공개 상태를 쓰므로 **상한값**이다. 수치는 요청 수량 기준.
WOOL+MILK+STRAWBERRY, 팀별 (단위 recall / precision / step 사건 recall):
- 거의 exact: saberzky 1.00/1.00/1.00, Joseph Ayanda .99/1.00/.99, JM .97/1.00/.99, thisray .94/.99/.98, 인공저능 .97/.92/.97, base_camp .96/.95/.95, MISIS .95/.86/.97
- 부분: Dlyra .89/.68/.96, Jun_value .86/.85/.94, Shawn404 .89/.47/.90, ctree .94/.55/.98, ultimatum .91/.39/.95, Agent 0 .85/.51/.86, Hikaru .77/.54/.82, Fritz .76/.20/.84, Agricola .78/.23/.85, Constantin .73/.54/.94
- 다름: juliencst .51/.61/.46, QQ农场 .03/.41/.69(판매량 매우 큼)
- 전체 step 사건 recall 0.90.
해석: 상위 팀 다수는 판매 결정이 공개 55be 와 사실상 같다. d157 이 thisray(판매 예측 .98)에게 0.24 인 것은 거의 mirror 경기에서 진다는 뜻이다.
한계: 실제 경기에서는 상대 shed 가 비공개라 추정값(_OR2 추적)을 써야 한다. 이 정확도는 상한이다. 요청 수량이지 체결량이 아니다.
보조 확인: hosted configuration.seed 는 None 이고 엔진이 seed 를 지운다(utils.resolve_episode_seed). seed 로 미래 shop 을 예측하는 경로는 불가능하다.
