# 상위권 write-up 과 비교: 무엇이 갈랐나

> 2026-10-12 에 대회 후 공개 글을 처음 읽고, 최종 순위가 확정된 뒤 2026-10-27 에 Kaggle write-up 페이지를 다시 읽어 갱신했다.
> "최종" 열은 10-27 의 write-up 제목·리더보드 기준이고, "10-12 표시" 열은 처음 읽을 때 작성자 옆에 표시된 실시간 순위다.
> 각 팀의 접근·수치는 그 팀이 보고한 내용(`[COMMUNITY]`)이며, 이 저장소에서 재현하지 않았다.
> 1위의 최종 write-up 과 2위 글은 10-27 현재 찾지 못했다. 1위는 대회 중 올린 예고 글만 읽었다.

## 읽은 글

링크는 모두 `https://www.kaggle.com/competitions/kaggriculture` 아래 경로다.

| 최종 | 10-12 표시 | 팀 | 접근 | 컴퓨트 (보고) | 글 |
|---|---|---|---|---|---|
| 1위 | 1위 | M & M & P & Q | BC ↔ self-play PPO 반복 + 자체 휴리스틱 플래너 시연 + 규칙 패치. 10M Transformer (예고 글) | A100 최대 17장 + A30 29장, self-play 약 829만 판 | [discussion/745073](https://www.kaggle.com/competitions/kaggriculture/discussion/745073) |
| 3위 | — | DSM | 상위권 리플레이 BC → self-play PPO → 추론 후처리. 10.4M Transformer. 후처리로 승률 74.2→87.8% | A100 최대 23장, 남은 로그 기준 약 17,400 A100-시간 | [writeups/kaggriculture-3rd-place-dsm-solution](https://www.kaggle.com/competitions/kaggriculture/writeups/kaggriculture-3rd-place-dsm-solution) |
| 4위 | 4위 | Farmcore (Yaroslav Pudovkin) | 순수 BC, RL·탐색 없음. 턴 전체를 한 번에 그리고 보정하는 21.5M Transformer. 실제 체결된 거래만 라벨로 사용 | 총 약 5.5 A100-시간 | [writeups/farmcore-…](https://www.kaggle.com/competitions/kaggriculture/writeups/farmcore-a-one-pass-transformer-trained-on-what-t) (처음 읽은 글: [discussion/745119](https://www.kaggle.com/competitions/kaggriculture/discussion/745119)) |
| 5위 | — | 有辣条有权 | 순수 SFT(BC), 토큰 단위 자기회귀 생성. 이긴 경기만, 최신·최강 팀 가중 | 4090 2장, 3090, DGX Spark, Colab | [writeups/its-sft-all-the-way-down](https://www.kaggle.com/competitions/kaggriculture/writeups/its-sft-all-the-way-down) |
| 6위 | — | CDE | 기준 tape 조건부 BC(1~11일) + 12일째부터 PPO. 약 2.2M | 다중 GPU (장수 미기재) | [writeups/6th-place-write-up](https://www.kaggle.com/competitions/kaggriculture/writeups/6th-place-write-up) |
| 7위 | 5위 (글 작성 시 7위) | DECEM | 순수 BC 8.2M Transformer + 규칙 2개. 최신·최강 팀 조건부 생성 | RTX 5090 1장, 사전학습 약 50분 | [writeups/7th-place-…](https://www.kaggle.com/competitions/kaggriculture/writeups/7th-place-my-solution-only-behavior-cloning-t) |
| 9위 | — | tetsuya 외 2명 | RL 로 시작해 마지막 주에 순수 BC 로 전환. 18.4M | RL 에 GPU 4장 | [writeups/from-reinforcement-learning-…](https://www.kaggle.com/competitions/kaggriculture/writeups/from-reinforcement-learning-to-a-final-bc-agent) |
| 10위 | — | KawattaTaido | BC → PPO, 21.8M | RTX 5090 1장, 약 23시간 | [writeups/10th-place-…](https://www.kaggle.com/competitions/kaggriculture/writeups/10th-place-bc-ppo-on-a-single-rtx-5090) |
| 12위 | — | Unknown Mother-Goose | BC → KL 고정 PPO, 따라 할 팀별로 두 갈래 | H200 1~2장 | [writeups/12th-place-bc-with-ppo](https://www.kaggle.com/competitions/kaggriculture/writeups/12th-place-bc-with-ppo) |
| 13위 | 11위 (글 작성 시 10위) | MarvinTMB | BC 후 PPO self-play 리그, 약 0.95M | RTX 5090 1장, 약 10시간 | [discussion/745258](https://www.kaggle.com/competitions/kaggriculture/discussion/745258) |
| 19위 | — | Christoffer Thimsen (솔로) | 1·3·7위 행동을 복제한 소형 CNN 12개 앙상블 + 규칙 3개. RL·탐색 없음 | 미기재 | [writeups/19th-place-…](https://www.kaggle.com/competitions/kaggriculture/writeups/19th-place-solo-gold-a-behaviour-clone) |
| 22위 | — | atsushi11o7 | 초반·후반 모델 분리, BC → PPO. 마지막 강자 BC 를 PPO 가 확실히 넘지 못했다고 보고 | RTX 5070 Ti 1장 | [writeups/22nd-place-…](https://www.kaggle.com/competitions/kaggriculture/writeups/22nd-place-behavior-cloning-and-ppo-with-diverse) |
| 32위 | — | mtmr_s1 | **ML 없음.** 상위권 리플레이에서 뽑은 opening book + 매일 simulated annealing·beam search 로 재계획 | GitHub Actions CPU | [writeups/32nd-place-…](https://www.kaggle.com/competitions/kaggriculture/writeups/32nd-place-solution-opening-book-and-heuristics) |
| 미확인 | 26위 (글 작성 시 24위) | t fuku | 하루 단위 거시 결정은 BC, 하루 실행은 결정론적 C++ 컴파일러 | 마지막 약 5일, Claude 와 함께 개발 | [discussion/745783](https://www.kaggle.com/competitions/kaggriculture/discussion/745783) |
| 미확인 | 196위 | k256.dev | 상점 순서에만 반응하는 상위 106위 봇을 골라 행동을 통째로 복제 | 이틀 | [discussion/748305](https://www.kaggle.com/competitions/kaggriculture/discussion/748305) |
| 미확인 | 438위 (글은 439위) | Chris Deotte | ① 공개 tape 봇 + 판매 레이어(1960) ② 상위권 첫 수를 따라 한 동물 중심 봇(2125). 사람 1명 + AI 에이전트 5개 | — | [discussion/747538](https://www.kaggle.com/competitions/kaggriculture/discussion/747538) |
| 미확인 | 267위 | Krzysztof Gonia | 경제 계획은 단순 규칙, 실행은 LNS 최적화 | — | [discussion/745087](https://www.kaggle.com/competitions/kaggriculture/discussion/745087) |

"미확인"은 10-27 에 최종 순위를 다시 확인하지 않은 글이다.

## 비교

| 축 | 상위권 (최종 10위 안 8팀) | 우리 (최종 1,498위, 기록 최고 354위) |
|---|---|---|
| 정책 | 상위권 리플레이로 학습한 신경망이 매 턴 상태를 보고 행동을 생성 | 공개 계보의 기록된 행동 tape 를 재생하고, 그 위에 규칙 레이어를 덧붙임 |
| 상대에 대한 반응 | 상태를 입력으로 받으므로 상대와 시장 변화에 반응 | tape 는 open-loop 라 반응하지 않음. 반응은 덧붙인 레이어만 |
| 따라 한 대상 | 상위 팀의 **행동 분포**(어떤 상태에서 무엇을 하는가) | 공개 노트북의 **행동 순서**(그대로 재생) |
| 데이터 관리 | 최신 버전 가중, 최강 팀 하나로 미세조정, 실제 체결된 행동만 라벨로 사용(4·9위) | 공개 계보를 갈아타며 따라감 |
| 경제 | 첫 턴부터 동물 중심 경제(Chris Deotte 관찰: 상위권 대부분이 첫 턴에 소를 산다) | 우리 봇도 동물을 키웠지만(예: 에피소드 115289957 15일째 소 6·양 6·거위 5) 규모와 작물 구성은 tape 가 정한 대로 고정. 거위·토마토 등 생산 변경은 tape 위에서 실험해 모두 실패 |
| 평가 | 같은 seed 짝 대결의 돈·승패로 체크포인트 선택. 검증 손실·정확도는 실전과 맞지 않았다고 보고(3·4·12·19위) | 같은 seed 짝 대결 + 실전 경기 tape 재생. 같은 계열 미세 변경은 실전과 맞지 않았음 |
| 컴퓨트 | 1·3위는 A100 수십 장. 4위는 A100 약 5.5시간, 7·10·13위는 RTX 5090 1장 | 맥북에어 + Kaggle/Colab 노트북 |

## 무엇을 배웠나

1. **천장은 방식에서 정해졌다.** Chris Deotte 의 tape 봇은 대회 후 다른 tape 봇과 정확히 5할을 나눴고, 2100점 위 상대는 tape 가 아니라 동물을 키우는 경제형 봇이었다고 한다.
   우리 실전 기록도 같은 모양이다. 마감 무렵 L4p·d157r 은 1600–1800점 상대에게 0.73·0.70, 1800–2000점 상대에게 0.50·0.45, 2000–2200점 상대에게 0.29·0.33이었다([실험 로그 §4 Phase 7](../experiments/EXPERIMENT_LOG.md)).
   마지막 사흘의 진단(55be 변형 상대 패배)과 개선은 모두 tape 계열 안의 싸움이었다.
   다만 우리 봇도 동물을 키웠으므로 차이를 "동물 유무"로 줄일 수는 없다. 상위권의 공통점은 상태를 보고 계획을 다시 세우는 정책이었다.
   대부분은 학습된 정책이었고, 32위는 학습 없이 상위권 opening book 과 매일 탐색으로 같은 일을 했다(마감 일주일 전 공개 LB 3위까지 올랐다고 보고).
2. **우리는 맞는 방향을 처음에 적어 두고 버렸다.** 09-03 [흡수 전략 문서](../plan/kaggriculture_strategy_transfer.md)는 "AlphaGo 처럼 기존 전략을 흡수할 수 있지 않나"라는 질문에서 출발했다.
   이 문서는 리플레이 행동 복제(L2)를 "확실한 상위권"으로 평가하고 2~3주차 2번 슬롯 후보로 잡았다. 그러나 09-06 범위 결정("규칙기반 + 좁은 ML까지만")과 09-10 tape router 전환 뒤 다시 다루지 않았다.
   최종 10위 안에서 읽은 8팀(1위는 예고 글)은 모두 BC 를 기반으로 했다. 7위는 마지막 9일 동안, 9위는 마지막 주에 RL 에서 BC 로 바꿔, 13위는 GPU 1장으로 10시간 학습해 그 자리에 올랐다.
3. **"RL 은 안 된다"는 KILL 은 반만 맞았다.** 순수 self-play PPO 를 막은 K6 의 근거(80k 벽)는 처음부터 RL 만 하는 경우의 이야기였고, 3위와 12위도 처음부터 PPO 는 무너졌다고 보고했다.
   효과가 있었던 것은 BC 로 출발한 뒤의 PPO(1·3·6·10·12위)였다. 반면 4·5·7·9·19위는 RL 없이 BC 만으로 충분했고, 4·7·19·22위는 PPO 이득이 작거나 불안정했다고 썼다.
   우리는 RL 문제를 BC 와 분리해 보지 않았다.
4. **엔진의 무음 처리를 우리는 gate 에만 썼고, 상위권은 학습에 썼다.** 우리 계약은 초과 주문 절삭, 셰드 초과 소멸 같은 무음 실패를 표로 정리했다([`AGENTS.md`](../AGENTS.md) §3).
   4위와 9위는 같은 현상을 학습 데이터 정제에 썼다. 4위는 실제로 체결된 행동만 라벨로 쓰자 이전 최강 네트워크 상대 24판 중 3승이 12승이 됐다고 처음 글에 썼고, 최종 write-up 에서는 급식 가드까지 더해 23승이 됐다고 보고했다.
5. **평가의 교훈은 같았고, 상위권은 한 걸음 더 갔다.** 상위권도 검증 손실 대신 같은 seed 짝 대결로 골랐고, 4위는 검증 정확도와 돈의 상관이 −0.86 이었다고 썼다.
   상대를 어떻게 두느냐도 다뤘다. 12위는 상대를 기록 재생(open-loop)으로 두는 평가는 난수 위치가 어긋나 무효라고 보고했고, 3위는 BC 복제 상대가 실제 팀보다 약 0.4 쉬웠다고 썼다.
   7위는 실전 경기를 8일째까지 그대로 재생한 뒤 후보가 이어받는 방식을 쓰기 전에, 자기 경기 99판을 정확히 재현하는지부터 확인했다.
   우리 문제는 짝 대결 자체가 아니라 상대 풀과 평가기 검증이었다. 로컬 상대는 공개 노트북 계열과 그 변형이 중심이었고, 09-25 calibration 도 "풀이 실전을 대표하지 못한다"고 진단했다.
   실전에서 우리를 이긴 경제형 봇을 풀에 넣지 못했다.

## 다음 대회에 가져갈 것

- 첫 주에 상위권 리플레이를 받아 **행동 복제 기준선**을 만든다(7위 사례: RTX 5090 1장, 사전학습 약 50분). 공개 노트북 exact 는 그와 별개의 빠른 기준선으로 쓴다.
- 매일 최신 상위권 경기를 다시 받아 학습 데이터를 갱신한다(5·7·10·12·19위가 공통으로 한 일).
- 로컬 상대 풀에 **실전 상위권과 같은 유형의 상대**를 넣는다. 공개 노트북만으로 풀을 만들면 리그 중간층에 맞춰진다.
- 평가 방식을 쓰기 전에 **이미 아는 결과를 재현하는지** 확인한다(7위의 99/99 재현처럼). 상대 분포가 실전과 다르면 짝 대결 결과를 승격 근거로 쓰지 않는다.
