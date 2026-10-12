#!/usr/bin/env python3
"""Compare two hosted submissions over a fixed, time-matched episode sample."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.rstrip("Z"))


def select_time_matched(
    episodes_a: list[dict], episodes_b: list[dict], *, after: datetime, as_of: datetime, count: int
) -> tuple[list[dict], list[dict]]:
    def eligible(episode: dict) -> bool:
        created = parse_time(episode["createTime"])
        return episode.get("state") == "COMPLETED" and after <= created <= as_of

    pool_a = sorted((e for e in episodes_a if eligible(e)), key=lambda e: parse_time(e["createTime"]))[-count:]
    pool_b = [e for e in episodes_b if eligible(e)]
    if len(pool_a) < count or len(pool_b) < count:
        raise ValueError(f"insufficient eligible episodes: A={len(pool_a)}, B={len(pool_b)}, requested={count}")

    remaining = {int(e["id"]): e for e in pool_b}
    matched_b: list[dict] = []
    for episode_a in pool_a:
        created_a = parse_time(episode_a["createTime"])
        episode_b = min(
            remaining.values(),
            key=lambda e: (abs((parse_time(e["createTime"]) - created_a).total_seconds()), int(e["id"])),
        )
        matched_b.append(episode_b)
        del remaining[int(episode_b["id"])]
    return pool_a, matched_b


def replay_header(response, *, max_bytes: int = 2_000_000) -> dict:
    data = bytearray()
    try:
        for chunk in response.iter_content(chunk_size=65_536):
            data.extend(chunk)
            marker = data.find(b'"steps":')
            if marker >= 0:
                return json.loads(bytes(data[:marker]) + b'"steps": null}')
            if len(data) > max_bytes:
                raise ValueError("replay header exceeded byte limit")
    finally:
        response.close()
    raise ValueError("replay did not contain a steps field")


def fetch_replay_header(api, episode_id: int) -> dict:
    from kagglesdk.competitions.types.competition_api_service import ApiGetEpisodeReplayRequest

    with api.build_kaggle_client() as kaggle:
        request = ApiGetEpisodeReplayRequest()
        request.episode_id = episode_id
        response = kaggle.competitions.competition_api_client.get_episode_replay(request)
        return replay_header(response)


def episode_result(api, episode: dict, team: str) -> dict:
    header = fetch_replay_header(api, int(episode["id"]))
    teams = header["info"]["TeamNames"]
    if team not in teams:
        raise ValueError(f"team {team!r} absent from episode {episode['id']}: {teams}")
    seat = teams.index(team)
    rewards = header["rewards"]
    opponent_seat = 1 - seat
    if rewards[seat] > rewards[opponent_seat]:
        result = "W"
    elif rewards[seat] < rewards[opponent_seat]:
        result = "L"
    else:
        result = "D"
    return {
        "episode_id": int(episode["id"]),
        "create_time": episode["createTime"],
        "seat": seat,
        "opponent": teams[opponent_seat],
        "reward": rewards[seat],
        "opponent_reward": rewards[opponent_seat],
        "result": result,
    }


def summarize(rows: list[dict]) -> dict:
    wins = sum(row["result"] == "W" for row in rows)
    draws = sum(row["result"] == "D" for row in rows)
    losses = sum(row["result"] == "L" for row in rows)
    return {
        "n": len(rows),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "point_score": (wins + 0.5 * draws) / len(rows),
        "seat_counts": {
            "0": sum(row["seat"] == 0 for row in rows),
            "1": sum(row["seat"] == 1 for row in rows),
        },
        "loss_opponents": sorted(row["opponent"] for row in rows if row["result"] == "L"),
    }


def episode_dicts(api, submission_id: int) -> list[dict]:
    return [episode.to_dict() for episode in api.competition_list_episodes(submission_id)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submission-a", type=int, required=True)
    parser.add_argument("--submission-b", type=int, required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--after", type=parse_time, required=True)
    parser.add_argument("--as-of", type=parse_time, required=True)
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    all_a = episode_dicts(api, args.submission_a)
    all_b = episode_dicts(api, args.submission_b)
    selected_a, selected_b = select_time_matched(
        all_a, all_b, after=args.after, as_of=args.as_of, count=args.count
    )
    rows_a = [episode_result(api, episode, args.team) for episode in selected_a]
    rows_b = [episode_result(api, episode, args.team) for episode in selected_b]
    summary_a = summarize(rows_a)
    summary_b = summarize(rows_b)
    payload = {
        "evidence_level": "HOSTED",
        "selection": {
            "after": args.after.isoformat(),
            "as_of": args.as_of.isoformat(),
            "count_per_submission": args.count,
            "method": "latest A episodes; nearest unique B episode by createTime",
        },
        "submissions": {
            str(args.submission_a): {"summary": summary_a, "episodes": rows_a},
            str(args.submission_b): {"summary": summary_b, "episodes": rows_b},
        },
        "loss_opponent_overlap": sorted(set(summary_a["loss_opponents"]) & set(summary_b["loss_opponents"])),
        "limitations": [
            "The two samples are time-matched but not matched on opponent identity or seed.",
            "Zero loss-opponent overlap does not prove complementary coverage when opponent pools differ.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "summaries": {str(args.submission_a): summary_a, str(args.submission_b): summary_b}, "loss_opponent_overlap": payload["loss_opponent_overlap"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
