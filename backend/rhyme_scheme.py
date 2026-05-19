# -*- coding: utf-8 -*-
"""
韵格分类模块

将词牌按韵脚分布规则分为5类：
1. 平韵格 - 通篇一韵到底，押平声
2. 仄韵格 - 通篇一韵到底，押仄声
3. 阕间换韵 - 上阕一个韵，下阕换一个韵
4. 阕内换韵 - 一阕之中中途换韵
5. 阕内+阕间皆换韵 - 上下阕各自内部还换韵
"""

import re

# 韵格类型常量
PING_YUN_GE = 'ping_yun_ge'           # 平韵格
ZE_YUN_GE = 'ze_yun_ge'               # 仄韵格
QUE_JIAN_HUAN_YUN = 'que_jian'         # 阕间换韵
QUE_NEI_HUAN_YUN = 'que_nei'           # 阕内换韵
QUE_NEI_JIAN_HUAN_YUN = 'que_nei_jian' # 阕内+阕间皆换韵

# 韵格显示信息（水墨朱砂配色）
RHYME_SCHEME_DISPLAY = {
    PING_YUN_GE: {
        'name': '平韵格',
        'desc': '通篇一韵到底，押平声',
        'color': '#3d5c4a',
        'icon': '平',
    },
    ZE_YUN_GE: {
        'name': '仄韵格',
        'desc': '通篇一韵到底，押仄声',
        'color': '#c9647e',
        'icon': '仄',
    },
    QUE_JIAN_HUAN_YUN: {
        'name': '阕间换韵',
        'desc': '上阕一个韵，下阕换一个韵',
        'color': '#7a9c88',
        'icon': '换',
    },
    QUE_NEI_HUAN_YUN: {
        'name': '阕内换韵',
        'desc': '一阕之中中途换韵',
        'color': '#5d7a6b',
        'icon': '换',
    },
    QUE_NEI_JIAN_HUAN_YUN: {
        'name': '阕内+阕间皆换韵',
        'desc': '上下阕各自内部还换韵',
        'color': '#a07050',
        'icon': '换',
    },
}


def parse_ye_rhyme_info(description):
    """
    从description中解析叶韵信息。
    
    例如：
    - "两平韵一叶韵" -> {'ping': 2, 'ye': 1}
    - "四平韵五叶韵" -> {'ping': 4, 'ye': 5}
    
    Returns:
        dict or None
    """
    if not description:
        return None
    
    cn_nums = {'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
               '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18}
    
    def parse_num(s):
        if s.isdigit():
            return int(s)
        return cn_nums.get(s, 0)
    
    # 匹配 "X平韵X叶韵" 各种变体
    # 支持: "4平韵5叶韵", "四平韵五叶韵", "两平韵一叶韵", "2平韵1叶韵" 等
    m = re.search(r'(\d+|[一二三四五六七八九十两]+)平韵[，,]?\s*(\d+|[一二三四五六七八九十两]+)叶韵', description)
    if not m:
        return None
    
    ping_count = parse_num(m.group(1))
    ye_count = parse_num(m.group(2))
    
    return {
        'ping': ping_count,
        'ye': ye_count,
        'total_rhyme': ping_count + ye_count,
    }


def has_ye_rhyme(description):
    """判断description中是否提到叶韵"""
    if not description:
        return False
    return '叶韵' in description


def compute_rhyme_groups_from_sentences(sentences, stanza_split=None):
    """
    从sentences计算韵组分组（与app.py中的逻辑一致）。
    
    按rhyme_type连续相同分组，返回 [{index, type, sentence_indices, stanza}] 
    """
    rhyme_groups = []
    current_rhyme_type = None
    current_group_index = -1
    
    for sent_idx, sent_data in enumerate(sentences):
        if not sent_data.get('rhyme', False):
            continue
        rt = sent_data.get('rhyme_type', '平')
        if rt != current_rhyme_type:
            current_rhyme_type = rt
            current_group_index += 1
            # 判断该句属于上阕还是下阕
            stanza = None
            if stanza_split is not None:
                stanza = 'upper' if sent_idx < stanza_split else 'lower'
            rhyme_groups.append({
                'index': current_group_index,
                'type': rt,
                'sentence_indices': [sent_idx],
                'stanza': stanza,
            })
        else:
            rhyme_groups[current_group_index]['sentence_indices'].append(sent_idx)
            # 更新stanza（可能跨越阕）
            if stanza_split is not None:
                first_sent = rhyme_groups[current_group_index]['sentence_indices'][0]
                if first_sent < stanza_split and sent_idx >= stanza_split:
                    rhyme_groups[current_group_index]['stanza'] = 'cross'
                elif sent_idx >= stanza_split:
                    rhyme_groups[current_group_index]['stanza'] = 'lower'
    
    return rhyme_groups


def parse_stanza_split_from_description(description, total_sentences):
    """
    从description中解析stanza_split（前段句数）。
    
    例如：
    - "双调九十五字，前段九句四平韵，后段十句四平韵" -> 9
    - "前后段各四句二仄韵二平韵" -> 4
    - "前后段各五句" -> 5
    
    Returns:
        int or None
    """
    if not description:
        return None
    
    cn_nums = {'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
               '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,
               '十八':18,'十九':19,'二十':20,'二十一':21,'二十二':22,'二十三':23,
               '二十四':24,'二十五':25}
    
    def parse_num(s):
        if s.isdigit():
            return int(s)
        return cn_nums.get(s)
    
    # 模式1："前后段各X句" -> 前段X句
    m = re.search(r'前后段各\s*(\d+|[一二三四五六七八九十]+)\s*句', description)
    if m:
        num = parse_num(m.group(1))
        if num:
            return num
    
    # 模式2："前段X句"
    m = re.search(r'前段\s*(\d+|[一二三四五六七八九十]+)\s*句', description)
    if m:
        num = parse_num(m.group(1))
        if num:
            return num
    
    # 模式3："上下片各X句"
    m = re.search(r'上下[片阕]各\s*(\d+|[一二三四五六七八九十]+)\s*句', description)
    if m:
        num = parse_num(m.group(1))
        if num:
            return num
    
    return None


def classify_rhyme_scheme(pattern, stanza_split=None, cipai_description=None):
    """
    根据pattern的sentences和stanza_split，判断韵格类型。
    
    Args:
        pattern: 词牌格律dict，包含sentences列表
        stanza_split: 上下阕分界句索引（None表示无法确定或单调）
        cipai_description: 词牌级别的description（fallback用）
    
    Returns:
        str: 韵格类型常量
    """
    # 优先使用手动覆盖
    override = pattern.get('rhyme_scheme_override')
    if override:
        return override
    
    sentences = pattern.get('sentences', [])
    if not sentences:
        return PING_YUN_GE
    
    # 如果没有stanza_split，尝试从description中解析
    if stanza_split is None:
        desc = pattern.get('description', '') or cipai_description or ''
        stanza_split = parse_stanza_split_from_description(desc, len(sentences))
    
    # 计算韵组
    rhyme_groups = compute_rhyme_groups_from_sentences(sentences, stanza_split)
    
    if not rhyme_groups:
        return PING_YUN_GE
    
    # 只有一个韵组 -> 平韵格或仄韵格
    if len(rhyme_groups) == 1:
        if rhyme_groups[0]['type'] == '平':
            return PING_YUN_GE
        else:
            return ZE_YUN_GE
    
    # 检查叶韵：如果有叶韵，叶韵的仄声句归入平韵组
    description = pattern.get('description', '') or cipai_description or ''
    if has_ye_rhyme(description):
        ye_info = parse_ye_rhyme_info(description)
        if ye_info and ye_info['ping'] > 0:
            ping_groups = [g for g in rhyme_groups if g['type'] == '平']
            ze_groups = [g for g in rhyme_groups if g['type'] == '仄']
            
            if len(ping_groups) >= 1 and len(ze_groups) <= ye_info.get('ye', 0) + 1:
                return PING_YUN_GE
    
    # 多个韵组 -> 需要根据stanza_split判断换韵位置
    if stanza_split is None:
        # 没有阕分界信息（单调），按韵组数判断
        # 单调词牌有多个韵组 -> 阕内换韵
        return QUE_NEI_HUAN_YUN
    
    # 有stanza_split，判断韵组与阕的关系
    upper_group_types = []  # 上阕中出现的韵组类型序列
    lower_group_types = []  # 下阕中出现的韵组类型序列
    
    for g in rhyme_groups:
        g_type = g['type']
        sent_indices = g['sentence_indices']
        
        # 判断该韵组的句子分布在哪个阕
        in_upper = any(idx < stanza_split for idx in sent_indices)
        in_lower = any(idx >= stanza_split for idx in sent_indices)
        
        if in_upper and not in_lower:
            upper_group_types.append(g_type)
        elif in_lower and not in_upper:
            lower_group_types.append(g_type)
        else:
            # 跨阕韵组（上下阕共享）
            upper_group_types.append(g_type)
            lower_group_types.append(g_type)
    
    # 判断各阕内部是否有换韵
    upper_has_change = _has_type_change(upper_group_types)
    lower_has_change = _has_type_change(lower_group_types)
    
    if upper_has_change and lower_has_change:
        return QUE_NEI_JIAN_HUAN_YUN
    elif upper_has_change or lower_has_change:
        return QUE_NEI_HUAN_YUN
    else:
        # 上下阕内部都不换韵，但韵类不同 -> 阕间换韵
        # 或者上下阕韵类相同但被分成了不同组（不应该发生）
        return QUE_JIAN_HUAN_YUN


def _has_type_change(type_list):
    """判断一个类型序列中是否有变化（换韵）"""
    if len(type_list) <= 1:
        return False
    # 去重后如果有多个不同类型，说明有换韵
    seen = []
    for t in type_list:
        if not seen or seen[-1] != t:
            seen.append(t)
    return len(seen) > 1


def get_rhyme_scheme_display(scheme_type):
    """获取韵格类型的显示信息"""
    return RHYME_SCHEME_DISPLAY.get(scheme_type, {
        'name': '未知',
        'desc': '',
        'color': '#6b7280',
        'icon': '⚪',
    })


def get_rhyme_scheme_info(pattern, stanza_split=None, cipai_description=None):
    """
    获取词牌格律的韵格完整信息。
    
    Returns:
        dict: {
            'type': str,           # 韵格类型常量
            'name': str,           # 中文名
            'desc': str,           # 说明
            'color': str,          # 显示颜色
            'icon': str,           # 图标
            'rhyme_groups': list,  # 韵组详情
            'is_ye_rhyme': bool,   # 是否有叶韵
        }
    """
    scheme_type = classify_rhyme_scheme(pattern, stanza_split, cipai_description)
    display = get_rhyme_scheme_display(scheme_type)
    rhyme_groups = compute_rhyme_groups_from_sentences(
        pattern.get('sentences', []), stanza_split
    )
    description = pattern.get('description', '')
    
    return {
        'type': scheme_type,
        'name': display['name'],
        'desc': display['desc'],
        'color': display['color'],
        'icon': display['icon'],
        'rhyme_groups': [
            {
                'index': g['index'],
                'type': g['type'],
                'stanza': g['stanza'],
                'count': len(g['sentence_indices']),
            }
            for g in rhyme_groups
        ],
        'is_ye_rhyme': has_ye_rhyme(description),
    }
