# -*- coding: utf-8 -*-
import importlib.util
spec = importlib.util.spec_from_file_location('cd', 'cipai_data.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
db = mod.CIPAI_DATABASE

targets = ['南乡子', '更漏子', '渔歌子', '调笑令', '望江南', '声声慢', '喜迁莺', '六州歌头']
for e in db:
    if any(t in e['name'] for t in targets):
        pat = e.get('patterns', [{}])[0]
        print(f'id={e["id"]:3d} {e["name"]}  total={pat.get("total_chars")}')
