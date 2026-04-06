import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE
import json

d = json.load(open('d:/MyClaw/ci-scoring/backend/representative_works.json','r',encoding='utf-8'))

print("=== 望海潮 ===")
for cid in [36, 44]:
    c = [x for x in CIPAI_DATABASE if x.get('id')==cid][0]
    print(f'ID {cid}: name={c.get("name")} | total_chars={c.get("total_chars")} | aliases={c.get("aliases",[])} | 句数={len(c.get("sentences",[]))}')
    for i,s in enumerate(c.get('sentences',[])):
        print(f'  句{i+1}: chars={len(s.get("tone",""))} | tone={s.get("tone","")} | text={s.get("text","")}')
    v = d.get(str(cid), {})
    print(f'  代表作: main={len(v.get("main",[]))}, variant={len(v.get("variant",[]))}')
    for w in v.get('main',[]):
        print(f'    - {w.get("title","?")} | {w.get("author","?")} | {str(w.get("text",""))[:40]}')
    print()

print("=== 谒金门 ===")
for cid in [50, 64]:
    c = [x for x in CIPAI_DATABASE if x.get('id')==cid][0]
    print(f'ID {cid}: name={c.get("name")} | total_chars={c.get("total_chars")} | aliases={c.get("aliases",[])} | 句数={len(c.get("sentences",[]))}')
    for i,s in enumerate(c.get('sentences',[])):
        print(f'  句{i+1}: chars={len(s.get("tone",""))} | tone={s.get("tone","")} | text={s.get("text","")}')
    v = d.get(str(cid), {})
    print(f'  代表作: main={len(v.get("main",[]))}, variant={len(v.get("variant",[]))}')
    for w in v.get('main',[]):
        print(f'    - {w.get("title","?")} | {w.get("author","?")} | {str(w.get("text",""))[:40]}')
    print()