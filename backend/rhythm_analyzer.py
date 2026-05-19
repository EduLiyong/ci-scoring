# -*- coding: utf-8 -*-
"""
词作格律分析与匹配模块
用于分析用户词作，与词牌格律进行匹配，计算匹配度
"""

import re
import unicodedata

# ===== 声调字典（简化版） =====
# 平声字（现代普通话中1声/2声，即阴平/阳平对应古代平声）
# 仄声字（现代普通话中3声/4声，即上声/去声，以及入声字）
# 这里使用一个基于汉字unicode的简化分析

# 常见平声字集合（部分）
PING_CHARS = set(
    "天人间风云山河日月春花开来时多年长安高飞鸣声知情心明情深诗书名前行当中"
    "东西南北同工功从容终弄丰逢风封峰蜂缝冯丛聪空宫公功弓躬工龚"
    "家华茶花发麻沙纱砂哗抓瓜爪"
    "何波河歌哦鹅车遮赊奢"
    "诗知资兹慈瓷丝私丝姿磁字迟池持匙"
    "鱼虞余于娱愚迂渔瑜于予与"
    "无吴芜梧模谟"
    "微威围为维惟唯薇巍"
    "归规龟闺硅瑰"
    "怀淮槐徊回"
    "开来财才材裁"
    "台台抬胎苔"
    "难南男蓝篮岚婪"
    "烦繁凡帆番翻藩"
    "天添填甜田"
    "民频宾彬斌"
    "新心辛芯薪欣"
    "真针珍贞侦"
    "安案鞍含"
    "官冠关观棺"
    "般班盘蟠攀"
    "残蚕惭参"
    "般般鞭边便笺"
    "连莲联廉镰嫌"
    "年粘黏拈"
    "前钱乾乾虔"
    "先仙纤嫌弦"
    "言盐炎严岩"
    "愁秋抽楸"
    "流留刘榴旒绸稠"
    "悠优忧幽"
    "妆装桩庄"
    "双霜孀"
    "光汪旺望"
    "方芳房防访仿"
    "凉梁粮粮良"
    "长常场偿尝裳"
    "香想向乡降"
    "阳扬杨洋羊疡"
    "王往汪"
    "唐堂棠汤塘糖"
    "航杭行"
    "苍仓沧藏"
    "江将浆疆缰"
    "强墙枪腔"
    "翔祥详象想"
    "郎浪廊"
    "荷何河核"
    "歌哥鸽"
    "坡婆破"
    "多夺"
    "过课戈"
    "柔肉揉糅楼"
    "侯猴喉吼候"
    "投偷头"
    "求囚仇球"
    "周舟洲州"
    "浮涪"
    "谁水推嘴"
    "飞非肥废"
    "堆对兑"
    "回"
)

# 常见仄声字集合（部分）
ZE_CHARS = set(
    "我你他它们日月色白夜是有也地上下却不可去古远晚静落断断断"
    "雪月国落觉入力白册策北色息直赤"
    "泪内背对碎"
    "已以矣"
    "绿旅曲女"
    "玉浴欲育郁"
    "怒路露"
    "故固骨谷"
    "暮木目墓幕牧"
    "复福腹服"
    "出触"
    "竹烛足属"
    "屋目木"
    "忍引敛锦"
    "品品品"
    "恨很痕"
    "冷"
    "胜剩圣"
    "景警"
    "请清情静精"
    "并病饼"
    "领岭令"
    "永咏勇用"
    "断短"
    "万晚碗挽"
    "换唤幻"
    "惯管贯"
    "汉看"
    "倦卷劝"
    "但淡弹"
    "晚挽蔓"
    "念年"
    "盼叛"
    "恨恨"
    "醉最罪"
    "笑孝效校"
    "岁穗碎"
    "贵桂季"
    "未味位"
    "翠翠悴萃"
    "壁碧"
    "石识食实"
    "极击激"
    "客刻克恪"
    "迹寂积"
    "辟僻"
    "择择宅"
    "责则"
    "涩"
    "惑或伙霍"
    "阁格各割"
    "合盒核"
    "独读毒渎"
    "曲曲屈哭"
    "木目牧沐"
    "峰缝奉凤"
    "怅唱"
    "放访仿"
    "况框矿眶"
    "望忘旺"
    "让壤嚷"
    "尚赏上"
    "放仗象"
    "傲奥"
    "到道导"
    "老好号浩"
    "考靠"
    "报保宝"
    "草早造"
    "调吊"
    "晓小笑效"
    "了料聊"
    "少哨邵"
    "豹约跃"
    "过课"
    "惯管"
    "绝决诀觉"
    "血雪"
    "别裂烈列"
    "接节杰结"
    "色策册厕"
    "热折"
    "铁贴"
    "接"
    "立粒利力"
    "急吉击"
    "执织直值殖"
    "实失湿石"
    "必壁臂碧"
    "密蜜觅"
    "吃尺赤"
    "七戚漆"
    "日逸忆"
    "一逸异意义"
    "已矣以"
    "理里礼"
    "此次"
    "死似"
    "子自紫"
    "四事似"
    "至制质"
    "是视士"
    "枕镇阵"
    "甚什沈"
    "忍引"
    "尽进近"
    "印"
    "凛临"
    "品"
    "分粉"
    "恨"
    "很"
    "冷"
)


def is_ping(char):
    """判断字是否为平声（粗略判断）"""
    if char in PING_CHARS:
        return True
    if char in ZE_CHARS:
        return False
    # 无法判断时，默认为中（可平可仄）
    return None


def char_to_tone(char):
    """字符转声调标记"""
    if is_ping(char) is True:
        return '平'
    elif is_ping(char) is False:
        return '仄'
    else:
        return '中'  # 不确定



def strip_punctuation(text):
    """去除标点符号，只保留汉字"""
    return re.sub(r'[^\u4e00-\u9fff]', '', text)


def strip_title_lines(text):
    """
    去除词作开头的词牌名/标题行。
    规则：
      - 如果第一行不包含句子标点（，。等），且纯汉字字数 ≤ 12，才跳过
      - 支持格式：「水调歌头\n词句...」「水调歌头·词名\n词句...」
      - 如果第一行包含标点符号，说明它是词句，不跳过
    """
    text = text.strip()
    # 先尝试按换行分段
    lines = text.split('\n')
    if len(lines) >= 2:
        first_line = lines[0].strip()
        first_line_chars = re.sub(r'[^\u4e00-\u9fff]', '', first_line)
        rest = '\n'.join(lines[1:]).strip()
        
        # 检查第一行是否包含句子标点（，。！？；等）
        # 注意："·"不是句子标点，是标题分隔符
        punct_marks = set('，。！？；…—～')
        has_punct = any(char in punct_marks for char in first_line)
        
        # 如果第一行包含句子标点，说明它是词句，不跳过
        if has_punct:
            return text
        
        # 如果第一行纯汉字字数 ≤ 12 且下方还有内容，跳过
        # 允许更长的标题（如"水调歌头·明月几时有"有10个汉字）
        if rest and len(first_line_chars) <= 12:
            return rest
    
    # 尝试检测 "词牌名·词作名" 格式（仅去掉·前的词牌名部分）
    # 这里保守处理：如果没有换行分隔，不做切割
    return text


def split_sentences_by_punct(text):
    """按标点符号分句，返回句子列表（不包含标点）"""
    sentences = []
    current = []
    # 只用中文标点分句，不用换行（换行由 strip_title_lines 处理）
    punct_marks = set('，。！？；…—～，。！？；')
    
    for char in text:
        if char in punct_marks:
            if current:
                sentences.append(''.join(current))
                current = []
        elif '\u4e00' <= char <= '\u9fff':
            current.append(char)
    
    if current:
        sentences.append(''.join(current))
    
    return [s for s in sentences if s]


def split_sentences_with_punct(text):
    """按标点符号分句，返回句子列表（包含标点）"""
    sentences = []
    current = []
    punct_marks = set('，。！？；…—～，。！？；')
    
    for char in text:
        if char in punct_marks:
            if current:
                sentences.append(''.join(current))
                current = []
            # 记录标点符号
            sentences.append(char)
        elif '\u4e00' <= char <= '\u9fff':
            current.append(char)
    
    if current:
        sentences.append(''.join(current))
    
    # 合并句子和标点：将句子和后面的标点合并
    result = []
    i = 0
    while i < len(sentences):
        sent = sentences[i]
        # 检查是否为标点（单个字符且在标点集合中）
        if len(sent) == 1 and sent in punct_marks:
            # 如果前面有句子，合并标点
            if result:
                result[-1] += sent
            i += 1
        else:
            # 检查下一个是否为标点
            if i + 1 < len(sentences) and len(sentences[i + 1]) == 1 and sentences[i + 1] in punct_marks:
                result.append(sent + sentences[i + 1])
                i += 2
            else:
                result.append(sent)
                i += 1
    
    return result



def analyze_tones(text):
    """分析文本的声调序列"""
    chars = strip_punctuation(text)
    tones = []
    for char in chars:
        tone = char_to_tone(char)
        tones.append({'char': char, 'tone': tone})
    return tones


def pattern_to_list(pattern_str):
    """将格律字符串解析为列表"""
    # 格律如 "中仄仄平仄" 解析为 ['中','仄','仄','平','仄']
    result = []
    i = 0
    tokens = ['中', '平', '仄', '韵', '句', '读']
    while i < len(pattern_str):
        matched = False
        for token in tokens:
            if pattern_str[i:i+len(token)] == token:
                result.append(token)
                i += len(token)
                matched = True
                break
        if not matched:
            i += 1
    return result


def match_tone(actual_tone, expected_tone):
    """判断实际声调是否符合预期格律"""
    if expected_tone == '中':
        return True  # 可平可仄
    if expected_tone == '平':
        return actual_tone in ('平', '中')
    if expected_tone == '仄':
        return actual_tone in ('仄', '中')
    return True  # 其他情况（韵位等）默认符合


def calculate_sentence_match(actual_chars, expected_tones_str):
    """
    计算单个句子的格律匹配度
    actual_chars: 实际汉字列表
    expected_tones_str: 期望格律字符串，如 "中仄仄平平"
    """
    expected_list = [c for c in expected_tones_str if c in ('中', '平', '仄')]
    
    if not expected_list or not actual_chars:
        return 0.0
    
    # 长度不匹配时按短的计算
    min_len = min(len(actual_chars), len(expected_list))
    total = max(len(actual_chars), len(expected_list))
    
    match_count = 0
    for i in range(min_len):
        actual_tone = char_to_tone(actual_chars[i])
        expected = expected_list[i]
        if match_tone(actual_tone, expected):
            match_count += 1
    
    # 长度差异也纳入扣分
    length_penalty = abs(len(actual_chars) - len(expected_list)) * 0.5
    score = (match_count / total) * 100 - length_penalty
    return max(0.0, min(100.0, score))


def calculate_total_match(poem_text, pattern_sentences):
    """
    计算整首词与某个格律的总匹配度
    poem_text: 词作文本
    pattern_sentences: 格律句子列表
    返回0-100的匹配度百分比
    """
    # 将词作按标点分句
    actual_sentences = split_sentences_by_punct(poem_text)
    
    if not actual_sentences or not pattern_sentences:
        return 0.0
    
    # 期望句子数
    expected_count = len(pattern_sentences)
    actual_count = len(actual_sentences)
    
    total_score = 0.0
    total_weight = 0.0
    
    # 按句子逐一匹配
    matched_sentences = min(actual_count, expected_count)
    
    for i in range(matched_sentences):
        actual = list(actual_sentences[i])
        expected_pattern = pattern_sentences[i]
        expected_tone_str = expected_pattern.get('tone', '')
        expected_chars = expected_pattern.get('chars', len(actual))
        
        # 计算该句匹配度
        sentence_score = calculate_sentence_match(actual, expected_tone_str)
        
        # 字数匹配权重
        weight = expected_chars
        total_score += sentence_score * weight
        total_weight += weight
    
    if total_weight == 0:
        return 0.0
    
    base_score = total_score / total_weight
    
    # 句数差异扣分
    sentence_diff = abs(actual_count - expected_count)
    sentence_penalty = sentence_diff * 3  # 每差一句扣3分
    
    final_score = max(0.0, base_score - sentence_penalty)
    return round(final_score, 2)


def calculate_char_count_match(poem_text, total_chars_expected):
    """计算字数匹配度"""
    actual_chars = len(strip_punctuation(poem_text))
    if total_chars_expected <= 0:
        return 100.0
    diff = abs(actual_chars - total_chars_expected)
    # 字数差异越小越好
    score = max(0, 100 - diff * 5)
    return score


def match_poem_to_cipai(poem_text, cipai_data):
    """
    将词作与词牌的所有格律（正体+全部变体）进行匹配
    选取匹配度最高的格律作为结果
    """
    patterns = cipai_data.get('patterns', [])
    if not patterns:
        return None, 0.0, []
    
    best_pattern = None
    best_score = 0.0
    all_scores = []
    
    # 所有格律（正体 + 变体）一视同仁，全部参与匹配
    for pattern in patterns:
        sentences = pattern.get('sentences', [])
        if not sentences:
            continue
        
        # 格律平仄匹配度
        tone_score = calculate_total_match(poem_text, sentences)
        
        # 字数匹配度
        total_chars = pattern.get('total_chars', 0)
        char_score = calculate_char_count_match(poem_text, total_chars)
        
        # 综合得分：格律匹配 65% + 字数匹配 35%
        final = tone_score * 0.65 + char_score * 0.35
        
        # 正体略加权（同分时优先选正体）
        if pattern.get('type') == '正体':
            final += 0.5
        
        all_scores.append({
            'pattern': pattern,
            'score': final,
            'detail': {
                'tone_match': round(tone_score, 1),
                'char_match': round(char_score, 1),
                'total': round(final, 1),
                'pattern_type': pattern.get('type', '正体'),
            }
        })
        
        if final > best_score:
            best_score = final
            best_pattern = pattern
    
    # 按得分降序排列，方便前端展示
    all_scores.sort(key=lambda x: x['score'], reverse=True)
    
    return best_pattern, best_score, all_scores


def get_tone_analysis(poem_text, best_pattern=None):
    """
    获取词作的逐字声调分析，并与最佳匹配格律逐字对比。
    先去除词牌名/标题行，只分析词句正文。
    每字含 match 字段：
      'match'    - 符合格律
      'mismatch' - 不符合格律
      'flexible' - 该位为"中"（可平可仄），不计入错误
      'rhyme'    - 韵脚位置
      'extra'    - 超出格律字数的字
      'unknown'  - 字典未收录，按可平可仄保守处理
    """
    # 去除标题行，只保留词句正文
    clean_text = strip_title_lines(poem_text)
    
    # 使用带标点的分句函数
    sentences_with_punct = split_sentences_with_punct(clean_text)
    
    # 提取纯汉字句子用于分析
    sentences = split_sentences_by_punct(clean_text)

    # 提取格律句子列表，用于逐字对比
    pattern_sentences = []
    if best_pattern:
        pattern_sentences = best_pattern.get('sentences', [])

    result = []
    for sent_idx, sent in enumerate(sentences):
        chars_analysis = []

        # 获取对应格律句子的平仄要求
        expected_tones = []
        is_rhyme_sent = False
        if sent_idx < len(pattern_sentences):
            ps = pattern_sentences[sent_idx]
            tone_str = ps.get('tone', '')
            expected_tones = [c for c in tone_str if c in ('中', '平', '仄')]
            is_rhyme_sent = ps.get('rhyme', False)

        for char_idx, char in enumerate(sent):
            raw_tone = char_to_tone(char)   # '平' / '仄' / '中'
            # 判断是否字典未收录
            is_dict_unknown = (raw_tone == '中'
                               and char not in PING_CHARS
                               and char not in ZE_CHARS)

            if char_idx >= len(expected_tones):
                # 超出格律字数
                display_tone = '中' if is_dict_unknown else raw_tone
                chars_analysis.append({
                    'char': char,
                    'tone': display_tone,
                    'expected': '-',
                    'match': 'extra'
                })
                continue

            expected = expected_tones[char_idx]

            if is_dict_unknown:
                # 字典未收录：保守处理，标为 unknown（不算错误，显示为中）
                display_tone = '中'
                match_status = 'unknown'
            else:
                display_tone = raw_tone
                # 韵脚：最后一字且该句押韵
                is_last = (char_idx == len(sent) - 1)
                if is_last and is_rhyme_sent:
                    match_status = 'rhyme'
                elif expected == '中':
                    match_status = 'flexible'
                elif match_tone(raw_tone, expected):
                    match_status = 'match'
                else:
                    match_status = 'mismatch'
                display_tone = raw_tone

            chars_analysis.append({
                'char': char,
                'tone': display_tone,
                'expected': expected,
                'match': match_status
            })

        # 获取带标点的句子（如果存在）
        sentence_display = sentences_with_punct[sent_idx] if sent_idx < len(sentences_with_punct) else sent
        result.append({'sentence': sentence_display, 'analysis': chars_analysis})
    return result


def score_rhythm(poem_text, cipai_data):
    """
    计算词作韵律分数（满分100）
    返回分数和分析详情
    """
    # 去除词牌名/标题行后再评分
    clean_text = strip_title_lines(poem_text)
    best_pattern, best_score, all_scores = match_poem_to_cipai(clean_text, cipai_data)
    
    # 格律匹配分（满分100）
    rhythm_score = min(100.0, best_score)
    
    # 构建返回数据
    pattern_name = best_pattern.get('description', '未知格律') if best_pattern else '无法匹配'
    pattern_type = best_pattern.get('type', '未知') if best_pattern else '-'
    
    # 逐字声调分析（传入最佳匹配格律，以便逐字对比；用clean_text保持一致）
    tone_detail = get_tone_analysis(clean_text, best_pattern)
    
    return {
        'score': round(rhythm_score, 1),
        'matched_pattern': pattern_name,
        'pattern_type': pattern_type,
        'match_rate': round(best_score, 1),
        'tone_detail': tone_detail,
        'all_pattern_scores': [
            {
                'pattern': s['pattern'].get('description', ''),
                'type': s['pattern'].get('type', ''),
                'score': round(s['score'], 1)
            } for s in all_scores
        ]
    }
