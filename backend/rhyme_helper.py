# -*- coding: utf-8 -*-
"""
填词辅助模块 - 韵脚和平仄检测
基于现代汉语拼音的简化韵部分类
"""

from pypinyin import pinyin, Style

# ===== 简化韵部分类（基于拼音韵母） =====
# 平水韵有106个韵部，这里简化为18个韵组，便于用户理解

RHYME_GROUPS = {
    'a': ['a', 'ia', 'ua'],           # 麻韵
    'o': ['o', 'uo'],                  # 波歌韵
    'e': ['e', 'ie', 'ue'],            # 皆韵
    'i': ['i', 'er'],                  # 支齐韵
    'u': ['u'],                        # 姑韵
    'v': ['v'],                        # 鱼韵
    'ai': ['ai', 'uai'],               # 开韵
    'ei': ['ei', 'ui'],                # 微韵
    'ao': ['ao', 'iao'],               # 豪韵
    'ou': ['ou', 'iu'],                # 尤韵
    'an': ['an', 'ian', 'uan', 'van'], # 寒韵
    'en': ['en', 'in', 'un', 'vn'],   # 痕韵
    'ang': ['ang', 'iang', 'uang'],    # 唐韵
    'eng': ['eng', 'ing', 'ung', 'vng'], # 庚韵
    'ong': ['ong', 'iong'],            # 东韵
    'zi_ci_si': ['i'],                  # 资韵（特殊：zi/ci/si的韵母）
    'zhi_chi_shi': ['i'],              # 知韵（特殊：zhi/chi/shi的韵母）
    'er': ['er'],                      # 儿韵
}

# 反向映射：韵母 -> 韵组
YUNMU_TO_GROUP = {}
for group, yunmus in RHYME_GROUPS.items():
    for yunmu in yunmus:
        YUNMU_TO_GROUP[yunmu] = group

def get_char_info(char):
    """
    获取汉字的拼音和平仄信息
    
    Returns:
        dict: {
            'char': 字符,
            'pinyin': 拼音（带声调）,
            'pinyin_simple': 拼音（无声调）,
            'shengmu': 声母,
            'yunmu': 韵母,
            'tone': 声调(1-4),
            'is_ping': 是否平声(1-2声为平),
            'rhyme_group': 韵组
        }
    """
    if not char or len(char) != 1:
        return None
    
    # 获取拼音（带声调）
    py_list = pinyin(char, style=Style.TONE)
    if not py_list or not py_list[0]:
        return None
    
    py_tone = py_list[0][0]  # 如 'tiān'
    
    # 获取拼音（无声调）
    py_simple_list = pinyin(char, style=Style.NORMAL)
    py_simple = py_simple_list[0][0] if py_simple_list else ''  # 如 'tian'
    
    # 获取声调数字
    py_tone_num_list = pinyin(char, style=Style.TONE3)
    tone_str = py_tone_num_list[0][0] if py_tone_num_list else ''  # 如 'tian1'
    
    # 提取声调（最后一个字符）
    tone = 0
    if tone_str and tone_str[-1].isdigit():
        tone = int(tone_str[-1])
    
    # 判断平仄：1声(阴平)、2声(阳平)为平声；3声(上声)、4声(去声)为仄声
    is_ping = tone in [1, 2] if tone > 0 else None
    
    # 提取韵母（去掉声母）
    yunmu = py_simple
    shengmu = ''
    if py_simple:
        # 常见声母列表
        shengmus = ['zh', 'ch', 'sh', 'b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 
                    'g', 'k', 'h', 'j', 'q', 'x', 'z', 'c', 's', 'r', 'y', 'w']
        for sm in shengmus:
            if py_simple.startswith(sm):
                shengmu = sm
                yunmu = py_simple[len(sm):]
                break
        
        # 特殊处理：zi, ci, si, zhi, chi, shi, ri 的韵母是 i（舌尖元音）
        if yunmu == '' and py_simple in ['zi', 'ci', 'si', 'zhi', 'chi', 'shi', 'ri']:
            yunmu = 'i'
    
    # 确定韵组
    rhyme_group = YUNMU_TO_GROUP.get(yunmu, 'unknown')
    
    return {
        'char': char,
        'pinyin': py_tone,
        'pinyin_simple': py_simple,
        'shengmu': shengmu,
        'yunmu': yunmu,
        'tone': tone,
        'is_ping': is_ping,
        'rhyme_group': rhyme_group
    }

def check_pingze(char, expected):
    """
    检查字的平仄是否符合预期
    
    Args:
        char: 汉字
        expected: 期望的平仄，'平'/'仄'/'中'（中表示可平可仄）
    
    Returns:
        dict: {
            'match': 是否匹配,
            'actual': 实际平仄,
            'expected': 期望平仄
        }
    """
    info = get_char_info(char)
    if not info:
        return {'match': False, 'actual': '未知', 'expected': expected, 'error': '无法识别'}
    
    if expected == '中':
        return {'match': True, 'actual': '平' if info['is_ping'] else '仄', 'expected': expected}
    
    actual = '平' if info['is_ping'] else '仄'
    match = actual == expected
    
    return {
        'match': match,
        'actual': actual,
        'expected': expected,
        'char': char,
        'pinyin': info['pinyin']
    }

def check_rhyme(char1, char2):
    """
    检查两个字是否押韵（属于同一韵组）
    
    Returns:
        dict: {
            'rhyme': 是否押韵,
            'group1': 字1的韵组,
            'group2': 字2的韵组,
            'yunmu1': 字1的韵母,
            'yunmu2': 字2的韵母
        }
    """
    info1 = get_char_info(char1)
    info2 = get_char_info(char2)
    
    if not info1 or not info2:
        return {'rhyme': False, 'error': '无法识别字符'}
    
    return {
        'rhyme': info1['rhyme_group'] == info2['rhyme_group'],
        'group1': info1['rhyme_group'],
        'group2': info2['rhyme_group'],
        'yunmu1': info1['yunmu'],
        'yunmu2': info2['yunmu'],
        'char1': char1,
        'char2': char2,
        'pinyin1': info1['pinyin'],
        'pinyin2': info2['pinyin']
    }

# 常用同韵字示例（按韵组分类）- 全局定义供多个函数使用
COMMON_RHYME_CHARS = {
    'a': ['家', '花', '霞', '茶', '纱', '沙', '涯', '华', '佳', '巴', '瓜', '麻', '牙'],
    'o': ['多', '歌', '河', '何', '波', '和', '磨', '罗', '萝', '过', '课', '梭', '驼', '蛾'],
    'e': ['月', '雪', '节', '绝', '别', '切', '缺', '说', '确', '叶', '夜', '灭', '列', '裂'],
    'i': ['时', '知', '思', '诗', '儿', '痴', '枝', '支', '池', '迟', '吹', '垂', '谁', '飞'],
    'u': ['书', '无', '如', '初', '湖', '珠', '孤', '途', '图', '庐', '苏', '枯', '夫', '扶'],
    'v': ['去', '雨', '语', '女', '许', '与', '处', '树', '路', '暮', '雾', '步', '度', '户'],
    'ai': ['来', '开', '台', '才', '材', '裁', '猜', '栽', '哉', '腮', '苔', '该', '孩', '骸'],
    'ei': ['非', '飞', '谁', '眉', '水', '美', '北', '杯', '悲', '备', '背', '妹', '味', '泪'],
    'ao': ['高', '劳', '豪', '桃', '逃', '涛', '朝', '潮', '招', '遥', '摇', '销', '骄'],
    'ou': ['愁', '秋', '流', '游', '头', '楼', '舟', '留', '求', '修', '收', '浮', '谋', '侯'],
    'an': ['山', '间', '还', '颜', '寒', '残', '难', '安', '班', '斑', '关', '闲', '湾'],
    'en': ['人', '春', '身', '新', '真', '尘', '神', '门', '文', '闻', '分', '纷', '痕', '根'],
    'ang': ['长', '芳', '香', '光', '霜', '堂', '凉', '黄', '茫', '忙', '阳', '杨', '扬', '郎'],
    'eng': ['声', '明', '生', '情', '行', '平', '清', '城', '成', '名', '兵', '京', '惊', '庭'],
    'ong': ['风', '空', '中', '同', '红', '东', '通', '功', '公', '宫', '松', '峰', '逢', '终'],
}

def get_rhyme_chars(char, limit=50):
    """
    获取与给定字押韵的常用字列表
    
    Args:
        char: 基准字
        limit: 返回字数限制
    
    Returns:
        list: 押韵字列表（按使用频率排序，这里简化为随机返回）
    """
    info = get_char_info(char)
    if not info:
        return []
    
    rhyme_group = info['rhyme_group']
    
    chars = COMMON_RHYME_CHARS.get(rhyme_group, [])
    
    # 过滤掉基准字本身（避免重复）
    chars = [c for c in chars if c != char]
    
    return chars[:limit]

def get_rhyme_chars_with_base(char, limit=50):
    """
    获取与给定字押韵的常用字列表（包含基准字本身）
    
    Args:
        char: 基准字
        limit: 返回字数限制
    
    Returns:
        list: 押韵字列表（包含基准字）
    """
    info = get_char_info(char)
    if not info:
        return []
    
    rhyme_group = info['rhyme_group']
    chars = COMMON_RHYME_CHARS.get(rhyme_group, [])
    
    # 去重
    seen = set()
    unique_chars = []
    for c in chars:
        if c not in seen:
            seen.add(c)
            unique_chars.append(c)
    
    return unique_chars[:limit]

def analyze_sentence_pattern(sentence_tone, user_text):
    """
    分析用户填写的句子是否符合格律
    
    Args:
        sentence_tone: 格律字符串，如 '中仄平平中仄平'
        user_text: 用户填写的文本
    
    Returns:
        list: 每个字的分析结果
    """
    results = []
    
    # 去除标点，只保留汉字
    chars = [c for c in user_text if '\u4e00' <= c <= '\u9fff']
    
    for i, (char, expected) in enumerate(zip(chars, sentence_tone)):
        if i >= len(sentence_tone):
            break
        
        result = check_pingze(char, expected)
        result['position'] = i
        results.append(result)
    
    return results

# ===== 测试代码 =====
if __name__ == '__main__':
    # 测试
    print("=== 测试汉字信息 ===")
    for char in ['天', '地', '人', '月', '风']:
        info = get_char_info(char)
        print(f"{char}: 拼音={info['pinyin']}, 平仄={'平' if info['is_ping'] else '仄'}, 韵组={info['rhyme_group']}")
    
    print("\n=== 测试押韵 ===")
    pairs = [('天', '年'), ('月', '雪'), ('花', '家'), ('风', '空')]
    for c1, c2 in pairs:
        result = check_rhyme(c1, c2)
        print(f"{c1}({result['pinyin1']}) vs {c2}({result['pinyin2']}): {'押韵' if result['rhyme'] else '不押韵'} (韵组: {result['group1']} vs {result['group2']})")
    
    print("\n=== 测试平仄 ===")
    tests = [('天', '平'), ('地', '仄'), ('人', '平'), ('月', '仄')]
    for char, expected in tests:
        result = check_pingze(char, expected)
        print(f"{char}: 期望{expected}, 实际{result['actual']}, {'匹配' if result['match'] else '不匹配'}")
