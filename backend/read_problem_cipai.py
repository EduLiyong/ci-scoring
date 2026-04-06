# -*- coding: utf-8 -*-
import json

with open('representative_works.json', encoding='utf-8') as f:
    d = json.load(f)

# 看6个严重问题词牌的当前数据
for cid in [17, 44, 91, 80, 76, 78]:
    key = str(cid)
    entry = d.get(key, {})
    main = entry.get('main', [])
    variants = entry.get('variants', [])
    print('=== id=%d ===' % cid)
    for i, w in enumerate(main):
        text = w['text']
        print('  [%d] %s《%s》 %d字' % (i+1, w['author'], w['title'], len(text)))
        print('      %s' % text[:60])
    if variants:
        for vi, vg in enumerate(variants):
            vname = vg.get('name', '')
            for i, w in enumerate(vg.get('works', [])):
                print('  变体%s[%d] %s《%s》 %d字' % (vname, i+1, w['author'], w['title'], len(w['text'])))
    print()
