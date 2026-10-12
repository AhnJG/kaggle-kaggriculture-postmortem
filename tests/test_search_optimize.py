import hashlib,json
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import search_optimize as s

class SearchTests(unittest.TestCase):
    def test_wrapper_preserves_parent_bytes_and_removes_one_layer(self):
        raw=b'RATE = 10\r\ndef first(obs, configuration=None): return RATE\r\n_MID_PARENT = first\r\ndef middle(obs, configuration=None): return _MID_PARENT(obs, configuration)+100\r\n_TOP_PARENT = middle\r\ndef last(obs, configuration=None): return _TOP_PARENT(obs, configuration)+1\r\n'
        changes=[x for x in s.mutation_specs(raw) if x['kind']=='layer']
        self.assertEqual(len(changes),1)
        with tempfile.TemporaryDirectory() as d,patch.object(s,'ROOT',Path(d)),patch.object(s,'OUT',Path(d)/'out'),patch.object(s.subprocess,'check_output',return_value='test-git-sha'):
            Path(d,'parent.py').write_bytes(raw)
            v=s.build_variant('parent.py',changes,'test')
            data=Path(d,v['path']).read_bytes();self.assertTrue(data.startswith(raw))
            env={};exec(data,env);self.assertEqual(env['search_entry']({},None),11)
    def test_common_schedule_is_deterministic_paired_and_disjoint(self):
        metric={'weights':{'a':.3,'b':.7}}
        first=s.schedule(metric,'pin',3000);second=s.schedule(metric,'pin',4000)
        self.assertEqual(first,s.schedule(metric,'pin',3000));self.assertEqual(len(first),1000)
        self.assertTrue({x[0] for x in first}.isdisjoint(x[0] for x in second))
        for a,b in zip(first[::2],first[1::2]):self.assertEqual((a[0],a[2]),(b[0],b[2]));self.assertEqual((a[1],b[1]),(0,1))
    def test_engine_constraints_not_mutated(self):
        specs=s.mutation_specs('MAX_ORDERS=10\nTURNS_PER_DAY=24\nGOOSE_COUNT=2\nRATE=1.0\n')
        self.assertEqual({x['target'] for x in specs},{'RATE'})
    def test_holdout_not_due_is_blocked_before_writes(self):
        with patch.object(s.time,'time',return_value=s.CP['CP1'][0]-1):
            with self.assertRaisesRegex(RuntimeError,'CHECKPOINT_NOT_DUE'):s.holdout_batch('CP1',{},'x','x',[])
    def test_holdout_resume_skips_completed_and_rejects_new_candidate(self):
        with tempfile.TemporaryDirectory() as d,patch.object(s,'ROOT',Path(d)),patch.object(s,'OUT',Path(d)/'experiments/search_20260925'),patch.object(s.time,'time',return_value=s.CP['CP1'][0]+1):
            root=Path(d);out=s.OUT;out.mkdir(parents=True)
            for name in ['parent.py','candidate.py','opponent.py','tools/search_loop.py','tools/search_optimize.py','tools/dp_counterfactual.py','tools/dp_loss_cause.py','tools/reproduce_replay.py','experiments/search_20260925/metric.json']:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(name)
            pin=s.sha(out/'metric.json');cand={'sha256':s.sha(root/'candidate.py')}
            j=dict(variant='CP1-candidate',path='candidate.py',sha256=cand['sha256'],opponent='opponent.py',opponent_sha256=s.sha(root/'opponent.py'),seed=9000,seat=0)
            def execute(job):return {'key':s.job_key(job),'job':job,'result':{'worker_peak_rss_bytes':1}}
            with patch.object(s,'execute',side_effect=execute) as e:
                a=s.holdout_batch('CP1',cand,'parent.py',pin,[j]);b=s.holdout_batch('CP1',cand,'parent.py',pin,[j]);self.assertEqual(e.call_count,1);self.assertEqual(a,b)
                with self.assertRaisesRegex(RuntimeError,'DIFFERENT_CANDIDATE'):s.holdout_batch('CP1',{'sha256':'different'},'parent.py',pin,[j])

if __name__=='__main__':unittest.main()
