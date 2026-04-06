# -*- coding: utf-8 -*-
"""最终质检：全面检查所有100个词牌的代表作"""
import json
from collections import defaultdict

cipai_globals = {}
with open('cipai_data.py', encoding='utf-8') as f:
    exec(f.read(), cipai_globals)
get_cipai = cipai_globals['get_cipai_by_id']

with open('representative_works.json', encoding='utf-8') as f:
    data = json.load(f)

# 现代词/占位符检测
bad_words = ['persistence', 'PLACEHOLDER', '占位符', '???', 'ration',
             'bat', '稀后', '莫莫莫', '我们', '你们', '他们',
             '人民', '革命', '阶级', '社会', '主义']

report = []

for cid_str in sorted(data.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    entry = get_cipai(cid)
    if not entry:
        continue

    cname = entry['name']
    cpatterns = {p['id']: p for p in entry.get('patterns', [])}
    wdata = data[cid_str]

    # 检查正体
    main_pattern = cpatterns.get(f'{cname}_zhengti', cpatterns.get(entry['patterns'][0]['id']) if entry.get('patterns') else None)
    main_expected = main_pattern.get('total_chars', 0) if main_pattern else 0

    for i, w in enumerate(wdata.get('main', [])):
        text = w['text']
        title = w['title']
        author = w['author']
        actual = len(text)
        issues = []

        if actual < 10:
            issues.append(f'残缺({actual}字)')
        elif actual != main_expected and main_expected > 0:
            diff = abs(actual - main_expected) / main_expected * 100
            if diff > 20:
                issues.append(f'字数异常(应{main_expected}字,实{actual}字)')

        for bw in bad_words:
            if bw in text:
                issues.append('含现代词/占位符')
                break

        if issues:
            report.append({
                'cid': cid, 'cname': cname, 'layer': '正体',
                'idx': i+1, 'title': title, 'author': author,
                'length': actual, 'expected': main_expected,
                'issues': issues
            })

    # 检查变体
    for vi, variant in enumerate(wdata.get('variants', [])):
        vname = variant.get('name', '')
        vpattern_id = f'{cname}_{vname}'
        vpattern = cpatterns.get(vpattern_id)
        if not vpattern and entry.get('patterns') and vi < len(entry['patterns']):
            vpattern = entry['patterns'][vi]
        vexpected = vpattern.get('total_chars', 0) if vpattern else 0

        for i, w in enumerate(variant.get('works', [])):
            text = w['text']
            title = w['title']
            author = w['author']
            actual = len(text)
            issues = []

            if actual < 10:
                issues.append(f'残缺({actual}字)')
            elif actual != vexpected and vexpected > 0:
                diff = abs(actual - vexpected) / vexpected * 100
                if diff > 20:
                    issues.append(f'字数异常(应{vexpected}字,实{actual}字)')

            for bw in bad_words:
                if bw in text:
                    issues.append('含现代词/占位符')
                    break

            if issues:
                report.append({
                    'cid': cid, 'cname': cname, 'layer': f'变体[{vname}]',
                    'idx': i+1, 'title': title, 'author': author,
                    'length': actual, 'expected': vexpected,
                    'issues': issues
                })

print(f"{'='*60}")
print(f"  词韵 · 代表作全面质检报告")
print(f"{'='*60}")
print(f"检查范围: 100个词牌")
print(f"问题条目数: {len(report)}")
print(f"{'='*60}\n")

# 按词牌分组
by_cipai = defaultdict(list)
for r in report:
    by_cipai[r['cid']].append(r)

for cid in sorted(by_cipai.keys()):
    entries = by_cipai[cid]
    cname = entries[0]['cname']
    print(f"【{cname}】 id={cid}")
    for e in entries:
        print(f"  - {e['layer']}第{e['idx']}首 [{e['title']}·{e['author']}] ({e['length']}字)")
        for iss in e['issues']:
            print(f"      ! {iss}")
    print()
