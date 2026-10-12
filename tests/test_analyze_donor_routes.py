import unittest
from tools.analyze_donor_routes import composition, context


class DonorRouteTests(unittest.TestCase):
    def test_composition_counts_actual_tiles(self):
        farm = {'tiles': [[None, 'LOCKED', {'kind': 'PLANT', 'crop': 'WHEAT'},
                           {'kind': 'PASTURE', 'animal': 'COW'}, {'kind': 'WEED'}]]}
        self.assertEqual(composition(farm), {'COW': 1, 'WEED': 1, 'WHEAT': 1})

    def test_context_uses_previous_observation(self):
        def state(cash, hands, action):
            farm = {'money': cash, 'hands': hands, 'farmer': [4,4], 'tiles': [[None]]}
            obs = {'day': 0, 'hour': 1, 'farms': [farm, farm],
                   'town': {'unlocked_shops': []},
                   'market': {'prices': {'WHEAT': 25}, 'inventory': {'WHEAT': 10}},
                   'private': {'shed': {'WHEAT': 0}, 'seeds': {}}}
            return {'observation': obs, 'action': action}
        replay = {'steps': [[state(7, [], {'farmer':['PASS']}), state(7, [], {'market':[]})],
                            [state(0, [[4,5]], {'market':[['HIRE']]}), state(0, [], {'market':[['SELL','WHEAT',1]]})]]}
        c = context(replay, 0, 1)
        self.assertEqual((c['cash'], c['hands']), (7,0))
        self.assertEqual((c['post_cash'], c['post_hands']), (0,1))
        self.assertEqual(c['opponent_previous_action_forensics_only'], {'market':[]})
        self.assertEqual(c['action'], {'market':[['HIRE']]})


if __name__ == '__main__':
    unittest.main()
