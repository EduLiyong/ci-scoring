"""
直接读取 cipai_data.py，找到并替换 ID 36 和 50 的条目
"""
import re, os

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

def make_sentence(sent):
    rhyme_str = 'True' if sent.get('rhyme') else 'False'
    rhyme_type = sent.get('rhyme_type', '仄')
    return "                                         {'chars': %d, 'rhyme': %s, 'rhyme_type': '%s', 'tone': '%s'}," % (
        sent['chars'], rhyme_str, rhyme_type, sent['tone'])

def make_pattern(pid, pname, pdesc, total, sentences):
    sent_block = '\n'.join(make_sentence(s) for s in sentences)
    return """            {   'id': '%s',
                'description': '%s',
                'name': '%s',
                'total_chars': %d,
                'rhyme_scheme': '',
                'sentences': [
%s
            ],
            },""" % (pid, pdesc, pname, total, sent_block)

def make_entry(eid, name, dynasty, desc, alias, patterns):
    alias_repr = repr(alias)
    pat_blocks = []
    for pi, p in enumerate(patterns):
        pcode = make_pattern(p['id'], p['name'], p['description'], p['total_chars'], p['sentences'])
        if pi < len(patterns) - 1:
            pcode = pcode.rstrip() + ','
        pat_blocks.append(pcode)
    pat_section = ',\n'.join(pat_blocks)
    return """  {   'alias': %s,
        'description': '%s',
        'dynasty': '%s',
        'id': %d,
        'name': '%s',
        'patterns': [
%s
        ],
  },""" % (alias_repr, desc, dynasty, eid, name, pat_section)

# 生成迷神引和昼夜乐的代码
misy_code = make_entry(36, '迷神引', '宋',
    '双调九十七字，前段十一句六仄韵，后段十一句六仄韵',
    ['迷神引'],
    [
        {'id': '迷神引_zhengti', 'name': '正体', 'description': '正体，柳永体，97字', 'total_chars': 97, 'sentences': MISY_SENTENCES},
        {'id': '迷神引_bianti_chao', 'name': '晁补之体', 'description': '变体，晁补之体', 'total_chars': 97, 'sentences': MISY_SENTENCES},
        {'id': '迷神引_bianti_zhao', 'name': '朱雍体', 'description': '变体，朱雍体，双片九十八字', 'total_chars': 98, 'sentences': MISY_SENTENCES + [{'chars':1,'rhyme':False,'rhyme_type':'平','tone':'平'}]},
    ])

zhouyele_code = make_entry(50, '昼夜乐', '宋',
    '双调九十八字，前段八句六仄韵，后段八句五仄韵',
    ['真欢乐'],
    [
        {'id': '昼夜乐_zhengti', 'name': '正体', 'description': '正体，柳永体，98字', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
        {'id': '昼夜乐_bianti_huang', 'name': '黄庭坚体', 'description': '变体一，黄庭坚体，后段第五句不押韵', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
        {'id': '昼夜乐_bianti_liu2', 'name': '柳永别首', 'description': '变体二，柳永别首体', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
    ])

print('迷神引代码生成完毕，长度: %d' % len(misy_code))
print('昼夜乐代码生成完毕，长度: %d' % len(zhouyele_code))

# 读取 cipai_data.py
with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('文件总行数: %d' % len(lines))

# 找到 ID 36 和 50 的行
id36_line = None
id50_line = None
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("'id':") or stripped.startswith('"id":'):
        if ", 36," in stripped or ", 36" in stripped:
            id36_line = i
        if ", 50," in stripped or ", 50" in stripped:
            id50_line = i

print('ID 36 在第 %d 行: %s' % (id36_line+1, lines[id36_line].strip()[:80]))
print('ID 50 在第 %d 行: %s' % (id50_line+1, lines[id50_line].strip()[:80]))

# 向前找到每个 entry 的起始 {（整行缩进的）
def find_entry_start(lines, id_line):
    for i in range(id_line, -1, -1):
        stripped = lines[i].rstrip()
        # 找到了顶部缩进的 {
        if stripped == '{':
            return i
    return -1

# 向后找到 entry 结束（计数括号）
def find_entry_end(lines, start):
    depth = 0
    for i in range(start, len(lines)):
        for ch in lines[i]:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return i
    return -1

s36 = find_entry_start(lines, id36_line)
e36 = find_entry_end(lines, s36)
s50 = find_entry_start(lines, id50_line)
e50 = find_entry_end(lines, s50)

print('ID 36 entry: 行 %d - %d' % (s36+1, e36+1))
print('ID 50 entry: 行 %d - %d' % (s50+1, e50+1))
print()
print('原 ID 36 首行: %s' % lines[s36].rstrip()[:80])
print('原 ID 36 末行: %s' % lines[e36].rstrip()[:80])
print('原 ID 50 首行: %s' % lines[s50].rstrip()[:80])
print('原 ID 50 末行: %s' % lines[e50].rstrip()[:80])

# 构建新内容
# 策略：从后向前替换（先替换 50，再替换 36，避免位置偏移）
new_lines = lines[:]

# 替换 ID 50（后面的那个）
new_lines[e50+1:] = []
new_lines[s50:e50+1] = [zhouyele_code + '\n']

# 现在行数变化了，重新计算 s36
# s36 之前的位置不变，但 e36 需要重新计算（因为 50 的部分被替换了）
# 新文件中，s36 的位置仍然是 s36，但 e36 变成了 s36 + len(zhouyele_code.split('\n'))
# 实际上，我们只替换了 [s50:e50+1]，所以 e36 之后的部分会前移
# 但是 36 在 50 之前，所以 36 的位置不受影响

# 替换 ID 36
new_lines[s36:e36+1] = [misy_code + '\n']

# 写回
with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('\ncipai_data.py 已更新！')
print('总行数变化: %d -> %d' % (len(lines), len(new_lines)))

# 验证语法
import subprocess
result = subprocess.run(
    ['C:\\Users\\Thinkpad\\.workbuddy\\binaries\\python\\versions\\3.13.12\\python.exe',
     '-c', 'import sys; sys.path.insert(0,"d:/MyClaw/ci-scoring/backend"); import cipai_data; print("OK, entries:", len(cipai_data.CIPAI_DATABASE))'],
    capture_output=True, text=True
)
print('验证结果:')
print('  stdout:', result.stdout.strip())
print('  stderr:', result.stderr.strip()[:200] if result.stderr else '无')

print('\n完成！')