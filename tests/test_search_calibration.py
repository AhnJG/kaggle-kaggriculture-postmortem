import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import search_calibration as c

class CalibrationTests(unittest.TestCase):
    def test_fixed_weights_total_one(self):
        pool=[{'path':c.NEW,'sha256':'n'},{'path':c.DP,'sha256':'d'},{'path':'x','sha256':'x'},{'path':'y','sha256':'y'}]
        with patch.object(c,'sha',side_effect=['n','d']):w=c.weights(pool)
        self.assertAlmostEqual(w['a'][c.NEW],.30);self.assertAlmostEqual(w['b'][c.NEW],.50)
        self.assertEqual(w['a']['x'],.275)
        for weights in w.values():self.assertAlmostEqual(sum(weights.values()),1)
    def test_no_rest_cannot_silently_renormalize(self):
        pool=[{'path':c.NEW,'sha256':'n'},{'path':c.DP,'sha256':'d'}]
        with patch.object(c,'sha',side_effect=['n','d']):
            with self.assertRaisesRegex(RuntimeError,'NO_REST_POOL'):c.weights(pool)
    def test_tape_indexes_next_step_action_and_preserves_inputs(self):
        # Exercise the actual emitted opponent, independently of the engine.
        import copy
        actions=[{'market':[['SELL','WHEAT',i]],'farmer':['PASS'],'hands':[]} for i in range(719)]
        text='import copy\n_TAPE = '+repr(actions)+'\ndef agent(obs, configuration=None):\n    return copy.deepcopy(_TAPE[int(obs["step"])])\n'
        env={};exec(text,env)
        got=env['agent']({'step':0});got['market'][0][2]=999
        self.assertEqual(env['agent']({'step':0})['market'][0][2],0)
        self.assertEqual(env['agent']({'step':718})['market'][0][2],718)
    def test_tape_seed_mismatch_blocks_before_execution(self):
        raw={'steps':[{}]*720,'info':{'seed':123}}
        with patch.object(c,'raw_read',return_value=raw):
            with self.assertRaisesRegex(RuntimeError,'TAPE_SEED_IDENTITY'):c.tape_file('x',0,456)
    def test_policy_is_immutable(self):
        with tempfile.TemporaryDirectory() as d,patch.object(c,'OUT',Path(d)):
            c.preregister();p=Path(d)/'calibration-policy.json';v=json.loads(p.read_text());v['calibration_required']=3;p.write_text(json.dumps(v))
            with self.assertRaisesRegex(RuntimeError,'POLICY_CHANGED'):c.preregister()

if __name__=='__main__':unittest.main()
