import json, sys
def parse_noop(replay_path):
    with open(replay_path) as f: r = json.load(f)
    seat = r['info']['TeamNames'].index('Sian')
    noops = 0
    for i in range(1, len(r['steps'])):
        pre = r['steps'][i-1][0]['observation']
        post = r['steps'][i][0]['observation']
        action = r['steps'][i][seat].get('action', {})
        hand_actions = action.get('hands', [])
        
        pre_farm = pre['farms'][seat]
        post_farm = post['farms'][seat]
        pre_hands = pre_farm.get('hands', [])
        post_hands = post_farm.get('hands', [])
        
        for h_idx, h_act in enumerate(hand_actions):
            if not h_act or h_act[0] == 'PASS': continue
            if h_idx < len(pre_hands) and h_idx < len(post_hands):
                if pre_hands[h_idx] == post_hands[h_idx]:
                    # check if seed blocked plant
                    is_seed_blocked = False
                    if h_act[0] == 'PLANT':
                        seed_type = h_act[1]
                        if pre['private']['inventories'][seat].get(seed_type, 0) == 0:
                            is_seed_blocked = True
                    if not is_seed_blocked:
                        noops += 1
    return noops
if __name__ == "__main__":
    print(parse_noop(sys.argv[1]))
