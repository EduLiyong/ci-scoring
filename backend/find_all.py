# -*- coding: utf-8 -*-
import importlib.util
spec = importlib.util.spec_from_file_location('cd', 'cipai_data.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
db = mod.CIPAI_DATABASE

# Show ALL cipai entries
for e in db:
    pat = e.get('patterns', [{}])[0]
    print(f'id={e["id"]:3d} {e["name"]:<12} total={pat.get("total_chars")}')
