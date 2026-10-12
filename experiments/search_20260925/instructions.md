# SEARCH LOOP 20260925 execution contract

Authority: coordination/proposals/claude/20260925-SEARCH-LOOP-CODEX.md v2.3 and direct user approval.
No downloads, submissions, BOARD/KILLS edits, or direct HYPOTHESES edits.
Preserve prior artifacts and all original source bytes, including CRLF.
Engine: kaggle-environments1.32.7; locked Python and JSON SHA mandatory.

Order: NEWMETA exact + sustained Mac load report → parent tournament report → calibration → frozen metric → search → one holdout per checkpoint.
Stage1 runtime: 10000–10499 ×both seats against DP, fixed1000 games. Direct2400–2439, E5 2300–2309, panel47 as frozen EXP018 inventory. Panel never enters metric.
Tournament: all unique >=1000-line sources in09-24/25 scan. Dependency+cleanroom, then2300×both runtime gate; screening2500–2519×both×DP/NEWMETA; top5 confirmation2520–2559×both×DP/NEWMETA. Reject failed gates; never silently patch a source.
Runner: tools/search_loop.py. The controller alone appends games.jsonl and atomically replaces state.json. A trailing incomplete record is archived and truncated on resume; a corrupt committed record blocks. Output keys include scoped variant id+seed+seat+opponent SHA. Every row stores candidate,opponent,manifest,runner SHA.
workers6. OMP/BLAS threads1. 24GiB×70% maximum memory. If late5min throughput<=60% of initial5min, compare worker5. Never lower a runtime gate to compensate for load.
Initial/late throughput and 30min continuous measurement are diagnostic, not WDL selection.
launchd installation is performed by the user using the commands in the NEWMETA-EXACT report. KeepAlive+RunAtLoad template generated locally. Open-lid sleep inhibition uses caffeinate; do not change pmset settings.

Calibration numerical details not fixed in v2.3 were asked in one pending question before stage2. Until resolved, do not choose mutation steps or begin dependent calibration/search.
Success thresholds and checkpoint seeds remain exactly v2.3. Never access9000–9599 during preparation, calibration or search.
