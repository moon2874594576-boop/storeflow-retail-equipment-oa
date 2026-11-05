"""Acceptance against a running DEMO server; creates test loan records.

Run only on fictional demonstration data, with the default demonstration users.
"""
import argparse
import concurrent.futures
import datetime
import json
import urllib.request
import urllib.error

p=argparse.ArgumentParser(); p.add_argument('--url',default='http://127.0.0.1:8765'); args=p.parse_args()
BASE=args.url+'/api/'
checks=[]
def check(name, ok):
    if not ok: raise AssertionError(name)
    checks.append(name)
def call(path, token=None, data=None, method=None):
    headers={'Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(BASE+path, data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            raw=r.read(); return r.status,json.loads(raw) if 'json' in r.headers.get('Content-Type','') else raw.decode('utf-8-sig')
    except urllib.error.HTTPError as e:
        raw=e.read()
        try: body=json.loads(raw)
        except ValueError: body=raw.decode(errors='replace')
        return e.code,body
tokens={}
for user in ['employee_a','employee_c','manager_a','manager_b','custodian','admin']:
    status,result=call('auth/login/',data={'username':user,'password':'Demo2026!'})
    check('real login '+user,status==200 and 'access' in result)
    tokens[user]=result['access']
check('anonymous denied',call('requests/')[0] in [401,403])
cat=call('categories/',tokens['employee_a'])[1][0]['id']
due=(datetime.date.today()+datetime.timedelta(days=7)).isoformat()
def create():
    st,d=call('requests/',tokens['employee_a'],{'category_id':cat,'purpose':'独立HTTP验收：门店盘点临时设备','due_date':due})
    check('create real draft',st==201)
    rid=d['id']
    check('submit',call(f'requests/{rid}/submit/',tokens['employee_a'],{})[0]==200)
    return rid
rid=create()
check('cross store detail denied',call(f'requests/{rid}/',tokens['employee_c'])[0] in [403,404])
check('wrong manager denied',call(f'requests/{rid}/approve/',tokens['manager_b'],{})[0] in [403,404])
check('employee cannot approve',call(f'requests/{rid}/approve/',tokens['employee_a'],{})[0] in [403,404])
check('status patch blocked',call(f'requests/{rid}/',tokens['employee_a'],{'status':'returned'},'PATCH')[0]>=400)
check('approve',call(f'requests/{rid}/approve/',tokens['manager_a'],{})[0]==200)
assets=call(f'assets/?status=available&category_id={cat}',tokens['custodian'])[1]['results']
asset=next(a for a in assets if a['status']=='available' and a['category_id']==cat)
check('issue',call(f'requests/{rid}/issue/',tokens['custodian'],{'asset_id':asset['id']})[0]==200)
check('double issue conflict',call(f'requests/{rid}/issue/',tokens['custodian'],{'asset_id':asset['id']})[0]==409)
check('receive',call(f'requests/{rid}/receive/',tokens['employee_a'],{})[0]==200)
check('return',call(f'requests/{rid}/return/',tokens['employee_a'],{})[0]==200)
check('damaged inspection requires note',call(f'requests/{rid}/inspect/',tokens['custodian'],{'condition':'damaged'})[0]==400)
check('damaged inspection',call(f'requests/{rid}/inspect/',tokens['custodian'],{'condition':'damaged','reason':'按键损坏，记录并转维修'})[0]==200)
detail=call(f'requests/{rid}/',tokens['employee_a'])[1]
check('real history and closure',detail['status']=='returned' and len(detail['events'])>=7)
check('damaged asset quarantined',call(f"assets/{asset['id']}/",tokens['custodian'])[1]['status']=='maintenance')
check('repair',call(f"assets/{asset['id']}/repair/",tokens['custodian'],{'reason':'更换按键并完成测试'})[0]==200)
ids=[create(),create()]
for item in ids: check('approve race participant',call(f'requests/{item}/approve/',tokens['manager_a'],{})[0]==200)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    race=list(pool.map(lambda item:call(f'requests/{item}/issue/',tokens['custodian'],{'asset_id':asset['id']})[0],ids))
check('two simultaneous issuers one winner',sorted(race)==[200,409])
for item in ids:
    d=call(f'requests/{item}/',tokens['employee_a'])[1]
    if d['status']=='handover': check('undo handover',call(f'requests/{item}/undo_issue/',tokens['custodian'],{'reason':'独立验收后回收设备'})[0]==200)
    check('withdraw race request',call(f'requests/{item}/withdraw/',tokens['employee_a'],{})[0]==200)
st,export=call('requests/export/',tokens['employee_c'])
check('CSV scope excludes other store',st==200 and detail['number'] not in export)
check('accounts admin only',call('accounts/',tokens['employee_a'])[0]==403)
check('dashboard live',call('dashboard/',tokens['manager_a'])[0]==200)
print(json.dumps({'passed':len(checks),'checks':checks,'url':args.url,'request_number':detail['number']},ensure_ascii=False,indent=2))
