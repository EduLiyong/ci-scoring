# -*- coding: utf-8 -*-
import importlib.util
spec = importlib.util.spec_from_file_location('cd', 'cipai_data.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
db = mod.CIPAI_DATABASE

targets = ['八声甘州', '摸鱼儿', '虞美人', '采桑子', '相见欢', '满庭芳', '破阵子', '双双燕']
for e in db:
    if e['name'] in targets:
        print(f'id={e["id"]:3d} name={e["name"]}')
