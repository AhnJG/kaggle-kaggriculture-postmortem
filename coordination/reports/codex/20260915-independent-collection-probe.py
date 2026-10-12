import ast, os, json, shutil, tempfile
from pathlib import Path
from types import SimpleNamespace as N
from contextlib import redirect_stdout
import io
root=Path(__file__).resolve().parents[3]
tree=ast.parse((root/'scripts/fetch_kaggle_updates.py').read_text())
ns=dict(os=os,json=json,shutil=shutil,tempfile=tempfile)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'collector_functions','exec'),ns)
class API:
 def competition_list_topics(self,*a,**kw):
  return N(topics=[N(id=i,title=f'T{i}',votes=i,last_comment_post_date=i,author_name='Writer') for i in range(1,7)],total_count=7)
 def competition_list_topic_messages(self,*a,**kw):
  return N(messages=[N(id=1,content='ROOT',author_name='Staff',post_date='2026-09-15',replies=[N(id=2,content='NESTED')])])
 def kernels_list(self,**kw):return [N(ref='a/k',title='K',total_votes=23,current_version_number=2)]
 def kernels_pull(self,ref,path):Path(path,'k.ipynb').write_text('{"cells": []}')
with tempfile.TemporaryDirectory() as td:
 os.chdir(td)
 with redirect_stdout(io.StringIO()):m=ns['fetch_discussions'](API(),'x'); c=ns['fetch_codes'](API(),'x')
 assert [x['id'] for x in m['top_voted']]==[1,2,3,4,5]
 assert m['top_voted']==m['recent'] and all(x['score']==0 for x in m['top_voted'])
 assert c['top_voted'][0]['score']==0
 body=Path(m['top_voted'][0]['path']).read_text()
 assert 'NESTED' not in body and 'Staff' not in body and '2026-09-15' not in body
 print('PASS observed_wrong_fields_sort_and_nested_reply_loss')
 class Broken(API):
  def competition_list_topic_messages(self,*a,**kw):raise RuntimeError('temporary outage')
 with redirect_stdout(io.StringIO()):ns['fetch_discussions'](Broken(),'x')
 assert 'ROOT' not in Path(m['top_voted'][0]['path']).read_text()
 print('PASS observed_transient_message_failure_deletes_last_good_body')
 class Outage:
  def authenticate(self):pass
  def competition_list_topics(self,*a,**kw):raise RuntimeError('outage')
  def kernels_list(self,*a,**kw):raise RuntimeError('outage')
 Path('docs/latest_metadata.json').write_text('{"last_good": true}')
 ns['KaggleApi']=Outage
 output=io.StringIO()
 with redirect_stdout(output):ns['main']()
 assert json.loads(Path('docs/latest_metadata.json').read_text())=={'discussions':{'top_voted':[],'recent':[]},'codes':{'top_voted':[],'recent':[]}}
 assert 'Updates fetched' in output.getvalue()
 print('PASS observed_total_api_outage_replaces_manifest_and_reports_success')
 class Changing(API):
  n=0
  def kernels_pull(self,ref,path):
   self.n+=1;Path(path,'k.ipynb').write_text(str(self.n))
 a=Changing()
 with redirect_stdout(io.StringIO()):c=ns['fetch_codes'](a,'x')
 assert a.n==2 and Path(c['top_voted'][0]['path']).read_text()=='2'
 print('PASS observed_duplicate_pull_same_ref_overwrites_snapshot')
 class Many(API):
  def kernels_pull(self,ref,path):
   Path(path,'k.ipynb').write_text('{}');Path(path,'helper.py').write_text('helper');Path(path,'data.json').write_text('{}')
 with redirect_stdout(io.StringIO()):c=ns['fetch_codes'](Many(),'x')
 assert len(list(Path('docs/code').iterdir()))<=2
 assert not Path('docs/code/data.json').exists() and not Path('docs/code/helper.py').exists()
 print('PASS observed_single_file_filter_discards_extra_pull_files')
