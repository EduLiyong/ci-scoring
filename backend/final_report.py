# -*- coding: utf-8 -*-
"""词韵 · 代表作全面质检：综合报告"""
import json

cipai_globals = {}
with open('cipai_data.py', encoding='utf-8') as f:
    exec(f.read(), cipai_globals)
get_cipai = cipai_globals['get_cipai_by_id']

with open('representative_works.json', encoding='utf-8') as f:
    data = json.load(f)

def compute_pattern_chars(pattern):
    return sum(s.get('chars', 0) for s in pattern.get('sentences', []))

bad_words = ['persistence', 'PLACEHOLDER', '占位符', '???', 'ration',
             'bat', '稀后', '莫莫莫']

# 计算每个词牌的期望字数（从patterns[0]）
cid_expected = {}
for cid_str in data.keys():
    cid = int(cid_str)
    entry = get_cipai(cid)
    if entry and entry.get('patterns'):
        cid_expected[cid] = compute_pattern_chars(entry['patterns'][0])

# 分类统计
critical = []   # 严重错位：词作明确不属于该词牌
truncated = []  # 内容残缺：字数少于期望50%
overlong = []   # 字数超长（可能错配）
placeholder = [] # 含占位符/现代词
ok = []

for cid_str in sorted(data.keys(), key=lambda x: int(x)):
    cid = int(cid_str)
    entry = get_cipai(cid)
    if not entry:
        continue
    cname = entry['name']
    expected = cid_expected.get(cid, 0)
    wdata = data[cid_str]

    for i, w in enumerate(wdata.get('main', [])):
        text = w['text']
        actual = len(text)
        title = w['title']
        author = w['author']
        info = {'cid': cid, 'cname': cname, 'layer': '正体', 'idx': i+1,
                'title': title, 'author': author, 'actual': actual, 'expected': expected}

        # 占位符
        has_placeholder = any(bw in text for bw in bad_words)
        if has_placeholder:
            placeholder.append(info.copy())
            continue

        if actual < 10:
            truncated.append(info.copy())
        elif expected > 0 and actual < expected * 0.5:
            truncated.append(info.copy())
        elif expected > 0 and actual > expected * 1.4:
            overlong.append(info.copy())
        else:
            ok.append((cid, cname))

    for vi, variant in enumerate(wdata.get('variants', [])):
        vname = variant.get('name', '')
        vpatterns = entry.get('patterns', [])
        ve = 0
        if vpatterns and vi < len(vpatterns):
            ve = compute_pattern_chars(vpatterns[vi])
        elif expected > 0:
            ve = expected

        for i, w in enumerate(variant.get('works', [])):
            text = w['text']
            actual = len(text)
            title = w['title']
            author = w['author']
            info = {'cid': cid, 'cname': cname, 'layer': f'变体[{vname}]', 'idx': i+1,
                    'title': title, 'author': author, 'actual': actual, 'expected': ve}

            has_placeholder = any(bw in text for bw in bad_words)
            if has_placeholder:
                placeholder.append(info.copy())
                continue

            if actual < 10:
                truncated.append(info.copy())
            elif expected > 0 and actual < expected * 0.5:
                truncated.append(info.copy())
            elif expected > 0 and actual > expected * 1.4:
                overlong.append(info.copy())

# ===== 打印综合报告 =====
total_works = sum(len(data[k].get('main', [])) for k in data)
total_variants = sum(
    sum(len(v.get('works', [])) for v in data[k].get('variants', []))
    for k in data
)

print(f"{'='*62}")
print(f"  词韵 · 代表作全面质检报告")
print(f"{'='*62}")
print(f"检查范围: 100个词牌")
print(f"正体代表作: {total_works}首  变体代表作: {total_variants}首")
print(f"{'='*62}\n")

def print_section(title, items, color="!"):
    if not items:
        return
    # 按词牌分组
    from collections import defaultdict
    by_cipai = defaultdict(list)
    for r in items:
        by_cipai[r['cid']].append(r)
    print(f"{color} {title}  ({len(items)}条，影响{len(by_cipai)}个词牌)")
    print("-" * 62)
    for cid in sorted(by_cipai.keys()):
        entries = by_cipai[cid]
        cname = entries[0]['cname']
        print(f"  【{cname}】 id={cid}")
        for e in entries:
            diff_str = f"({e['actual']}字 vs 应{e['expected']}字)" if e['expected'] > 0 else f"({e['actual']}字)"
            print(f"    - {e['layer']}第{e['idx']}首 [{e['title']}·{e['author']}] {diff_str}")
        print()

print_section("类别A - 内容残缺（字数严重不足）", truncated)
print_section("类别B - 字数超长（可能词牌错配）", overlong)
print_section("类别C - 含占位符/现代词", placeholder)

# 列出完全没有问题的词牌
print(f"~ 正常词牌（字数偏差<40%，无占位符，共{len(ok)}首）")
from collections import Counter
ok_by_cipai = Counter(ok)
for cid, cname in sorted(ok_by_cipai.keys()):
    cnt = ok_by_cipai[(cid, cname)]
    print(f"  {cname}(id={cid}): {cnt}首")

print(f"\n{'='*62}")
print(f"总结:")
print(f"  残缺条目: {len(truncated)}条")
print(f"  超长条目: {len(overlong)}条")
print(f"  占位符:   {len(placeholder)}条")
print(f"  正常条目: {len(ok)}条")
print(f"{'='*62}")
