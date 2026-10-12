from datetime import datetime

from tools.compare_hosted_episodes import replay_header, select_time_matched, summarize


class FakeResponse:
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False

    def iter_content(self, chunk_size):
        del chunk_size
        yield from self.chunks

    def close(self):
        self.closed = True


def test_replay_header_stops_before_steps():
    response = FakeResponse(
        [b'{"info":{"TeamNames":["Sian","opp"]},', b'"rewards":[2,1],"steps":[[1]]}']
    )
    assert replay_header(response) == {
        "info": {"TeamNames": ["Sian", "opp"]},
        "rewards": [2, 1],
        "steps": None,
    }
    assert response.closed


def test_select_time_matched_uses_latest_a_and_unique_nearest_b():
    def episode(episode_id, minute):
        return {"id": episode_id, "state": "COMPLETED", "createTime": f"2026-09-12T01:{minute:02d}:00"}

    selected_a, selected_b = select_time_matched(
        [episode(1, 1), episode(2, 10), episode(3, 20)],
        [episode(11, 9), episode(12, 19), episode(13, 21)],
        after=datetime.fromisoformat("2026-09-12T01:00:00"),
        as_of=datetime.fromisoformat("2026-09-12T02:00:00"),
        count=2,
    )
    assert [row["id"] for row in selected_a] == [2, 3]
    assert [row["id"] for row in selected_b] == [11, 12]


def test_summarize_counts_draws_as_half_point():
    rows = [
        {"result": "W", "seat": 0, "opponent": "a"},
        {"result": "D", "seat": 1, "opponent": "b"},
        {"result": "L", "seat": 1, "opponent": "c"},
    ]
    assert summarize(rows) == {
        "n": 3,
        "wins": 1,
        "draws": 1,
        "losses": 1,
        "point_score": 0.5,
        "seat_counts": {"0": 1, "1": 2},
        "loss_opponents": ["c"],
    }
