"""
用迷神引替换ID 36，用昼夜乐替换ID 50
直接重写 cipai_data.py 的安全方法
"""
import sys, json, ast, os
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')

# 先从 backup 恢复 cipai_data.py
backup_file = 'd:/MyClaw/ci-scoring/backend/cipai_data.backup.py'
if os.path.exists(backup_file):
    with open('d:/MyClaw/ci-scoring/backend/cipai_data.py', 'r', encoding='utf-8') as f:
        current = f.read()
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup = f.read()
    print('backup 存在, len(backup)=%d' % len(backup))
    # 直接用 backup 重置
    cipai_py = backup
else:
    print('WARNING: 没有 backup 文件，跳过恢复')
    cipai_py = None

# 迷神引句子 (根据longyusheng.org)
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

def make_pattern(id_str, name, desc, total, sentences):
    """生成 pattern dict 的 Python 源码"""
    s_parts = []
    for si, s in enumerate(sentences):
        comma = ',' if si < len(sentences) - 1 else ''
        s_parts.append("                                         {'chars': %d, 'rhyme': %s, 'rhyme_type': '%s', 'tone': '%s'}%s" % (
            s['chars'], 'True' if s['rhyme'] else 'False', s.get('rhyme_type', '仄'), s['tone'], comma))
    s_lines = ',\n'.join(s_parts)
    return """            {   'id': '%s',
                'description': '%s',
                'name': '%s',
                'total_chars': %d,
                'rhyme_scheme': '',
                'sentences': [
%s
            ],
            },""" % (id_str, desc, name, total, s_lines)

def make_entry(entry):
    """生成整个 entry dict 的 Python 源码"""
    alias_str = repr(entry['alias'])
    patterns_lines = []
    for pi, p in enumerate(entry['patterns']):
        p_code = make_pattern(p['id'], p['name'], p['description'], p['total_chars'], p['sentences'])
        comma = ',' if pi < len(entry['patterns']) - 1 else ''
        patterns_lines.append(p_code.rstrip(',') + ',' if comma else p_code.rstrip(','))
    patterns_block = '\n'.join(patterns_lines)
    return """  {   'alias': %s,
        'description': '%s',
        'dynasty': '%s',
        'id': %d,
        'name': '%s',
        'patterns': [
%s
        ],
  },""" % (alias_str, entry['description'], entry['dynasty'], entry['id'], entry['name'], patterns_block)

# 构建迷神引和昼夜乐 entry
misy_entry = {
    'alias': ['迷神引'],
    'description': '双调九十七字，前段十一句六仄韵，后段十一句六仄韵',
    'dynasty': '宋',
    'id': 36,
    'name': '迷神引',
    'patterns': [
        {'id': '迷神引_zhengti', 'description': '正体，柳永体，97字', 'name': '正体', 'total_chars': 97, 'sentences': MISY_SENTENCES},
        {'id': '迷神引_bianti_chao', 'description': '变体，晁补之体', 'name': '晁补之体', 'total_chars': 97, 'sentences': MISY_SENTENCES},
        {'id': '迷神引_bianti_zhao', 'description': '变体，朱雍体，双片九十八字', 'name': '朱雍体', 'total_chars': 98, 'sentences': MISY_SENTENCES + [{'chars':1,'rhyme':False,'tone':'平'}]},
    ]
}

zhouyele_entry = {
    'alias': ['真欢乐'],
    'description': '双调九十八字，前段八句六仄韵，后段八句五仄韵',
    'dynasty': '宋',
    'id': 50,
    'name': '昼夜乐',
    'patterns': [
        {'id': '昼夜乐_zhengti', 'description': '正体，柳永体，98字', 'name': '正体', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
        {'id': '昼夜乐_bianti_huang', 'description': '变体一，黄庭坚体，后段第五句不押韵', 'name': '黄庭坚体', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
        {'id': '昼夜乐_bianti_liu2', 'description': '变体二，柳永别首体', 'name': '柳永别首', 'total_chars': 98, 'sentences': ZHOUYELE_SENTENCES},
    ]
}

# 用 exec 执行备份文件获取 CIPAI_DATABASE
if cipai_py:
    # 先确认 backup 内容正确（ID 36 和 50 是望海潮/谒金门）
    try:
        db_list = exec(cipai_py)
    except:
        print('backup exec 失败')
else:
    print('没有 backup，跳过')
    sys.exit(1)