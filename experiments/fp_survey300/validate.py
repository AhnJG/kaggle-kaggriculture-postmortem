"""Recompute survey coverage and independent replay-feature agreement."""
import collections
import json

EPISODES = "analysis/survey300_20260929/episodes_all.json"
TARGETS = "analysis/survey300_20260929/targets.json"
SNAPS = "experiments/fp_survey300/snapshots.jsonl"
FEAT = "analysis/survey300_20260929/feat300.jsonl"


def main():
    episodes = json.load(open(EPISODES, encoding="utf-8"))
    targets = {x["label"]: x for x in json.load(open(TARGETS, encoding="utf-8"))}
    metadata = collections.defaultdict(list)
    for row in episodes:
        metadata[row["id"]].append(row)
    snapshots = {row["episode"]: row for row in map(json.loads, open(SNAPS, encoding="utf-8"))}
    features = {row["episode"]: row for row in map(json.loads, open(FEAT, encoding="utf-8"))}
    assert len(snapshots) == 2572
    assert not any("error" in row for row in snapshots.values())
    assert all(row.get("parity") is True for row in features.values())
    assert features.keys() <= snapshots.keys()

    metadata_reward_mismatch = 0
    for episode, row in snapshots.items():
        for metarow in metadata[episode]:
            seat = metarow["our_seat"]
            metadata_reward_mismatch += row["rewards"][seat] != metarow["our_reward"]
    snapshot_mismatch = reward_mismatch = 0
    for episode, row in features.items():
        other = snapshots[episode]
        reward_mismatch += row["rewards"] != other["rewards"]
        for seat in (0, 1):
            for turn in (288, 576):
                snapshot_mismatch += row["seat"][str(seat)][f"snap{turn}"] != other["seats"][seat][f"snap{turn}"]
    missing = collections.Counter()
    available = collections.Counter()
    for episode, rows in metadata.items():
        groups = {targets[row["submission_label"]]["group"] for row in rows}
        for group in groups:
            (available if episode in snapshots else missing)[group] += 1
    print(json.dumps({"episode_rows": len(episodes), "unique_episodes": len(metadata),
                      "snapshots": len(snapshots), "flow_prefix": len(features),
                      "metadata_reward_mismatch": metadata_reward_mismatch,
                      "flow_reward_mismatch": reward_mismatch,
                      "flow_snapshot_mismatch": snapshot_mismatch,
                      "available_target_unique_by_group": available,
                      "missing_target_unique_by_group": missing}, ensure_ascii=False))
    assert metadata_reward_mismatch == reward_mismatch == snapshot_mismatch == 0


if __name__ == "__main__":
    main()
