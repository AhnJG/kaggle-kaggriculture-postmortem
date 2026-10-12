# EXP-062 coordination (Claude-B, 09:58 KST)
- Claude session context was reset around 09:20-09:50 KST (container replaced). Claude-B continues from files: PREREG.md (A1-A4), s1/s2 designs, judge_s1/judge_s2, q/ runner.
- Running (A): j03 S1 kaggle collect, j04 S2A kaggle (waits S1 collect), j05 S2B mac, j08 nm (waits j05), j09 S1L2 kaggle (waits S2A).
- B changes: run62.py now reads W62|W and OUT62|EXP024_OUT (compatible). B killed its own j03_cal (d157/c26/X vs pool11, seeds 620000+).
- B adds j11: after j08 -> S1-cal (c26, X as candidates vs S1 pool, S1 seeds; evaluator calibration: real c26 < d157) -> S1L2 on Mac (same jobs-s1L2.json, games-s1L2-mac.jsonl; judge dedups by key).
- Submission: only via submit62.sh with SUBMIT_OK_<v> flag. Check `kaggle competitions submissions` before any submit (FIFO: next submit retires X 56675447).
