# EXP-061 donor route (Claude Opus 5.5, 2026-09-30 00:05 KST — Codex 사용량 소진으로 Claude 가 수행)
- 사람 승인(09-29 23:00): 다른 팀 경기의 farmer+hands+market 전체를 route 로 쓰는 것 허용. market 만 떼어 붙이기(K3) 금지.
- 후보: survey300 에서 순위 R1–R100 팀이 이긴 193판 중, 같은 seed·좌석에서 d157 을 상대 기록으로 step 145 까지 돌렸을 때 d157 농장(tiles·farmer·hands·땅)이 기록된 그 팀 농장과 step 144 에 같은 29판(9팀). 행동 순서 중복 제거 후 29 route (D 12, S 11, Y 6). scan.jsonl, make_dn.py.
- 변형 DN{i}: d157 바이트 + 파일 끝 layer. 거울판(rg_layer 와 같은 판정)이고 첫 두 상점이 donor 의 그룹이면 step 144 에 donor route 로 전환. step 648 끝내기 route 2 전환은 그대로.
- 스모크 4경기 오류 0 (DN 4판 모두 짐, 같은 tape 의 d157 은 3승 1무 — 참고만).
- 빠른 screen(결과 전 고정): DN 마다 그 그룹 M1 screen tape 앞 10판(290경기). DN 평균 점수가 같은 10판의 d157 평균 이상인 DN 만 40판 screen 으로 넘어간다. 없으면 EXP-061 종료.
- 40판 screen 을 통과한 DN 은 EXP-060 PREREG 의 M2 규칙(그룹별 상위 3 에 포함 여부, +0.05, 90% 하한)을 그대로 따른다.

## 결과 1 (00:35 KST)
- 빠른 screen 290+30경기, 오류 0. 29개 중 27개가 d157 보다 −0.1~−0.55. 통과 DN29(Y, R95) +0.3, DN27(Y, R85) 0.0.
- 40판 screen(Y): DN29 0.725 대 d157 0.500 (+0.225; 새 30판만 +0.20), DN27 0.588 (+0.087). → 규칙대로 M2 후보 자격(그룹 상위 3 판정은 M1 FM 결과와 합쳐서).

## EXP-061b (00:35 KST, 결과 전 고정)
- 같은 방식으로 순위 R101–R300 팀이 이긴 경기에서 donor 를 더 모은다(scan61b.jsonl). 같은 빠른 screen 규칙(그룹 screen tape 앞 10판, d157 이상만 40판) 을 적용. 40판 결과가 그룹 M1 상위 3 안에 들면 M2 에 합류.
