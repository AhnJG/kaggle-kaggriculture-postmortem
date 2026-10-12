# EXP-044 margin 분해 (Claude 09-28 22:20 KST)
자료: d157 × 2400+ select 19팀 tape 594판(holdout 제외). games42 와 rewards 121/121 표본 일치, Σ현금흐름+3000 = reward 정확.
스크립트: run44.py(분기별), run44s.py(step별 6품목 SELL), decomp44.py. 결과: d157.jsonl, d157_steps.jsonl.
1. WHEAT 순현금 차이는 margin 과 무관(r=+0.01). 상위 팀의 대량 WHEAT 거래는 승패 요인이 아니다.
2. margin 분산은 WOOL(r=.48, sd 6.9k), MILK(.49, 4.3k), STRAWBERRY(.40), TOMATO(.33)에 있다. 판매 수량은 승·패 모두 같고 단가만 다르다.
3. 판매 단위의 ~68%는 같은 step(두 봇 일정이 같음)에서 팔리고, 같은 step 단가 차이는 ~0 → slot 순서는 무관.
4. 차이는 한쪽만 파는 step 에서 난다. WOOL solo Q2/Q3 우리 단가: 패배 104/69.5, 승리 148/125. 상대는 110/76 → 100/89.5.
   상대 판매가 ±12 step 에 없는 우리 "isolated" WOOL 판매: 패배 7.4개@42, 승리 9.1개@154. MILK 5.8@45.5 → 4.5@89.
5. 주의: 결과(승패)로 나눈 분해라 인과가 아니다. 판매 단가가 좋은 판이 이긴 판으로 분류되는 것은 부분적으로 기계적이다. 시장 수준(seed·YARN_STORE 수)도 패배판이 낮다. 인과 검증은 개입 실험(EXP-045)으로만 한다.
6. [정정 09-28 23:00] d157 은 이미 상대를 관측한다. tape 6판 REPORT 합계: _OR2 rival_harvest 8473·rival_sold 9004(상대 수거·판매 추적), _V9_RACE rival_sales 868·leads 219, _S758 fires 89, _V92_P pred_fires 20, _S793 moved_sells 1247. 'R_opp 추정' 자체는 새 기능이 아니다. 차이는 그 정보를 판매 결정에 어떻게 쓰는지다(reports45.py).
GPT-5.6 Sol(chat, High) 자문 2회: gpt_prompt1.md, gpt_answer1-2.md.
