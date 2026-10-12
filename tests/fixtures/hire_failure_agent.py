"""Exhaust the exponentially increasing HIRE budget across two turns."""


def agent(observation, configuration=None):
    market = ([["HIRE"] for _ in range(10)]
              if int(observation["step"]) in (0, 1) else [])
    return {"farmer": ["PASS"], "hands": [], "market": market}
