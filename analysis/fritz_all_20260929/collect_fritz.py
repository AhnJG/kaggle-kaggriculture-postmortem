#!/usr/bin/env python3
"""FRITZALL: Fritz Cremer(teamId 16925604) 의 알려진 제출 3개의 공개 완료 경기 전부 목록 + replay 다운로드 + 검증.
top2400_fresh_20260929/step1_2_collect.py + step3_download_replays.py 를 합친 것. 날짜 필터·cap 없음.
사용: python3 analysis/fritz_all_20260929/collect_fritz.py list   → episodes_all.json, summary.json
      python3 analysis/fritz_all_20260929/collect_fritz.py download → raw/*.json.gz, 검증 결과를 episodes_all.json 에 기록"""
import os, sys, json, time, gzip, random, zipfile, csv
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import kaggle
OUT = "analysis/fritz_all_20260929"; RAW = "private_artifacts/fritz_all_20260929/raw"
TEAM_ID = 16925604; TEAM = "Fritz Cremer"
SUBS = [56613024, 56619080, 56647721]
os.makedirs(OUT, exist_ok=True); os.makedirs(RAW, exist_ok=True)
EP = os.path.join(OUT, "episodes_all.json")

def do_list():
    as_of = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    open(os.path.join(OUT, "as_of.txt"), "w").write(as_of)
    rows, summ, other_subs = [], {}, set()
    for sid in SUBS:
        eps = [json.loads(e.to_json()) for e in kaggle.api.competition_list_episodes(sid)]
        kept = 0
        for ep in eps:
            if ep.get("state") != "COMPLETED" or ep.get("type") != "EPISODE_TYPE_PUBLIC": continue
            ag = ep.get("agents", [])
            if len(ag) != 2: continue
            for a in ag:
                if a.get("teamId") == TEAM_ID and a.get("submissionId") not in SUBS: other_subs.add(a.get("submissionId"))
            me = [a for a in ag if a.get("submissionId") == sid]
            if len(me) != 1: continue
            me = me[0]; op = [a for a in ag if a is not me][0]
            if op.get("teamId") == TEAM_ID: continue
            r1, r2 = me.get("reward"), op.get("reward")
            if r1 is None or r2 is None: continue
            rows.append({"id": ep.get("id"), "seed": None, "fritz_submission_id": sid, "fritz_seat": me.get("index", 0),
                         "fritz_reward": r1, "op_reward": r2, "margin": r1 - r2,
                         "result": "W" if r1 > r2 else ("L" if r1 < r2 else "D"),
                         "op_teamName": op.get("teamName"), "op_teamId": op.get("teamId"), "op_submissionId": op.get("submissionId"),
                         "createTime": ep.get("createTime"), "endTime": ep.get("endTime"), "op_lb_score": None})
            kept += 1
        summ[str(sid)] = {"listed": len(eps), "kept": kept}
        print(f"[{sid}] listed {len(eps)} kept {kept}", flush=True)
    try: kaggle.api.competition_leaderboard_download("kaggriculture", path=OUT)
    except Exception as e: print("leaderboard error:", e)
    lb = {}
    zp = os.path.join(OUT, "kaggriculture.zip")
    if os.path.exists(zp):
        with zipfile.ZipFile(zp) as z:
            n = [x for x in z.namelist() if x.endswith(".csv")][0]
            for r in csv.DictReader(z.read(n).decode("utf-8-sig").splitlines()):
                try: lb[int(r["TeamId"])] = float(r["Score"])
                except Exception: pass
    for r in rows: r["op_lb_score"] = lb.get(r["op_teamId"])
    summ["total"] = len(rows); summ["fritz_lb"] = lb.get(TEAM_ID); summ["other_fritz_subs_seen"] = sorted(other_subs); summ["as_of"] = as_of
    json.dump(rows, open(EP, "w"), indent=1); json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
    print("total", len(rows), "fritz_lb", lb.get(TEAM_ID), "other_subs", sorted(other_subs))

def dl(api, eid, retries=8):
    gz = os.path.join(RAW, f"{eid}.json.gz")
    if os.path.exists(gz) and os.path.getsize(gz) > 10_000: return eid, True, "cached"
    from kagglesdk.competitions.types.competition_api_service import ApiGetEpisodeReplayRequest
    tmp = gz + ".tmp"
    for k in range(retries):
        try:
            time.sleep(random.uniform(0.1, 0.25))
            with api.build_kaggle_client() as c:
                q = ApiGetEpisodeReplayRequest(); q.episode_id = eid
                resp = c.competitions.competition_api_client.get_episode_replay(q)
                with gzip.open(tmp, "wb") as f:
                    for ch in resp.iter_content(chunk_size=128 * 1024): f.write(ch)
            if os.path.getsize(tmp) > 10_000: os.replace(tmp, gz); return eid, True, "downloaded"
        except Exception as e:
            time.sleep(4.0 * (k + 1) if "429" in str(e) else 1.0 + k)
            if k == retries - 1: return eid, False, str(e)[:200]
        finally:
            if os.path.exists(tmp): os.remove(tmp)
    return eid, False, "unknown"

def do_download():
    rows = json.load(open(EP)); ids = list(dict.fromkeys(r["id"] for r in rows))
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, f in enumerate(as_completed([ex.submit(dl, kaggle.api, e) for e in ids]), 1):
            eid, s, st = f.result(); ok += s; fail += (not s)
            if not s: print("FAIL", eid, st, flush=True)
            if i % 100 == 0: print(f"{i}/{len(ids)} ok {ok} fail {fail}", flush=True)
    mism = miss = 0
    for r in rows:
        gz = os.path.join(RAW, f"{r['id']}.json.gz")
        try: d = json.load(gzip.open(gz, "rt"))
        except Exception: r["replay_missing"] = True; miss += 1; continue
        info = d.get("info", {}); r["seed"] = info.get("seed", d.get("configuration", {}).get("seed"))
        tn = info.get("TeamNames") or []; rw = d.get("rewards") or []; s = r["fritz_seat"]; m = []
        if len(tn) > s and tn[s] != TEAM: m.append(f"seat_team {tn[s]}")
        if len(rw) > s and rw[s] != r["fritz_reward"]: m.append(f"reward {rw[s]} vs {r['fritz_reward']}")
        r["mismatch"] = m or None; mism += bool(m)
    json.dump(rows, open(EP, "w"), indent=1)
    print(f"download ok {ok} fail {fail}; verify total {len(rows)} missing {miss} mismatch {mism}")

def do_download2():
    """Slow path after 429s: copy replays already held in other private_artifacts dirs, then 1 request at a time with pauses."""
    import glob, shutil
    rows = json.load(open(EP)); have = {}
    for d in glob.glob("private_artifacts/*/raw"):
        if d == RAW: continue
        for f in os.listdir(d): have.setdefault(f, d)
    cp = 0
    for r in rows:
        fn = f"{r['id']}.json.gz"
        if not os.path.exists(os.path.join(RAW, fn)) and fn in have:
            shutil.copy(os.path.join(have[fn], fn), os.path.join(RAW, fn)); cp += 1
    print("copied from cache", cp, flush=True)
    ok = fail = 0
    for i, r in enumerate(rows, 1):
        eid, s, st = dl(kaggle.api, r["id"], retries=6)
        ok += s; fail += (not s)
        if st == "downloaded": time.sleep(6)
        if not s: print("FAIL", eid, st, flush=True); time.sleep(60)
        if i % 25 == 0: print(f"{i}/{len(rows)} ok {ok} fail {fail}", flush=True)
    do_download_verify(rows)
def do_download_verify(rows):
    mism = miss = 0
    for r in rows:
        gz = os.path.join(RAW, f"{r['id']}.json.gz")
        try: d = json.load(gzip.open(gz, "rt"))
        except Exception: r["replay_missing"] = True; miss += 1; continue
        info = d.get("info", {}); r["seed"] = info.get("seed", d.get("configuration", {}).get("seed"))
        tn = info.get("TeamNames") or []; rw = d.get("rewards") or []; s = r["fritz_seat"]; m = []
        if len(tn) > s and tn[s] != TEAM: m.append(f"seat_team {tn[s]}")
        if len(rw) > s and rw[s] != r["fritz_reward"]: m.append(f"reward {rw[s]} vs {r['fritz_reward']}")
        r["mismatch"] = m or None; mism += bool(m)
    json.dump(rows, open(EP, "w"), indent=1)
    print(f"verify total {len(rows)} missing {miss} mismatch {mism}")

{"list": do_list, "download": do_download, "download2": do_download2}[sys.argv[1]]()
