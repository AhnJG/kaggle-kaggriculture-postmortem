"""Render the EXP-018 report from preserved episode-level evidence."""
import csv
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'experiments/results/dp_loss_cause_20260925'
REPORT=ROOT/'coordination/reports/codex/20260925-1340-DP-LOSS-CAUSE.md'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows=list(csv.DictReader((ROOT/'analysis/dp_hosted_20260924/opponents.csv').open()))
    byid={r['episode']:r for r in rows}
    q1=read(OUT/'q1_summary.json');q2=read(OUT/'q2_refresh_summary.json')
    q4=read(ROOT/'analysis/exp018_panel/summary.json');q5=read(OUT/'q5.json')
    verified=read(OUT/'verification.json');freeze=read(OUT/'freeze.json')
    lines=['# DP-LOSS-CAUSE — 필수 DP 하한 미달, 후보 채택 불가',
           '',
           '1. 무엇을 시험했는가: DP 0924의 기존 판매 예측 갱신 주기 하나를 3턴에서 2턴으로 바꿨다. 부모 바이트 전체 뒤에 `_V92_P_EVERY = 2`만 덧붙였다.',
           '2. 왜 했는가: herd-safe 상대의 반복 패배에서 후반 STRAWBERRY 판매 단가가 낮았고, 두 코드의 기존 예측 갱신 주기가 달랐다. 원인 후보였으며, 같은 판매 층을 새로 붙이지 않았다.',
           '3. 결과: [LOCAL] 유효 hosted 복제 패널은 부모 23승/0무/24패 → 후보 28승/0무/19패. 그러나 DP 직접 대결은 22승/34무/24패, 39/80 = **0.4875 < 0.50**이다. 따라서 최종 SUCCESS 및 B-2 모두 불가다.',
           '4. 다음: 추천 패치·Q5 exact 후보 모두 없음. release와 제출을 하지 않았다. 기준·seed·카드 SHA를 바꾸거나 근소한 미달을 재시험하지 않는다. 결과를 Coordinator에 인계한다.',
           '',
           '## 판정의 의미',
           '',
           '**VERIFIED_NOT_ELIGIBLE_DP_FLOOR**: 실행/identity 오류로 막힌 BLOCKED가 아니라, 유효하게 측정한 필수 하한 미달이다. 원자료의 `panel_verdict=SUCCESS`는 본문 패널 조건만 통과했다는 뜻이며 `eligible_success=false`와 함께 읽는다. 09-25 상단 조건을 적용한 최종 SUCCESS가 아니다. 분모·SE·임계값을 사후 변경하지 않았다.',
           '',
           '원래 00:17 BOARD 차단 보고는 역사로 보존한다. 00:45 재개 지시로 해소한 뒤 이 작업을 수행했다. 중단 후에는 기존 프로세스의 완료 결과를 회수했으며, 완료한 경기를 다시 실행하지 않았다.',
           '',
           '## Q1 — 실제 체결, 구매 시점, 패배 묶음',
           '',
           '[LOCAL replay audit] 319개 저장 replay의 시장 주문을 고정 엔진 1.32.7로 재계산했다. pre-state → unit actions(atomic PLANT 포함) → market 순서이며, SELL 요청량이 아니라 `_commit_unit` 성공 수량과 가격이다. 288,360회 player-step 현금 검산이 저장 post-state와 일치했다. 재현: `python3 tools/dp_loss_cause.py describe`.',
           '',
           '- 전체 패배 199, 제외 submission56502662의 패배 28은 표시만, 유효 패배 171. LB<2400 패배는 전체95/유효76이다.',
           '- 모든 경기의 d0–11/d12–18/d19–29 품목별 판매 수량·평균가·구간 끝 cash: `experiments/results/dp_loss_cause_20260925/q1_period_sales.csv`.',
           '- 실제 HIRE/BUY_LAND/BUY_ANIMAL 시점: 같은 폴더 `q1_purchases.csv`. 구매 요청과 실제 증가를 구분했다.',
           '- 경기별 원래 metadata, raw SHA, trade ledger, postmortem: 같은 폴더 `episodes/<episode>.json`.',
           '- `postmortem`의 bank_a/b는 원래 seat0/1이다. DP seat1이면 gap 부호를 반대로 읽어야 한다. 아래 근거112606102와112786680은 DP seat0다.',
           '',
           '### 최우선 herd-safe FULL — 두 반복 증상',
           '',
           '| 묶음 | 유효 패배 수 | 최종 margin 합 | 상대 LB 중앙값 | 관측된 결정/시험 |',
           '|---|---:|---:|---:|---|']
    for name,explanation in [('refresh','d19–29 STRAWBERRY 평균 판매가 열세; 기존 예측 refresh 3→2'),('carrot','전체 CARROT 판매 수량 부족; 기존 전환 margin -5→-15 (미실행)')]:
        rs=[byid[e] for e in q1['screening'][name]]
        lines.append(f"| {name} | {len(rs)} | {sum(float(r['margin']) for r in rs):.0f} | {statistics.median(float(r['op_lb_score']) for r in rs):.2f} | {explanation} |")
    lines+=['','두 묶음은 겹치므로 합산하지 않는다. 원본 herd FULL은 DP1승15패이나, 제외 submission의3패를 빼면1승12패다. 112606102의 첫 지속 분기는 day9 gap−4, 최악 day26의 gap 변화−389, 최종−499; 112786680의 최악 day28 변화−812, 최종−1897 (`tools/postmortem.py:build_report` 적용 결과). 후반 단가 차이가 모든 초기 분기와 모든 패배의 원인이라는 주장은 하지 않는다.',
              '',
              f"[INFERENCE, sampling correction] 승리 재가중 후 herd FULL 비중은 전체 non-draw 기준 {100*q1['field']['herd_share_all']:.3f}%, 제외 submission을 뺀 non-draw 기준 {100*q1['field']['herd_share_eligible']:.3f}%다. 다운로드 표본의 15패를 field의 큰 비중이라고 읽지 않는다.",
              '',
              '### DP-prefix 상대 — 첫 행동 분기',
              '',
              '상단 우선순위의 17패 전부를 확인했다. 상대의 실제 pre-observation에 fresh DP를 순서대로 호출한 비교다. 상대의 비공개 코드나 원인 효과를 재구성했다는 뜻은 아니다. action_row는 replay의 행 번호, decision step은 그보다1 작다. 결과 원문: `q1_dp_prefix_divergences.json`.',
              '',
              '| Episode | submission 제외 표시 | decision step / action_row | 최초 다른 내용 (DP 예상 → 실제 상대) |',
              '|---|---|---|---|']
    for x in read(OUT/'q1_dp_prefix_divergences.json'):
        r=x['metadata'];d=x['first_difference']
        if d:
            p=d['dp_on_op_observation'];o=d['hosted_op_action']
            keys=[k for k in set(p)|set(o) if p.get(k)!=o.get(k)]
            detail='; '.join(f'{k}: {p.get(k)} → {o.get(k)}' for k in sorted(keys))
            step=f"{d['decision_step']} / {d['action_row']}"
        else:step='N/A';detail='719개 행동 전부 일치; 수집기의 prefix label만으로 변형이라고 단정할 수 없음'
        lines.append(f"| {r['episode']} | {'56502662 제외' if r['submission']=='56502662' else '유효'} | {step} | `{detail}` |")
    lines+=['','추가 WOOL 판매, 판매 수량·순서, 씨앗/사료 구매 등의 차이가 관측됐다. 이들은 후속 가설 자료이며 Q2 최우선 후보가 선택 조건을 통과했으므로 별도 패치로 실행하지 않았다.',
              '',
              '### 나머지 반복 패배 묶음',
              '',
              '최초로 구간 끝 cash가 뒤진 구간과 그 구간에서 가장 큰 판매수입 부족 품목으로 묶은 **증상 분류**다. 구매비·판매시점 차이도 cash에 영향을 주므로 표를 확정 원인으로 읽지 않는다. 아래는 유효 표본에서5경기 이상인 묶음만 표시한다. 개별 기록은 q1_summary와 CSV에 보존했다.',
              '',
              '| 우선순위 | 첫 cash 열세 구간 | 최대 판매수입 부족 | 경기 수 | margin 합 | 상대 LB 중앙값 |',
              '|---|---|---|---:|---:|---:|']
    for g in q1['groups']:
        if g['excluded_submission'] or g['tier'] in ['1-herd-full','2-dp-prefix']:continue
        rs=[byid[e] for e in g['episodes'] if not (byid[e]['op_lb_score'] and float(byid[e]['op_lb_score'])>=2600 and byid[e]['match_full']!='True')]
        if len(rs)<5:continue
        period={'0':'d0–11','1':'d12–18','2':'d19–29'}.get(g['first_negative_period'],'N/A')
        lines.append(f"| {g['tier']} | {period} | {g['largest_sales_deficit_item']} | {len(rs)} | {sum(float(r['margin']) for r in rs):.0f} | {statistics.median(float(r['op_lb_score']) for r in rs):.1f} |")
    lines+=['','LB≥2600이고 FULL 공개 파일이 확인되지 않은 상대 패배: **전체37 / 유효33 / 제외4**. 사설 코드 여부 자체는 N/A이며 더 상세한 전략 분석이나 패치 우선순위를 부여하지 않았다.',
              '',
              '## Q2 — 사전 고정 8경기 closed-loop',
              '',
              '| Episode | 부모 margin | 후보 margin | 변화 | 패→승 |','|---|---:|---:|---:|---|']
    for r in q2['results']:lines.append(f"| {r['episode']} | {r['parent_margin']:.0f} | {r['candidate_margin']:.0f} | {r['margin_change']:+.0f} | {'Y' if r['flipped'] else 'N'} |")
    lines+=['','3/8이 strict win으로 전환되어 Q2 기준(≥3)을 통과했다. draw는 전환으로 세지 않았다. 사전 순서에 따라 carrot fallback은 **미실행**이다. 같은 방향 재조정0회. open-loop 반사실 게임은 실행하지 않았고 Q1의 관측 비교를 반사실 성과로 세지 않는다.',
              '',
              '## Q3 / Q4 — 변경과 최종 판정',
              '',
              '변경: 부모7333줄을 한 바이트도 바꾸지 않고 끝에 `_V92_P_EVERY = 2`를 추가했다. `_ADV_LOOK=4`, 최종 SELL 재정렬, 기존 예측 horizon은 보존했다. 마지막 callable은 `_final_sell_block_reorder_entrypoint`다. 부가 wrapper·네트워크·파일 로딩은 추가하지 않았다. release는 추천 조건 미달로 생성하지 않았으며 E-5 clean-room/tar gate는 N/A다.',
              '',
              '패널 inventory59(29L/30W) 전체를 freeze에 보존했다. 상단의 submission56502662 제외를 적용해12(5L/7W)를 판정에서 제외했다. 유효47(24L/23W) 전부를 실행했다. 부모47경기는 양쪽67,586개 행동·67,680개 projected state가 원본과 정확히 일치했다. 고유seed47개, 원래 DP좌석 그대로다.',
              '',
              '| 항목 | 부모 | 후보/결과 | 판정 |','|---|---:|---:|---|',
              '| 유효 패널 W/D/L | 23/0/24 | 28/0/19 | 5패→승 |',
              f"| 패널 점수율 | {23/47:.8f} | {28/47:.8f} | Δ={q4['delta']:.8f} |",
              f"| paired SE / 2SE | — | {q4['paired_se']:.8f} / {q4['two_se']:.8f} | Δ>2SE PASS |",
              '| 기존 승리의 새 패배 | — | 0 ≤ 5/3 | PASS |',
              '| DP 직접 80경기 W/D/L | — | 22/34/24 | 39점/80 |',
              '| 필수 DP 하한 | ≥0.50 | **0.4875** | **FAIL; SUCCESS/B-2 불가** |',
              f"| DP 40seed paired SE | — | {q4['dp80_seed_paired_se']:.8f} | 참고값, 하한은 point score |",
              f"| 후보 최대 step | <0.5s | {q4['max_step_seconds']:.9f}s | PASS |",
              '| 예외 / caught-error telemetry / 비정상 종료 | 0 | 0 | PASS |',
              '',
              '직접80경기는 seed2400–2439×양좌석을 모두 완료했다. 0.50에 필요한40점보다1점 부족하며, 반올림해서 통과시키지 않는다. body의 선택20경기를 필수80경기로 대체한 것은 실행 전 카드에 명시했다. Q2의16실행을 재사용해 전체 actual game 실행은174회(Q2 16 + 추가 패널78 + DP80 80)다.',
              '',
              '패널은 Q1/Q2에도 사용한 development 자료다. 이 결과의 SE는 고정 sample의 기술 통계이며 독립 holdout의 선택 편향 보정값이나 hosted BT 우위 증명이 아니다. Runtime은 serial local 측정이며 hosted runtime은 N/A다.',
              '',
              '### DP 비중 시나리오 — 보고용, 판정에 사용하지 않음',
              '',
              '| DP 비중 | 부모 기대 점수율 | 후보 기대 점수율 | 변화 |','|---|---:|---:|---:|']
    for r in q4['scenarios']:lines.append(f"| {100*r['dp_share']:.4f}% ({r['label']}) | {r['parent']:.6f} | {r['candidate']:.6f} | {100*r['delta']:+.4f}%p |")
    coverage=sum(r['weight'] for r in q4['panel'])/743
    lines+=['',f'승리 weight=각submission의 전체승리/샘플승리, 패배weight=1. FULL 유효 패널의 가중치 합은154.4이며 유효 non-draw field743의 **{100*coverage:.2f}%**를 대표한다. 나머지 상대 효과를0으로 채워 full-field 예측으로 제시하지 않았다. 전체884헤더 중 draw19의 replay가 없으므로 non-draw 조건부 추정이다.',
              '',
              '현재1.6839%는 **유효 FULL 패널의 exact-DP 비중**이다. 넓은 DP-prefix를 포함한 유효 수집 표본의 재가중 비중은3.7506%(전체submission은3.4528%)로 별개다. 비공개 DP 변형을 exact-DP로 간주하지 않았다. 혼합식은 카드대로 non-DP weighted mean×(1−p)+DP직접점수×p, 부모mirror는 양좌석 평균0.50이다. 조건부 시나리오가 양수여도 필수하한을 면제하지 않는다.',
              '',
              '## Q5 — 다른 계열 exact 후보',
              '',
              '| 공개 FULL 계열 | DP W/L (다운로드 표본) | 사용 팀 LB 중앙값 | 범위 | 추천 |',
              '|---|---:|---:|---|---|']
    for r in q5['families']:
        if not r['dp_l']:continue
        why='상단 Q5 보정으로 상성 상대만' if r['family']=='herd-safe-v3-experimental-risk-aware-feed' else '팀 집단 LB 근거 부족'
        lines.append(f"| {r['family']} | {r['dp_w']}/{r['dp_l']} | {r['median_team_lb']:.2f} | {r['min_team_lb']:.1f}–{r['max_team_lb']:.1f} | 없음: {why} |")
    lines+=['','DP 외부7팀 LB 중앙값2435.9 (Sian 수렴 중2069.1은 외부그룹에서 제외), 조회snapshot09-24 11:43:08 UTC. herd는지시대로 제외한다. pipe18은 높은 팀2466.5도 있으나 집단 중앙값2305.0이고, 유효 FULL에서는 DP2승2패다. 단일 고점 팀과 다운로드의 과대표집된 패배만으로 Y를 추천하지 않는다. 다른 패배유발 공개계열의 팀LB도 이 기준집단에 못 미친다. 새Y closed-loop 우위 시험은 N/A; **추천할 Y 없음**이다. 경로·raw SHA는 `q5.json`에 보존했다. 팀 최고LB를 해당submission의 점수로 간주하지 않는다.',
              '',
              '## Artifact identity와 검증',
              '',
              '| 파일 | SHA-256 |','|---|---|']
    paths=[ROOT/freeze['card'],OUT/'freeze.json',ROOT/'releases/public-tetsutani-demand-preserving-0924-exact/main.py',ROOT/freeze['candidates']['refresh']['path'],ROOT/'tools/dp_counterfactual.py',ROOT/'analysis/exp018_panel/summary.json',OUT/'verification.json']
    for path in paths:lines.append(f'| `{path.relative_to(ROOT)}` | `{sha(path)}` |')
    lines+=['',f"카드/입력 freeze 시각은 **{freeze['frozen_at_utc']}** (09-25 00:59:43 KST), Q2 및 Q4 실행 전이다. source/opponent/raw319개 등을 포함한351개 입력 SHA가 종료 검산에서도 동일했다. 기록의 Q4 `started_at`은 runner가 결과 저장 직전에 쓴 시각이므로 정밀한 game 시작시각으로 인용하지 않는다; 사전 freeze는 별도 freeze.json과 Q2 실행 전 기록으로 확인한다.",
              '',
              '실행한 검증:',
              '',
              '- `python3 tools/dp_loss_cause.py audit` — 엔진 lock, 원자료 및 패널 제외 대조 PASS.',
              '- `python3 tools/dp_loss_cause.py describe` — 319개 replay, 288360 cash checks PASS.',
              '- `python3 tools/dp_loss_cause.py summarize` 및 `divergences` — Q1 집계·17패 최초 분기 기록.',
              '- `python3 -m unittest tests.test_reproduce_replay -q` — 5 tests PASS (2.821s).',
              '- `python3 tools/dp_counterfactual.py --freeze experiments/results/dp_loss_cause_20260925/freeze.json --candidate refresh` — 고정Q2 8개 모두 완료, 3flip.',
              '- 같은 command에 `--phase q4` — 패널47개 양artifact 및 DP80 완료, exit0은 실행완료이며 후보승인이 아님.',
              '- `python3 tools/verify_dp_loss_results.py` — 2039 checks PASS, 별도 계산으로 `VERIFIED_NOT_ELIGIBLE_DP_FLOOR`.',
              '- `python3 tools/validate_hypotheses.py --strict` — exit0, hypothesis ledger PASS:37 entries. HYP-0016 결과와 HYP-0037 fallback 미실행을 updater event로 기록했다.',
              '',
              'Q2/Q4 runner와 카드·freeze·측정결과는 검산 중 수정하지 않았다. BOARD/KILLS/다른 owner 문서는 직접 고치지 않았다. HYPOTHESES는 updater만 사용한다. 공유 원장에는 다른 agent의 기존 미커밋 변경도 있으므로 해당 전체 diff를 이번 commit에 섞지 않는다; 이번 immutable events가 변경 근거다.',
              '',
              '다음 행동 두 가지: ① Coordinator가 이 gate 실패와 후보 미채택을 BOARD에 반영한다. ② 현재 DP의 다음 hosted snapshot과 새 공개 계열을 확인하되, 이 카드의 seed 추가·threshold 완화·fallback 뒤늦은 실행으로 미달을 우회하지 않는다.',
              '',
              'VERDICT | VERIFIED_NOT_ELIGIBLE_DP_FLOOR — 패널 조건 PASS, 필수 DP80 하한 FAIL | 후보 f3e727b175eac13b702c3de34191b2cff170e30220bcb108b1010fc782505052 | independent arithmetic/identity audit 2039 checks PASS | NEXT ACTION: 후보 채택 없이 Coordinator 인계; release·제출 없음']
    REPORT.write_text('\n'.join(lines)+'\n')
    print(REPORT)


if __name__=='__main__':
    main()
