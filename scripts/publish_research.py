"""Publish source-labelled research; never converts archived or synthetic data into measurements."""
import datetime,hashlib,json,os,re,urllib.request,urllib.parse
from pathlib import Path
BASE='https://prometheus-bungie-auth.davidwelden1.workers.dev'
def build(root):
 records=[]
 for p in sorted((root/'data').glob('*.json')):
  data=json.loads(p.read_text());raw=p.read_bytes();entries=data.get('records',data.get('findings',data.get('leads',[data])))
  if isinstance(entries,dict):entries=[{'id':k,**v} if isinstance(v,dict) else {'id':k,'value':v} for k,v in entries.items()]
  if not isinstance(entries,list):entries=[data]
  for n,v in enumerate(entries):
   if not isinstance(v,dict):continue
   source=v.get('source_url') or v.get('source') or data.get('source_url') or 'https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/blob/main/'+p.as_posix()
   if not isinstance(source,str) or not source.startswith('https://'):source='https://github.com/davidwelden1-sketch/destiny2-manifest-sync1/blob/main/'+p.as_posix()
   title=v.get('title') or v.get('weapon') or v.get('name') or str(v.get('id') or p.stem).split(':')[-1].replace('_',' ').replace('-',' ').title()
   terms=[str(v[k]) for k in ('weapon','name','exotic','perk') if isinstance(v.get(k),str) and len(v[k])>=6]
   grade=str(v.get('confidence_grade',v.get('confidence',data.get('confidence_grade','research'))))
   evidence='software' if any(s in grade.lower() for s in ['synthetic','software']) else 'official_historical' if 'official' in grade.lower() or 'bungie_known_issue'==v.get('status') else 'research'
   if v.get('evidence') in ('archive','official_historical','research','software'):evidence=v['evidence']
   date=v.get('reviewed_at') or v.get('source_checked_on_utc') or data.get('reviewed_at_utc') or data.get('source_checked_at') or data.get('indexed_at_utc') or data.get('generated_at_utc') or data.get('reviewed_on') or '2026-10-29'
   summary=v.get('mechanism') or v.get('condition') or v.get('limits') or v.get('summary') or data.get('notes') or data.get('policy') or 'Source-indexed research. Open details for conditions, provenance and unresolved measurements.'
   records.append({'id':str(v.get('id') or p.stem+':'+str(n)),'title':str(title)[:180],'summary':str(summary)[:1200],'text':json.dumps(v,ensure_ascii=False,indent=2),'source_url':source,'evidence':evidence,'reviewed_at':str(date),'patch_status':str(v.get('bungie_status') or v.get('status') or 'Historical or research evidence; current gameplay not retested.'),'activities':v.get('activities',['pve','pvp']),'runtime_verified':False,'match_terms':terms,'provenance':{'dataset':p.name,'sha256':hashlib.sha256(raw).hexdigest(),'commit':os.environ.get('GITHUB_SHA','local-import')}})
 return {'schema_version':1,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':os.environ.get('GITHUB_SHA','initial-import'),'records':records}
def main():
 feed=build(Path('.'));Path('research-feed.json').write_text(json.dumps(feed,ensure_ascii=False,separators=(',',':')))
 if '--local' in __import__('sys').argv:return
 q=urllib.parse.urlencode({'audience':'vaeltrion-research-publish'});url=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']+'&'+q
 req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})
 with urllib.request.urlopen(req,timeout=20) as r:token=json.load(r)['value']
 req=urllib.request.Request(BASE+'/app/research/publish',data=json.dumps(feed).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=45) as r:result=json.load(r)
 assert result.get('status')=='published' and result.get('records')==len(feed['records']);print('Research feed published:',len(feed['records']),'records; revision',feed['revision'])
if __name__=='__main__':main()
