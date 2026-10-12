# EXP-007 — 두 번째 슬롯: thomas replay router v2 (공개, 다른 계보)

hypothesis_id: HYP-0007
test_id: TEST-0007

사전등록 2026-09-11 13:33 UTC (Claude). 확인 실행 전 커밋. 커밋 후 seeds·임계 변경 금지.
사람 결정(2026-09-11): 공개 코드 파생물 최종 슬롯 사용 허용 · 두 번째 슬롯은 thomas 라우터로 전환.
배경: 군중 회피형 품목 치환은 스크리닝 실패(F-T11). 같은 스크리닝에서 thomas 는 풀 0.957(parent 0.936), parent 패배 9셀 중 7셀 승.

```yaml
id:            EXP-007
parent:        (계보 다름) 비교 기준 = exp006 hosted 56165718, tar 1c478c249079075d28d0ce7e1fbd5e305007f196c1f1b6b05c8b3b1d4ba59721
candidate:     releases/public-thomas-replay-router-v2-exact/submission.tar.gz (Codex 빌드, 무수정)
               # sha256 8031d51abe010eb4ccb924b90e9ebc8173a7183df55d3c1db885a8217b514180 (48,928 B), member main.py 8241246765098c50223d897739cb32076b71a303284d2e5e1c5f0fb495bb5a97
               # 출처 thomastschinkel/kaggriculture-95-5-win-rate-via-replay-routing v2 (kaggle_id 133468879), notebook sha 7e3c9917…23c
one_change:    두 번째 활성 슬롯 A -> B : yhay81 복사본 56147691 -> thomas router v2 exact (코드 변경 0줄)
fixed:         [tar 바이트 동일, 엔진 1.32.7, exp006 불변]
hypothesis:    H1 강도: 풀 점수 ≥ 0.80 · H2 비상관: exp006 이 이기지 못한 풀 셀(A, 6셀) 중 thomas 승 ≥ 3셀
opponents:     tape pool = private_artifacts/tapes/*.json 47개 (풀 해시 201d9724…6e1) · public 4봇 (EXP-006 과 동일 SHA) · h2h = exp006 tar 해제본 · self
seeds:         pool [5101, 5102, 5103] / public [5101..5105] / h2h [5201..5210] / self [5301, 5302]
               # exp006 결과 재사용: evidence/raw/EXP-006/pool_cand.jsonl ce631165… · public_cand.jsonl cfd2fdbe… (결정론 F-T4)
               # A = exp006 비승리 풀 셀 6개: 3정훈_105975926 s5103 좌석0·1 / Crop_Dusta_105975926 s5103 좌석0·1 / binghua_105943236 s5102 좌석0·1
seats:         both
metric:        G1 풀 점수(282) · G2 A 셀 thomas 승 수 · G3 공개봇 thomas L(40) · G4 안전(thomas player-run 기준): shed_unsold, manual_drop_lost, end_animals, discard 최대/run, end_units 평균/run
               G5 status≠DONE, CPU s/episode 최대, p99 ms 최대 · G6 self 2판 DONE
               진단: h2h vs exp006 W/D/L(20), 두 봇 중 하나라도 이긴 풀 셀 비율, P(thomas 패 | exp006 패), 셀 결과 phi 상관
success:       G1 ≥ 0.80 AND G2 ≥ 3 AND G3 L ≤ 4 AND G4 shed_unsold = 0 AND manual_drop_lost = 0 AND end_animals = 0 AND discard ≤ 20/run AND end_units 평균 ≤ 5/run
               AND G5 = 0·≤ 5.0 s·≤ 5.0 ms AND G6 2/2                                                  -> 제출 가능(사람 실행)
failure:       G1 < 0.70 OR G2 ≤ 1 OR G3 L ≥ 8 OR G4·G5·G6 중 하나라도 위반                              -> 제출 안 함
inconclusive:  나머지 (0.70 ≤ G1 < 0.80, 또는 G2 = 2, 또는 5 ≤ G3 L ≤ 7)                                -> 제출 안 함, seeds 추가 금지
next_if_success: 사람 제출 -> 활성 {exp006, thomas} -> 최종 2슬롯 후보 쌍
next_if_failure: 제출 안 함 -> 두 번째 슬롯은 exp006 판독(09-12 13:00 UTC 이후) 뒤 재결정
artifact:      evidence/raw/EXP-007/ · 판정 스크립트 동 폴더 · 하니스 sellaudit.py a4dc3443… · pool.py 0c6777df…
```

## §7.5 체크리스트 (Ledger 제외 제출 전)
```
Identity:  tar sha256 8031d51a…0180 = 확인 실행에 쓴 해제본 main.py 8241246… 와 일치                         [PASS]
Schema:    루트 main.py 단일 · get_last_callable 마지막 callable = agent · __file__ 불사용 · guard 없음(원본 무수정) → 344판 status 로 확인 [PASS]
Runtime:   CPU ≤ 5.0 s/episode · p99 ≤ 5.0 ms                                                                     [PASS: 0.41 s · 0.13 ms · 최대 턴 397 ms]
Isolation: 빈 폴더 해제 → get_last_callable 로드 → starter 상대 720 steps DONE · path self 720 steps DONE             [PASS]
License:   Rules 3.6b 공개 공유 코드 = OSI 간주 · 출처 메타 releases/public-thomas-replay-router-v2-exact/manifest.json
           주의: 스케줄은 다른 팀 리플레이에서 온 "donor schedules"(main.py:630-647) — 사람이 공개 코드 파생 허용으로 승인        [PASS(사람 승인 근거)]
Ledger:    (제출 후) submission ID ↔ tar sha ↔ episodes                                                             [ ]
```

## 은퇴 · 타이밍
- 지금 제출하면 FIFO 로 **yhay81 복사본 56147691 이 은퇴**하고 활성은 {exp006 56165718, thomas}. EXP-006 의 복사본 대비 hosted A/B 판독은 사라진다.
- A/B 를 살리려면 2026-09-12 13:00 UTC(exp006 경과 24h) 판독 뒤 제출. 선택은 사람.

## 결과 — 2026-09-11 14:09 UTC · 사전등록 판정 **SUCCESS** · 독립 검증자 의견 **제출 불가** (사람 결정 필요)

원자료 `evidence/raw/EXP-007/` · 344판 결측 0, 전부 DONE.

| 게이트 | 임계 | 값 |
|---|---|---|
| G1 풀 점수 (282) | ≥ 0.80 | **0.9433** (exp006 0.9787) |
| G2 A 셀(exp006 비승리 6) 중 thomas 승 | ≥ 3 | **4** |
| G3 공개봇 L (40) | ≤ 4 | 40-0 |
| G4 안전 | shed_unsold·수동DROP·가축 0, discard ≤ 20/run, 종료 PRODUCTS 평균 ≤ 5 | 0·0·0, 최대 9, 평균 3.1 (최대 10) |
| G5·G6 | DONE, CPU ≤ 5 s, p99 ≤ 5 ms, self 2/2 | 통과 (0.41 s, 0.13 ms) |

진단: 둘 중 하나라도 이긴 풀 셀 99.29% (exp006 단독 97.87%) · 패배 2×2 both 2 / thomas만 14 / exp006만 4 / 둘 다 승 262, phi 0.176 · h2h thomas vs exp006 4-0-16.

독립 검증(서브에이전트) — Identity·7판 재현·판정 재계산 PASS. 반대 의견과 Claude 판단:
1. **실효 표본 3쌍**: 좌석 교대가 정보를 더하지 않아(exp006 141/141쌍, thomas 승패 라벨 0/141 flip) G2 는 쌍 단위 2/3. 타당. 보강 자료(탐색, 사전등록 아님): 스크리닝에서 parent 패배 9쌍 중 thomas 7승 → 합산 9/12쌍.
2. **thomas 패배가 Jiro2 테이프에 집중**(thomas만 진 7쌍 중 5쌍): 검증자는 다양성 주장과 배치된다고 봄. Claude 판단: exp006 패배는 3정훈·Crop_Dusta·binghua 에 몰리므로 약점 군집이 서로 다른 것 자체가 비상관의 형태다.
3. **Codex manifest 의 silent-failure gate FAIL/HOLD**(sell_unfilled 31–6,193, self seed 5301 에서 7,000,410): F-T7 의 sentinel 과다요청 착시와 같은 정의다. 교정 지표(G4)는 전부 통과. 단 gate 재정의는 아직 사람 승인 전이므로 사람이 명시적으로 수용해야 한다.
4. "thomas 는 exp006 보다 약해 대체 근거가 박약": thomas 는 exp006 이 아니라 **yhay81 복사본 슬롯**을 대체한다. 복사본은 exp006 과 같은 계열이라 패배가 거의 그대로 겹친다.
5. 판정 스크립트 버그: self 판을 슬롯마다 중복 집계(end_units 평균 3.107 → 정정 3.125). 판정 불변.
