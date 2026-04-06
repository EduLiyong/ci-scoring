"""
用迷神引替换ID 36(望海潮)，用昼夜乐替换ID 50(谒金门)
正确更新 cipai_data.py
"""
import sys, re, json
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
import cipai_data as cp

# 迷神引 97字 - 根据longyusheng.org权威数据
# 上片11句: 7+7+4+3+3+3+3+5+3+5+3 = 46? (权威说48)
# 下片11句: 7+7+4+3+3+3+3+5+3+5+3 = 46? (权威说49)
# 合计22句97字

MISY_SENTENCES = [
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 4, "rhyme": False, "tone": "中平中仄"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": False, "tone": "中仄仄"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 3, "rhyme": True,  "rhyme_type": "仄", "tone": "中平中仄"},
]

# 昼夜乐 98字 - 根据品诗文网数据
# 上片8句，下片8句
ZHOUYELE_SENTENCES = [
    {"chars": 7, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄平平仄仄平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 5, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": False, "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
    {"chars": 4, "rhyme": True,  "rhyme_type": "仄", "tone": "中仄仄平平"},
]

misy_total = sum(s['chars'] for s in MISY_SENTENCES)
zhouyetotal = sum(s['chars'] for s in ZHOUYELE_SENTENCES)
print('迷神引句子字数合计: %d' % misy_total)
print('昼夜乐句子字数合计: %d' % zhouyetotal)

misy_entry = {
    "alias": ["迷神引"],
    "description": "双调九十七字，前段十一句六仄韵，后段十一句六仄韵",
    "dynasty": "宋",
    "id": 36,
    "name": "迷神引",
    "patterns": [
        {"id": "迷神引_zhengti", "description": "正体，柳永体，97字", "name": "正体",
         "total_chars": 97, "rhyme_scheme": "", "sentences": MISY_SENTENCES},
        {"id": "迷神引_bianti_zhao", "description": "变体，朱雍体，双片九十八字", "name": "朱雍体",
         "total_chars": 98, "rhyme_scheme": "", "sentences": MISY_SENTENCES + [{"chars":1,"rhyme":False,"tone":"平"}]},
        {"id": "迷神引_bianti_chao", "description": "变体二，晁补之体", "name": "晁补之体",
         "total_chars": 97, "rhyme_scheme": "", "sentences": MISY_SENTENCES}
    ]
}

zhouyele_entry = {
    "alias": ["真欢乐"],
    "description": "双调九十八字，前段八句六仄韵，后段八句五仄韵",
    "dynasty": "宋",
    "id": 50,
    "name": "昼夜乐",
    "patterns": [
        {"id": "昼夜乐_zhengti", "description": "正体，柳永体，98字", "name": "正体",
         "total_chars": 98, "rhyme_scheme": "", "sentences": ZHOUYELE_SENTENCES},
        {"id": "昼夜乐_bianti_huang", "description": "变体一，黄庭坚体，后段第五句不押韵", "name": "黄庭坚体",
         "total_chars": 98, "rhyme_scheme": "", "sentences": ZHOUYELE_SENTENCES},
        {"id": "昼夜乐_bianti_liu2", "description": "变体二，柳永别首", "name": "柳永别首",
         "total_chars": 98, "rhyme_scheme": "", "sentences": ZHOUYELE_SENTENCES}
    ]
}

# 构建 new_db
new_db = []
for c in cp.CIPAI_DATABASE:
    cid = c.get('id')
    if cid == 36:
        new_db.append(misy_entry)
        print('ID 36 -> 迷神引')
    elif cid == 50:
        new_db.append(zhouyele_entry)
        print('ID 50 -> 昼夜乐')
    else:
        new_db.append(c)

# 验证
for c in new_db:
    if c.get('id') in [36, 50]:
        print('ID %d %s patterns:' % (c.get('id'), c.get('name')))
        for p in c.get('patterns', []):
            sc = sum(s.get('chars', 0) for s in p.get('sentences', []))
            print('  %s: %d句, total_chars=%d, 句子字数合计=%d' % (p.get('name'), len(p.get('sentences',[])), p.get('total_chars'), sc))

# 写回 cipai_data.py
# 策略：用 Python 的 repr/eval 读写，但 cipai_data.py 是大文件
# 更好的方法：直接用文本替换，找到 {  'id': 36, ...} 和 { 'id': 50, ...} 的位置

with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 用正则找 ID 36 和 50 的条目（简单策略：找包含 'id': 36, 或 "id": 36, 的 dict）
# 由于 cipai_data.py 格式是 { ... 'id': 36, ... }
# 我们需要把整个 dict 替换掉

def find_entry_bounds(text, target_id):
    """找到 ID == target_id 的 dict 的开始和结束位置"""
    # 寻找包含 'id': N, 或 "id": N, 的行
    patterns = ["'id': %d," % target_id, '"id": %d,' % target_id]
    for pat in patterns:
        idx = text.find(pat)
        if idx >= 0:
            # 向前找最近的开 brace
            start = text.rfind('{', 0, idx)
            # 向后找匹配的闭 brace（简单策略：计数括号）
            depth = 0
            i = start
            while i < len(text):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        return start, i + 1
                i += 1
            return start, i
    return -1, -1

# 找到并替换
s36, e36 = find_entry_bounds(content, 36)
s50, e50 = find_entry_bounds(content, 50)
print('ID 36: 字节位置 %d - %d' % (s36, e36))
print('ID 50: 字节位置 %d - %d' % (s50, e50))

# 序列化新 entry 为 Python repr 字符串
def entry_to_py(entry):
    """把 entry dict 转成 Python 源码格式"""
    lines = []
    lines.append('  {')
    for key in ['alias', 'description', 'dynasty', 'id', 'name', 'patterns']:
        val = entry.get(key)
        if key == 'alias':
            lines.append("      'alias': %s," % str(val))
        elif key == 'description':
            lines.append("      'description': '%s'," % val)
        elif key == 'dynasty':
            lines.append("      'dynasty': '%s'," % val)
        elif key == 'id':
            lines.append("      'id': %d," % val)
        elif key == 'name':
            lines.append("      'name': '%s'," % val)
        elif key == 'patterns':
            lines.append("      'patterns': [")
            for pi, pat in enumerate(val):
                lines.append('        {')
                for pk in ['id', 'description', 'name', 'total_chars', 'rhyme_scheme', 'sentences']:
                    pv = pat.get(pk)
                    if pk == 'id':
                        lines.append("          'id': '%s'," % pv)
                    elif pk == 'description':
                        lines.append("          'description': '%s'," % pv)
                    elif pk == 'name':
                        lines.append("          'name': '%s'," % pv)
                    elif pk == 'total_chars':
                        lines.append("          'total_chars': %d," % pv)
                    elif pk == 'rhyme_scheme':
                        lines.append("          'rhyme_scheme': '',")
                    elif pk == 'sentences':
                        lines.append("          'sentences': [")
                        for si, sent in enumerate(pv):
                            comma = ',' if si < len(pv) - 1 else ''
                            lines.append("            {'chars': %d, 'rhyme': %s, 'tone': '%s', 'rhyme_type': '%s'}%s" % (
                                sent.get('chars'), 'True' if sent.get('rhyme') else 'False',
                                sent.get('tone'), sent.get('rhyme_type', '仄'), comma))
                        lines.append('          ],')
                comma = ',' if pi < len(val) - 1 else ''
                lines.append('        }%s' % comma)
            lines.append('      ],')
    lines.append('  },')
    return '\n'.join(lines)

# 替换
old36 = content[s36:e36]
old50 = content[s50:e50]
new36 = entry_to_py(misy_entry)
new50 = entry_to_py(zhouyele_entry)

print('\n替换 ID 36 (%d -> %d 字节)' % (len(old36), len(new36)))
print('替换 ID 50 (%d -> %d 字节)' % (len(old50), len(new50)))

# 执行替换
new_content = content[:s36] + new36 + content[e36:s50] + new50 + content[e50:]

with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('\ncipai_data.py 已更新！')

# 验证
import importlib
import importlib.util
spec = importlib.util.spec_from_file_location('cipai_data2', 'd:/MyClaw/ci-scoring/backend/cipai_data.py')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    db2 = mod.CIPAI_DATABASE
    for c in db2:
        if c.get('id') in [36, 50]:
            print('ID %d %s:' % (c.get('id'), c.get('name')))
            for p in c.get('patterns', []):
                sc = sum(s.get('chars', 0) for s in p.get('sentences', []))
                print('  %s: %d句, total_chars=%d, 字数合计=%d' % (p.get('name'), len(p.get('sentences',[])), p.get('total_chars'), sc))
except Exception as e:
    print('ERROR: %s' % e)

print('\n完成！')