"""의도적으로 조용한 no-op을 발생시키는 gate fixture."""


def agent(obs, config=None):
    return {"farmer": ["PASS"], "hands": [],
            "market": [["SELL", "WHEAT", 1000] for _ in range(11)]}
