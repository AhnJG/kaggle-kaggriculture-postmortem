"""Independent, read-only SURVEY300 snapshot analysis per frozen PLAN.md.

No bot or engine is imported. Observational differences are not efficacy tests.
"""
import collections
import csv
import json
import math
import random
import statistics as stats
import zipfile

SNAP = "experiments/fp_survey300/snapshots.jsonl"
EPISODES = "analysis/survey300_20260929/episodes_all.json"
TARGETS = "analysis/survey300_20260929/targets.json"
LB = "analysis/survey300_20260929/kaggriculture.zip"
OUT = "experiments/fp_survey300/summary.json"
KINDS = ("C_TOMATO", "C_STRAWBERRY", "C_CARROT", "C_WHEAT", "C_MELON",
         "A_COW", "A_SHEEP", "A_GOOSE")
FEATURES = tuple(f"{kind}@{day}" for day in (288, 576) for kind in KINDS) + (
    "land1_day", "land2_day", "land3_day", "hires_observed")


def features(seat):
    out = {}
    for day in (288, 576):
        snap = seat[f"snap{day}"]
        for kind in KINDS:
            out[f"{kind}@{day}"] = snap.get(kind, 0)
    for n in (1, 2, 3):
        days = seat["land_days"]
        out[f"land{n}_day"] = days[n - 1] if len(days) >= n else 30
    out["hires_observed"] = seat["hires_observed"]
    return out


def interval(values, seed=42, times=1000):
    if not values:
        return [None, None]
    rng = random.Random(seed)
    n = len(values)
    draws = sorted(stats.mean(rng.choices(values, k=n)) for _ in range(times))
    return [draws[int(.025 * times)], draws[int(.975 * times)]]


def main():
    episodes = json.load(open(EPISODES, encoding="utf-8"))
    targets = {t["label"]: t for t in json.load(open(TARGETS, encoding="utf-8"))}
    target_seats = collections.defaultdict(list)
    for episode in episodes:
        target_seats[episode["id"]].append((episode["our_seat"], targets[episode["submission_label"]]))
    with zipfile.ZipFile(LB) as archive:
        teams = list(csv.DictReader(archive.read(archive.namelist()[0]).decode("utf-8-sig").splitlines()))
    rank = {team["TeamName"]: int(team["Rank"]) for team in teams}
    snapshots = [json.loads(line) for line in open(SNAP, encoding="utf-8")]
    valid = [row for row in snapshots if "error" not in row]
    unique = {e["id"] for e in episodes}
    available = {r["episode"] for r in valid}
    coverage = {}
    for group in ("top300", "band600_1300"):
        ids = {e["id"] for e in episodes if targets[e["submission_label"]]["group"] == group}
        coverage[group] = {"target_rows": sum(targets[e["submission_label"]]["group"] == group for e in episodes),
                           "unique_ids": len(ids), "snapshot_ids": len(ids & available)}

    paired_all = collections.defaultdict(list)
    paired_direct = collections.defaultdict(list)
    paired_target_direct = collections.defaultdict(list)
    by_team = collections.defaultdict(lambda: collections.defaultdict(list))
    direct_games = []
    target_direct_games = 0
    target_direct_top_wins = 0
    missing_rank_seats = 0
    for row in valid:
        names = row["teams"]
        ranks = [rank.get(name) for name in names]
        missing_rank_seats += sum(r is None for r in ranks)
        ff = [features(row["seats"][s]) for s in (0, 1)]
        rewards = row["rewards"]
        for s, target in target_seats[row["episode"]]:
            group = "top" if target["group"] == "top300" else "band"
            if group in ("top", "band"):
                for key in FEATURES:
                    by_team[(group, target["team_id"])][key].append(ff[s][key])
        if rewards[0] != rewards[1]:
            winner = 0 if rewards[0] > rewards[1] else 1
            for key in FEATURES:
                paired_all[key].append(ff[winner][key] - ff[1 - winner][key])
        target_groups = {target["group"]: s for s, target in target_seats[row["episode"]]}
        if len(target_groups) == 2:
            top = target_groups["top300"]
            band = target_groups["band600_1300"]
            target_direct_games += 1
            target_direct_top_wins += rewards[top] > rewards[band]
            for key in FEATURES:
                paired_target_direct[key].append(ff[top][key] - ff[band][key])
        groups = ["top" if r is not None and r <= 300 else
                  "band" if r is not None and 600 <= r <= 1300 else "other" for r in ranks]
        if sorted(groups) == ["band", "top"]:
            top = groups.index("top")
            direct_games.append((row, ff, top))
            for key in FEATURES:
                paired_direct[key].append(ff[top][key] - ff[1 - top][key])

    team_deltas = {}
    for key in FEATURES:
        top = [stats.mean(v[key]) for (g, _), v in by_team.items() if g == "top"]
        band = [stats.mean(v[key]) for (g, _), v in by_team.items() if g == "band"]
        rng = random.Random(20260929)
        diffs = sorted(stats.mean(rng.choices(top, k=len(top))) -
                       stats.mean(rng.choices(band, k=len(band))) for _ in range(1000))
        delta = stats.mean(top) - stats.mean(band)
        se = stats.pstdev(diffs)
        p = math.erfc(abs(delta / se) / math.sqrt(2)) if se else 1.0
        team_deltas[key] = {"top_mean": stats.mean(top), "band_mean": stats.mean(band),
                            "delta": delta, "ci95": [diffs[25], diffs[975]], "p_normal_approx": p}
    ordered = sorted(FEATURES, key=lambda key: team_deltas[key]["p_normal_approx"])
    accepted = []
    for i, key in enumerate(ordered, 1):
        if team_deltas[key]["p_normal_approx"] <= .1 * i / len(ordered):
            accepted.append(key)
    bh_cutoff = max((team_deltas[key]["p_normal_approx"] for key in accepted), default=-1)
    for key in FEATURES:
        team_deltas[key]["bh_fdr_0_1"] = team_deltas[key]["p_normal_approx"] <= bh_cutoff

    paired = {}
    for key in FEATURES:
        a, d = paired_all[key], paired_direct[key]
        paired[key] = {"winner_minus_loser": stats.mean(a), "winner_ci95": interval(a),
                       "top_minus_band_direct": stats.mean(d), "direct_ci95": interval(d),
                       "target_top_minus_band_direct": stats.mean(paired_target_direct[key]),
                       "target_direct_ci95": interval(paired_target_direct[key])}
    same = {}
    for days in ((288,), (576,), (288, 576)):
        n = win = 0
        for row, ff, top in direct_games:
            keys = [f"{kind}@{day}" for day in days for kind in KINDS]
            if all(ff[0][key] == ff[1][key] for key in keys):
                n += 1
                win += row["rewards"][top] > row["rewards"][1 - top]
        same["+".join(map(str, days))] = {"games": n, "top_wins": win}

    summary = {"input": {"episode_rows": len(episodes), "unique_episodes": len(unique),
                          "raw_snapshot_rows": len(snapshots), "valid_snapshot_rows": len(valid),
                          "missing_rank_seats": missing_rank_seats, "coverage": coverage},
               "samples": {"winner_loser_games": len(paired_all[FEATURES[0]]),
                           "top_vs_band_direct_games": len(direct_games),
                           "target_top_vs_band_direct_games": target_direct_games,
                           "target_top_wins_direct": target_direct_top_wins,
                           "top_wins_direct": sum(row["rewards"][top] > row["rewards"][1 - top]
                                                  for row, _, top in direct_games),
                           "top_teams": sum(g == "top" for g, _ in by_team),
                           "band_teams": sum(g == "band" for g, _ in by_team)},
               "paired": paired, "team": team_deltas, "same_snapshot": same}
    with open(OUT, "w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)
    print(json.dumps(summary["input"], ensure_ascii=False))
    print(json.dumps(summary["samples"], ensure_ascii=False))
    for key in ("C_TOMATO@576", "C_STRAWBERRY@576", "A_GOOSE@576", "land2_day"):
        print(key, json.dumps({"paired": paired[key], "team": team_deltas[key]}, ensure_ascii=False))
    print("same_snapshot", json.dumps(same))


if __name__ == "__main__":
    main()
