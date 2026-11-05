"""Publish source-labelled research; never converts archived or synthetic data into measurements."""
import datetime,hashlib,json,os,re,urllib.request,urllib.parse
from pathlib import Path
BASE='https://prometheus-bungie-auth.davidwelden1.workers.dev'
def build(root):
 # Internal datasets stay in the research repository. Only edited player guides
 # may enter the player feed; never fall back to raw JSON or code-test reports.
 p=root/'data/player_discoveries.json';raw=p.read_bytes();data=json.loads(raw);records=[];ids=set()
 for v in data['records']:
  player=v.get('player',{})
  if player.get('version')!=1 or not all(isinstance(player.get(k),str) and len(player[k])>=20 for k in ('takeaway','explanation','watch_out','status')):
   raise ValueError('Player guide needs a written explanation, practical advice and honest status')
  if not all(isinstance(player.get(k),str) and player[k].strip() for k in ('category','activity','guardian')) or not isinstance(v.get('title'),str) or not v['title'].strip():
   raise ValueError('Player guide needs readable title, category, activity and guardian labels')
  if not isinstance(player.get('steps'),list) or not 1<=len(player['steps'])<=8 or not all(isinstance(x,str) and len(x)>=12 for x in player['steps']):
   raise ValueError('Player guide needs readable steps')
  if v['id'] in ids or v.get('evidence') not in ('official_historical','research') or v.get('runtime_verified') is not False:
   raise ValueError('Duplicate or invalid player guide')
  source=v.get('source_url','');parsed=urllib.parse.urlsplit(source)
  if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() for c in source):
   raise ValueError('Player guide needs a valid HTTPS source URL')
  for date_field in ('reviewed_at','source_published_at'):
   value=v.get(date_field)
   if date_field=='source_published_at' and value is None:continue
   if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
    raise ValueError('Player guide needs ISO source and review dates')
   try:datetime.date.fromisoformat(value)
   except ValueError:raise ValueError('Player guide has invalid calendar date')
  if v.get('source_published_at') and v['reviewed_at']<v['source_published_at']:
   raise ValueError('Review date predates source publication')
  ids.add(v['id']);text=player['takeaway']+'\n\nWhy it matters\n'+player['explanation']+'\n\nHow to use it\n'+'\n'.join(str(i+1)+'. '+x for i,x in enumerate(player['steps']))+'\n\nWhat to watch for\n'+player['watch_out']+'\n\nSource & status\n'+player['status']
  records.append({**v,'summary':player['takeaway'],'text':text,'provenance':{'dataset':p.name,'sha256':hashlib.sha256(raw).hexdigest(),'commit':os.environ.get('GITHUB_SHA','local-import')}})
 return {'schema_version':1,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'revision':os.environ.get('GITHUB_SHA','initial-import'),'records':records}

def main():
 feed=build(Path('.'));Path('research-feed.json').write_text(json.dumps(feed,ensure_ascii=False,separators=(',',':')))
 if '--local' in __import__('sys').argv:return
 q=urllib.parse.urlencode({'audience':'vaeltrion-research-publish'});url=os.environ['ACTIONS_ID_TOKEN_REQUEST_URL']+'&'+q
 req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})
 with urllib.request.urlopen(req,timeout=20) as r:token=json.load(r)['value']
 req=urllib.request.Request(BASE+'/app/research/publish',data=json.dumps(feed).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json','User-Agent':'VAELTRION-Research-Publisher/1.0'},method='POST')
 with urllib.request.urlopen(req,timeout=45) as r:result=json.load(r)
 assert result.get('status')=='published' and result.get('records')==len(feed['records']);print('Research feed published:',len(feed['records']),'records; revision',feed['revision'])
if __name__=='__main__':main()
