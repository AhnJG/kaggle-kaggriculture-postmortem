import random
SH = sorted(["BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET"])
def pred(seed, day, ncalls=0):
    rng = random.Random((seed * 1_000_003) ^ day)
    for _ in range(ncalls): rng.random()
    return rng.choice(SH)
def first2(seed, n2=0, n5=0):
    return (pred(seed, 2, n2), pred(seed, 5, n5))
