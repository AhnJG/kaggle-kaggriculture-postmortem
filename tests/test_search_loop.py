import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('search_loop',Path(__file__).resolve().parents[1]/'tools/search_loop.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DurabilityTests(unittest.TestCase):
    def test_atomic_replace(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'state.json';m.atomic(p,{'a':1});m.atomic(p,{'a':2})
            self.assertEqual(json.loads(p.read_text()),{'a':2})
            self.assertEqual(len(list(Path(d).iterdir())),1)
    def test_torn_append_recovered(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'games.jsonl';m.append_game(p,{'key':'a','result':1})
            with p.open('ab') as f:f.write(b'{"key":"b"')
            self.assertEqual(list(m.read_journal(p)),['a'])
            m.append_game(p,{'key':'b','result':2})
            self.assertEqual(list(m.read_journal(p)),['a','b'])
            self.assertEqual(len(list(Path(d).glob('*.torn-*'))),1)
    def test_bad_committed_line_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'games.jsonl';p.write_text('broken\n')
            with self.assertRaises(json.JSONDecodeError):m.read_journal(p)
    def test_duplicate_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'games.jsonl';m.append_game(p,{'key':'a'});m.append_game(p,{'key':'a'})
            with self.assertRaises(RuntimeError):m.read_journal(p)
    def test_holdout_leak_blocks(self):
        job={'variant':'x','seed':9000,'seat':0,'path':'p','sha256':'x','opponent':'q','opponent_sha256':'y'}
        from unittest.mock import patch
        with patch.object(m,'sha',side_effect=['x','y']):
            with self.assertRaisesRegex(RuntimeError,'HOLDOUT_SEED_LEAK'):
                m.verify_manifest({'workers':6,'sha256':{'p':'x','q':'y'},'jobs':[job]})

class GateTests(unittest.TestCase):
    def test_same_variant_different_seats_do_not_collide(self):
        j={'variant':'a','seed':1,'seat':0,'opponent_sha256':'op'}
        self.assertNotEqual(m.job_key(j),m.job_key(dict(j,seat=1)))
    def test_candidate_error_is_invalid_even_when_done(self):
        r={'steps':720,'statuses':['DONE','DONE'],'exceptions':[[],[]],'caught_errors':[{'counter':'layer.errors','value':1}]}
        self.assertFalse(m.valid(r))
    def test_resume_does_not_use_stale_state(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            j={'variant':'a','seed':1,'seat':0,'opponent_sha256':'op'}
            p=out/'manifest.json';p.write_text(json.dumps({'id':'test','workers':6,'jobs':[j]}))
            row={'key':m.job_key(j),'job':j,'manifest_sha256':m.sha(p)}
            m.append_game(out/'games.jsonl',row)
            m.atomic(out/'state.json',{'completed':0,'status':'RUNNING'})
            with patch.object(m,'OUT',out),patch.object(m,'verify_manifest'),patch.object(m,'execute',side_effect=AssertionError('must not replay')):
                m.run(p)
            self.assertEqual(json.loads((out/'state.json').read_text())['completed'],1)
            self.assertEqual(len(m.read_journal(out/'games.jsonl')),1)
    def test_manifest_change_blocks_reuse(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);j={'variant':'a','seed':1,'seat':0,'opponent_sha256':'op'}
            p=out/'manifest.json';p.write_text(json.dumps({'id':'test','workers':6,'jobs':[j]}))
            m.append_game(out/'games.jsonl',{'key':m.job_key(j),'job':j,'manifest_sha256':'wrong'})
            with patch.object(m,'OUT',out),patch.object(m,'verify_manifest'):
                with self.assertRaisesRegex(RuntimeError,'RESUME_IDENTITY_MISMATCH'):m.run(p)

if __name__=='__main__':unittest.main()
