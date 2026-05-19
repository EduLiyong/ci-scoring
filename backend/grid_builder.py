# -*- coding: utf-8 -*-
"""
按代表作分行构建grid的模块
"""
import re


def _count_chars(text):
    """计算文本中的汉字数（排除所有标点和空格）"""
    return sum(1 for c in text if c not in '，。；：！？、""\'\'（）【】《》…—· \t　')


def parse_repr_with_pattern(repr_text, tone_sentences):
    """
    格律感知的解析器：用格律数据的每句字数来引导分句。
    
    核心思路：按格律字数从左到右依次"吃掉"代表作文本中的字符，
    遇到标点时跳过（不计入字数），从而精确分句。
    顿号(、)作为句内标点保留，不做分句标记。
    
    Args:
        repr_text: 代表作文本
        tone_sentences: 格律数据的sentences列表
    
    Returns:
        (sentences, line_groups) 或 (None, None)
    """
    if not repr_text or not isinstance(repr_text, str):
        return None, None
    
    # 分割上下阕
    parts = repr_text.split('\n\n')
    
    sentences = []
    line_groups = []
    global_sent_idx = 0
    tone_idx = 0  # 当前对应的格律句索引
    
    for part_idx, part in enumerate(parts):
        if not part.strip():
            continue
        
        # 按原文行分组：每行对应一个line_group
        lines = part.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            text = line.strip()
            current_line_indices = []
            pos = 0
            
            while pos < len(text) and tone_idx < len(tone_sentences):
                expected_chars = tone_sentences[tone_idx].get('chars', 0)
                if expected_chars <= 0:
                    tone_idx += 1
                    continue
                
                # 从pos开始，收集expected_chars个汉字（跳过标点计数）
                char_count = 0
                end_pos = pos
                punct_after_end = ''  # 句末标点
                
                while end_pos < len(text) and char_count < expected_chars:
                    ch = text[end_pos]
                    if ch in '，。；：！？、':
                        # 标点不计入字数，跳过
                        end_pos += 1
                    elif ch in ' \t　':
                        end_pos += 1
                    else:
                        # 汉字
                        char_count += 1
                        end_pos += 1
                
                # 收集紧跟在expected_chars个汉字之后的标点
                punct_after_end = ''
                while end_pos < len(text) and text[end_pos] in '，。；：！？、':
                    punct_after_end = text[end_pos]
                    end_pos += 1
                
                # 确保韵脚字永远在标点之前
                # 如果当前句应是韵脚句，但收集的句末标点不是。/！/？，
                # 则向后查找最近的。/！/？，把句子延伸到那里
                is_rhyme = tone_sentences[tone_idx].get('rhyme', False)
                if is_rhyme and punct_after_end and punct_after_end not in '。！？':
                    # 向后最多看8个字符，找最近的句末标点
                    found_pos = -1
                    for offset in range(1, 9):
                        if end_pos + offset >= len(text):
                            break
                        ch = text[end_pos + offset]
                        if ch in '。！？':
                            found_pos = end_pos + offset
                            break
                        elif ch in '，、；：':
                            # 中间标点，继续向后看
                            continue
                        else:
                            # 遇到了汉字，说明句末标点不在这个方向
                            break
                    if found_pos >= 0:
                        end_pos = found_pos + 1
                        punct_after_end = text[found_pos]

                # 提取句子文本
                sent_text = text[pos:end_pos]

                # 韵脚判断：使用格律数据（不受文本解析影响）
                is_rhyme = tone_sentences[tone_idx].get('rhyme', False)
                end_punct = punct_after_end
                
                sentences.append({
                    'text': sent_text,
                    'chars': expected_chars,
                    'rhyme': is_rhyme,
                    'end_punct': end_punct,
                    'is_upper': (part_idx == 0)
                })
                
                current_line_indices.append(global_sent_idx)
                
                pos = end_pos
                tone_idx += 1
                global_sent_idx += 1
            
            # 每行结束后，将当前行的句子索引加入line_groups
            if current_line_indices:
                line_groups.append(current_line_indices)
    
    return sentences, line_groups


def parse_repr_to_sentences(repr_text):
    """
    从代表作文本中提取句子信息（按标点分句，按换行符分行）
    
    逻辑：
    - 按所有标点（逗号、顿号、分号、冒号、句号、感叹号、问号）分割句子
    - 每个标点分隔的片段对应格律数据中的一个sentence
    - 换行符分割行（line），一行可包含多个句子
    - 韵脚判断由格律数据的rhyme字段决定，不依赖标点类型
    - 前端展示规则：韵脚标点后换行，非韵脚标点后不换行
    
    返回: (sentences, line_groups)
        sentences: [
            {
                'text': '怒发冲冠，',  # 完整文本（包含标点）
                'chars': 4,  # 不包含标点
                'rhyme': False,  # 韵脚判断（仅从句号/感叹号/问号推断，最终由格律数据覆盖）
                'end_punct': '，',
                'is_upper': True  # 是否在上阕
            }
        ]
        line_groups: [[0, 1], [2], ...]  # 每行包含的sentence索引
    """
    import re
    # 类型检查
    if not repr_text or not isinstance(repr_text, str):
        return None, None
    
    # 分割上阕和下阕
    parts = repr_text.split('\n\n')
    
    sentences = []
    line_groups = []
    
    for part_idx, part in enumerate(parts):
        if not part.strip():
            continue
        
        # 按换行符分行
        lines = part.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 用栈处理引号，把引号内的句号/感叹号/问号临时替换
            temp_line = ''
            in_quote = False
            quote_char = None
            i = 0
            placeholders = []
            ph_counter = 0
            
            while i < len(line):
                ch = line[i]
                
                # 检测引号开始/结束
                if ch in '"\'『」«‹「』':
                    if not in_quote:
                        in_quote = True
                        quote_char = ch
                    elif ch == quote_char:
                        in_quote = False
                        quote_char = None
                    temp_line += ch
                # 引号内的句号/感叹号/问号替换
                elif in_quote and ch in '。！？':
                    ph = f'\x00{ph_counter}\x00'
                    placeholders.append((ph, ch))
                    temp_line += ph
                    ph_counter += 1
                else:
                    temp_line += ch
                i += 1
        
        # 按所有标点（含顿号）分割，但保留分隔符
            sentence_texts = re.split(r'([，。；：！？、])', temp_line)
            
            # 重新组合句子（句子文本 + 标点）
            current_line_indices = []
            i = 0
            while i < len(sentence_texts):
                if sentence_texts[i].strip():
                    sent_text = sentence_texts[i]
                    # 检查下一个是否是标点
                    if i + 1 < len(sentence_texts) and sentence_texts[i + 1] in ['，', '。', '；', '：', '！', '？', '、']:
                        sent_text += sentence_texts[i + 1]
                        i += 1
                    
                    # 先还原引号内的占位符，再判断韵脚
                    for ph, punct in placeholders:
                        sent_text = sent_text.replace(ph, punct)
                    
                    # 判断末尾标点和是否是韵脚（必须在还原占位符之后）
                    end_punct = ''
                    rhyme = False
                    if sent_text[-1] in ['。', '！', '？']:
                        end_punct = sent_text[-1]
                        rhyme = True
                    elif sent_text[-1] in ['，', '；', '：', '、']:
                        end_punct = sent_text[-1]
                        rhyme = False
                    
                    # 重新计算字数（包含还原后的标点）
                    chars_count = 0
                    for char in sent_text:
                        if char not in ['，', '、', '；', '：', '？', '！', '。', ' ', '　']:
                            chars_count += 1
                    
                    sent_idx = len(sentences)
                    sentences.append({
                        'text': sent_text,
                        'chars': chars_count,
                        'rhyme': rhyme,
                        'end_punct': end_punct,
                        'is_upper': (part_idx == 0)
                    })
                    current_line_indices.append(sent_idx)
                
                i += 1
            
            # 一行可能包含多个句子
            if current_line_indices:
                line_groups.append(current_line_indices)
    
    return sentences, line_groups

def get_tone_for_position(tone_sentences, global_pos):
    """
    从格律数据的tone中获取指定位置的平仄信息
    """
    current_pos = 0
    for sent in tone_sentences:
        sent_chars = sent.get('chars', 0)
        if current_pos <= global_pos < current_pos + sent_chars:
            local_pos = global_pos - current_pos
            tone_str = sent.get('tone', '')
            if local_pos < len(tone_str):
                return tone_str[local_pos]
        current_pos += sent_chars
    return '中'

def get_rhyme_type_for_position(tone_sentences, global_pos):
    """
    从格律数据中获取指定位置的韵脚类型
    """
    current_pos = 0
    for sent in tone_sentences:
        sent_chars = sent.get('chars', 0)
        if current_pos <= global_pos < current_pos + sent_chars:
            local_pos = global_pos - current_pos
            if local_pos == sent_chars - 1 and sent.get('rhyme', False):
                return sent.get('rhyme_type', '平')
        current_pos += sent_chars
    return None

def build_grid_from_repr(repr_text, tone_sentences, description='', lineGroups=None):
    """
    根据代表作文本构建grid数据
    
    优先使用格律感知的解析器(parse_repr_with_pattern)，
    如果失败则fallback到标点解析器(parse_repr_to_sentences)。
    """
    # 优先使用格律感知的解析器
    repr_sentences, parsed_line_groups = parse_repr_with_pattern(repr_text, tone_sentences)
    
    if not repr_sentences or len(repr_sentences) != len(tone_sentences):
        # 格律感知解析失败，尝试标点解析器
        repr_sentences, parsed_line_groups = parse_repr_to_sentences(repr_text)
    
    # 如果解析失败，返回None
    if not repr_sentences:
        return None
    
    # 验证sentence数量是否匹配
    if len(repr_sentences) != len(tone_sentences):
        return None
    
    # 构建grid
    grid = []
    rhyme_positions = []
    global_char_index = 0
    
    for sent_idx, sent_info in enumerate(repr_sentences):
        chars_count = sent_info['chars']
        is_rhyme = tone_sentences[sent_idx].get('rhyme', False) if sent_idx < len(tone_sentences) else sent_info['rhyme']
        
        sentence_grid = {
            'sentence_index': sent_idx,
            'char_count': chars_count,
            'tone_pattern': '',
            'is_rhyme': is_rhyme,
            'punctuation': '',
            'chars': []
        }
        
        tone_pattern = ''
        
        # 计算每个字后面的标点
        punct_positions = {}
        temp_text = sent_info['text']
        temp_pos = 0
        for char in temp_text:
            if char in ['，', '、', '；', '：', '？', '！', '。']:
                if temp_pos > 0:
                    punct_positions[temp_pos - 1] = char
            elif char not in ['，', '、', '；', '：', '？', '！', '。']:
                temp_pos += 1
        
        for i in range(chars_count):
            tone_char = get_tone_for_position(tone_sentences, global_char_index)
            tone_pattern += tone_char
            rhyme_type = get_rhyme_type_for_position(tone_sentences, global_char_index)
            
            char_info = {
                'global_index': global_char_index,
                'local_index': i,
                'expected_tone': tone_char,
                'is_rhyme': False,
                'user_char': '',
                'punctuation_after': punct_positions.get(i, '')
            }
            
            if i == chars_count - 1 and is_rhyme:
                char_info['is_rhyme'] = True
                if rhyme_type:
                    char_info['rhyme_type'] = rhyme_type
                rhyme_positions.append(global_char_index)
            
            sentence_grid['chars'].append(char_info)
            global_char_index += 1
        
        sentence_grid['tone_pattern'] = tone_pattern
        grid.append(sentence_grid)
    
    # 分行逻辑：优先使用原文换行结构（parsed_line_groups），
    # 只有当原文换行结构不可用时，才按韵脚分行
    # 这解决了"句句押韵"词牌（如谒金门）中每句都单独一行的问题
    if parsed_line_groups and len(parsed_line_groups) > 0:
        line_groups = parsed_line_groups
    else:
        # 按韵脚分行：韵脚标点后换行，非韵脚标点后不换行
        line_groups = []
        current_line = []
        for sent_idx, sent_info in enumerate(repr_sentences):
            current_line.append(sent_idx)
            is_rhyme = tone_sentences[sent_idx].get('rhyme', False) if sent_idx < len(tone_sentences) else sent_info['rhyme']
            if is_rhyme:
                line_groups.append(current_line)
                current_line = []
        if current_line:
            line_groups.append(current_line)
    
    # 计算stanza_split
    stanza_split = 0
    if description:
        cn_nums = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
                   '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18,'十九':19,'二十':20}
        m = re.search(r'前段(\d+)句', description)
        if m:
            stanza_split = int(m.group(1))
        else:
            m = re.search(r'前段([一二三四五六七八九十]+)句', description)
            if m:
                stanza_split = cn_nums.get(m.group(1), 0)
            else:
                m = re.search(r'前后段各(\d+)句', description)
                if m:
                    stanza_split = int(m.group(1))
                else:
                    m = re.search(r'前后段各([一二三四五六七八九十]+)句', description)
                    if m:
                        stanza_split = cn_nums.get(m.group(1), 0)

    if not stanza_split:
        parts = repr_text.split('\n\n')
        if len(parts) == 2:
            upper_sentences, _ = parse_repr_with_pattern(parts[0], tone_sentences[:len(grid)//2] if len(grid) > 1 else tone_sentences)
            stanza_split = len(upper_sentences) if upper_sentences else 0
        else:
            stanza_split = len(grid) // 2

    return grid, line_groups, stanza_split, rhyme_positions
