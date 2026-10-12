# 외부 코드·데이터 provenance

수상 시 제출물과 **그 생성에 쓴 소스 전부**를 CC-BY 4.0으로 공개해야 한다(공식 Rules).
따라서 외부에서 가져온 모든 것을 처음부터 여기 기록한다. 나중에 복원할 수 없다.

## 기록 양식
| 항목 | URL | 저자 | 라이선스 | 수집일 | 엔진 버전 | 용도 |
|---|---|---|---|---|---|---|

## 현재 항목

| 항목 | URL | 저자 | 라이선스 | 수집일 | 엔진 버전 | 용도 |
|---|---|---|---|---|---|---|
| kaggle-environments 1.32.7 | https://pypi.org/project/kaggle-environments/1.32.7/ | Kaggle | Apache-2.0 | 2026-09-06 | — | 게임 엔진 |
| opponents/public/boatlee.py | https://www.kaggle.com/code/boatlee/v16-rc5-high-score-8c-4s-premium-market-lead | boatlee | Apache-2.0 | 2026-09-06 | 1.32.7 | 벤치마크 상대 (v16-rc5) |
| opponents/public/kaitofukami.py | https://www.kaggle.com/code/kaitofukami/25-27-strict-future-v27-midgame-meta-reset | kaitofukami | Apache-2.0 | 2026-09-06 | 1.32.7 | 벤치마크 상대 (v27) |
| opponents/public/raykkretzschmar.py | https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta | raykkretzschmar | Apache-2.0 | 2026-09-06 | 1.32.7 | 벤치마크 상대 (C95) |
| opponents/public/lynnsakurai.py | https://www.kaggle.com/code/lynnsakurai/farming-score-a-mathematical-approach | lynnsakurai | Apache-2.0 | 2026-09-06 | 1.32.7 | 벤치마크 상대 (Farming Score) |
| releases/public-yhay81-shop-router-0909-exact | https://www.kaggle.com/code/yhay81/shop-router-0909 | Yusuke Hayashi (upstream aurax7) | Apache-2.0 (tar 내 LICENSE.txt) | 2026-09-09 | 1.32.7 | 제출 56147691·56330776 (exact) |
| releases/public-lynnsakurai-farming-score-v2-exact | https://www.kaggle.com/code/lynnsakurai/farming-score-v2-a-better-approach | lynnsakurai (+ 본문에 명시된 upstream 다수) | Apache-2.0 (본문 SPDX·notice 표기, tar 내 별도 LICENSE 파일 없음) | 2026-09-18 | 1.32.7 | F0 exact 후보 P2 (수집본 기준 빌드) |
| releases/public-alperen-before-dawn-stock-cash-sales-exact | https://www.kaggle.com/code/alperen5252525/kaggriculture-before-dawn-stock-cash-sales | alperen5252525 (+ nathanjacob Pipe-8 등) | Apache-2.0 ("All inherited Apache-2.0 license text and author notices remain in main.py") | 2026-09-18 | 1.32.7 | F0 exact 후보 P1. 09-19 원문 조회 403 (비공개/삭제 추정) |
| releases/public-tetsutani-market-smart-farming-exact | https://www.kaggle.com/code/tetsutani/market-smart-farming-kaggriculture | tetsutani | 본문 라이선스 문구 없음 → Kaggle 공개 코드 규정(Rules §7.b, OSI 라이선스 간주) | 2026-09-16 | 1.32.7 | F0 exact 후보 P3 |
| releases/public-ahmedberatozer-kaggriculture-v56-smarter-seeds-and-fertilizer-exact | https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer | ahmedberatozer | Apache-2.0 | 2026-09-22 | 1.32.7 | step 91 bot exact X (V56) |
| docs/code/*.ipynb 16건 | Kaggle 공개 노트북 | 각 저자 | Apache-2.0 (Kaggle Rules §7.b) | 2026-09-06 | 각기 다름 | 분석·상대 원본 |
| docs/discussion/*.md 6건 | Kaggle 공개 디스커션 | 각 저자 | 인용만 | 2026-09-06 | — | 사실 수집 |

## 주의
- **리플레이에서 추출한 "행동"은 사실 데이터**이고, 공식적으로 공개·다운로드 가능하며 운영진이
  IL/BC 용도를 명시했다. **남의 코드를 복사하는 것과는 라이선스 관점에서 다르다.**
- 공개 노트북 코드를 실제로 쓸 경우 **원본 Kaggle 페이지에서 라이선스를 먼저 확인**하고 이 표를 채운다.
- 팀 밖으로 우리 코드를 사적으로 공유하는 것은 **실격 사유**다.
| url | author | license | date | version |
| https://www.kaggle.com/code/nathanjacob/kaggriculture-pipe16-idle-workers | nathanjacob | Apache-2.0 | 2026-09-21 | 1.32.7 |
| https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v51-lean-flock | ahmedberatozer | Apache-2.0 | 2026-09-21 | 1.32.7 |
- **ahmedberatozer/kaggriculture-v53-opening-signature**: Apache-2.0, downloaded 2026-09-21, Kaggle Environment 1.32.7
| tetsutani/demand-preserving-turn-sale-timing (09-24 버전, = prvsiyan frontier moon/soil 09-24) | Apache-2.0 (NOTICE.txt 동봉) | releases/public-tetsutani-demand-preserving-0924-exact main 178ae0f7…d3a | 2026-09-24 Claude |
