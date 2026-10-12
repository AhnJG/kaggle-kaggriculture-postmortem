"""Buy ten WHEAT, then use a deliberately oversized sentinel SELL request."""


def agent(observation, configuration=None):
    step = int(observation["step"])
    market = [["BUY_PRODUCT", "WHEAT", 10]] if step == 0 else (
        [["SELL", "WHEAT", 1000]] if step == 1 else [])
    return {"farmer": ["PASS"], "hands": [], "market": market}
