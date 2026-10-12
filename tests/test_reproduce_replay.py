import copy
import unittest

from tools.reproduce_replay import first_difference, projection, reproduce, tape_agent


class ReplayVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from kaggle_environments import make
        env = make('kaggriculture', configuration={'seed': 73421, 'episodeSteps': 720})
        def active(obs):
            return {'farmer': ['DIG' if obs['step'] % 2 == 0 else 'PASS'], 'hands': [], 'market': []}
        env.run([active, active])
        cls.replay = env.toJSON()
        cls.replay['module_version'] = '1.32.7'
        cls.replay['statuses'] = [s.status for s in env.steps[-1]]
        cls.replay['rewards'] = [s.reward for s in env.steps[-1]]

    def test_generated_roundtrip(self):
        result = reproduce(self.replay)
        self.assertEqual(result['verdict'], 'PASS')
        self.assertEqual(result['action_matches'], 1438)

    def test_action_alignment_and_copy(self):
        agent = tape_agent(self.replay, 0)
        action = agent({'step': 0})
        self.assertEqual(action, self.replay['steps'][1][0]['action'])
        self.assertEqual(agent({'step': 1})['farmer'], ['PASS'])
        action['farmer'][0] = 'NORTH'
        self.assertEqual(self.replay['steps'][1][0]['action']['farmer'], ['DIG'])

    def test_corrupted_state_fails(self):
        replay = copy.deepcopy(self.replay)
        replay['steps'][20][0]['observation']['farms'][0]['money'] += 1
        result = reproduce(replay)
        self.assertEqual(result['verdict'], 'FAILURE')
        self.assertEqual(result['first_differences'][0]['step'], 20)

    def test_missing_seed_rejected(self):
        replay = copy.deepcopy(self.replay)
        replay['info'].pop('seed', None)
        with self.assertRaisesRegex(ValueError, 'seed missing'):
            reproduce(replay)

    def test_projection_excludes_only_non_game_fields(self):
        state = self.replay['steps'][1][0]
        changed = copy.deepcopy(state)
        changed['observation']['remainingOverageTime'] = -10
        self.assertEqual(projection(state), projection(changed))
        changed['observation']['private']['shed']['WHEAT'] += 1
        self.assertIsNotNone(first_difference(projection(state), projection(changed)))


if __name__ == '__main__':
    unittest.main()
