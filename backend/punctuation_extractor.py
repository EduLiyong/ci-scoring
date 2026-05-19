# -*- coding: utf-8 -*-
"""
标点符号提取器 - 从代表作文本中提取标点符号
"""
import re
import json
import os

def load_rep_works():
    """加载代表作数据"""
    path = os.path.join(os.path.dirname(__file__), 'representative_works.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def extract_punctuation_positions(text):
    """
    从文本中提取每个字符后面的标点符号位置
    
    返回: {字符位置: 标点符号}
    """
    # 清理换行符
    text = text.replace('\n', '').replace('\r', '').strip()
    
    punctuation_marks = '，。！？、；：""''（）【】《》…—·'
    
    positions = {}
    char_pos = 0
    
    for i, char in enumerate(text):
        if char in punctuation_marks:
            # 标点符号附加到前一个字符
            if char_pos > 0:
                positions[char_pos - 1] = char
        else:
            char_pos += 1
    
    return positions


def get_punctuation_positions_for_pattern(cipai_id, pattern_index):
    """
    获取指定格律的标点位置信息
    
    参数:
        cipai_id: 词牌ID
        pattern_index: 格律索引
    
    返回:
        {字符位置: 标点符号}
    """
    # 加载代表作数据
    # 代表作数据的ID从1开始，格律数据的ID从0开始，需要+1调整
    rep_works = load_rep_works()
    cipai_reps = rep_works.get(str(cipai_id), {})
    
    # 尝试找到对应格律的代表作
    works = None
    pattern_key = str(pattern_index)
    
    if pattern_key in cipai_reps:
        works = cipai_reps[pattern_key]
    elif pattern_index == 0 and 'main' in cipai_reps:
        works = cipai_reps['main']
    elif 'variants' in cipai_reps and pattern_index > 0:
        variants = cipai_reps.get('variants', [])
        if pattern_index - 1 < len(variants):
            works = variants[pattern_index - 1].get('works', [])
    elif 'main' in cipai_reps and pattern_index == 0:
        works = cipai_reps['main']
    
    if not works or len(works) == 0:
        return {}
    
    # 获取第一个代表作的文本
    work = works[0] if isinstance(works, list) else works
    text = work.get('text', work.get('content', ''))
    
    if not text:
        return {}
    
    # 提取标点位置
    return extract_punctuation_positions(text)


def extract_punctuation_from_text(text):
    """
    从文本中提取每句的标点符号
    
    返回: [(句子文本, 标点符号), ...]
    """
    # 先清理换行符和多余空格
    text = text.replace('\n', '').replace('\r', '').strip()
    
    # 中文标点符号
    punctuation_marks = '，。！？、；：""''（）【】《》…—·'
    
    # 按标点分句
    sentences = []
    current_sentence = ''
    
    for char in text:
        if char in punctuation_marks:
            # 遇到标点，保存句子和标点
            if current_sentence:
                sentences.append((current_sentence, char))
                current_sentence = ''
        else:
            current_sentence += char
    
    # 最后可能还有未结束的句子（没有标点结尾）
    if current_sentence:
        sentences.append((current_sentence, ''))
    
    return sentences


def extract_sub_sentences_from_rep(text, total_chars):
    """
    从代表作文本中提取子句断句信息
    
    参数:
        text: 代表作文本
        total_chars: 格律数据的总字数（用于匹配句号句）
    
    返回:
        [
            {'chars': 5, 'punctuation': '，'},
            {'chars': 5, 'punctuation': '。'},
            ...
        ]
    """
    # 清理换行符
    text = text.replace('\n', '').replace('\r', '').strip()
    
    # 先提取所有子句
    all_sub_sentences = extract_punctuation_from_text(text)
    
    # 合并为句号句
    period_sentences = []  # [(总字数, [子句列表])]
    current_period = []
    current_chars = 0
    
    for sub_text, punct in all_sub_sentences:
        current_period.append({'chars': len(sub_text), 'punctuation': punct})
        current_chars += len(sub_text)
        
        if punct in '。！？':  # 句号结尾
            period_sentences.append((current_chars, current_period))
            current_period = []
            current_chars = 0
    
    return period_sentences

def get_sub_sentences_for_pattern(cipai_id, pattern_index, sentences_data):
    """
    获取指定格律的子句断句信息（旧方法，仅用于按句号分句的格律数据）
    """
    # 加载代表作数据
    rep_works = load_rep_works()
    cipai_reps = rep_works.get(str(cipai_id), {})
    
    # 尝试找到对应格律的代表作
    works = None
    pattern_key = str(pattern_index)
    
    if pattern_key in cipai_reps:
        works = cipai_reps[pattern_key]
    elif pattern_index == 0 and 'main' in cipai_reps:
        works = cipai_reps['main']
    elif 'variants' in cipai_reps and pattern_index > 0:
        variants = cipai_reps.get('variants', [])
        if pattern_index - 1 < len(variants):
            works = variants[pattern_index - 1].get('works', [])
    elif 'main' in cipai_reps and pattern_index == 0:
        works = cipai_reps['main']
    
    if not works or len(works) == 0:
        return None
    
    # 获取第一个代表作的文本
    work = works[0] if isinstance(works, list) else works
    text = work.get('text', work.get('content', ''))
    
    if not text:
        return None
    
    # 清理换行符
    text = text.replace('\n', '').replace('\r', '').strip()
    
    # 先提取所有子句
    all_sub_sentences = extract_punctuation_from_text(text)
    
    # 合并为句号句（匹配格律数据的句子结构）
    period_sentences = []
    current_period = []
    current_chars = 0
    
    for sub_text, punct in all_sub_sentences:
        current_period.append({'chars': len(sub_text), 'punctuation': punct})
        current_chars += len(sub_text)
        
        if punct in '。！？':  # 句号结尾
            period_sentences.append({
                'total_chars': current_chars,
                'sub_sentences': current_period
            })
            current_period = []
            current_chars = 0
    
    # 验证句子数量是否匹配
    if len(period_sentences) != len(sentences_data):
        return None
    
    # 验证每句字数是否匹配
    result = []
    for i, period in enumerate(period_sentences):
        expected_chars = sentences_data[i].get('chars', len(sentences_data[i].get('tone', '')))
        if period['total_chars'] != expected_chars:
            return None
        result.append(period['sub_sentences'])
    
    return result


def get_punctuation_for_pattern(cipai_id, pattern_index, sentences_data):
    """
    获取指定格律的标点符号列表
    """
    # 加载代表作数据
    rep_works = load_rep_works()
    cipai_reps = rep_works.get(str(cipai_id), {})
    
    # 尝试找到对应格律的代表作
    # 优先使用 pattern_index 对应的代表作
    pattern_key = str(pattern_index)
    
    # 格式可能是 {"0": [...], "1": [...], ...} 或 {"main": [...], "variants": [...]}
    works = None
    
    if pattern_key in cipai_reps:
        works = cipai_reps[pattern_key]
    elif pattern_index == 0 and 'main' in cipai_reps:
        works = cipai_reps['main']
    elif 'variants' in cipai_reps and pattern_index > 0:
        variants = cipai_reps.get('variants', [])
        if pattern_index - 1 < len(variants):
            works = variants[pattern_index - 1].get('works', [])
    elif 'main' in cipai_reps and pattern_index == 0:
        works = cipai_reps['main']
    
    if not works or len(works) == 0:
        return None
    
    # 获取第一个代表作的文本
    work = works[0] if isinstance(works, list) else works
    text = work.get('text', work.get('content', ''))
    
    if not text:
        return None
    
    # 提取标点
    sentence_puncts = extract_punctuation_from_text(text)
    
    # 验证句子数量是否匹配
    if len(sentence_puncts) != len(sentences_data):
        # 句子数量不匹配，返回None表示无法使用
        return None
    
    # 验证每句字数是否匹配
    punctuations = []
    for i, (sent_text, punct) in enumerate(sentence_puncts):
        expected_chars = sentences_data[i].get('chars', len(sentences_data[i].get('tone', '')))
        actual_chars = len(sent_text)
        
        if actual_chars != expected_chars:
            # 字数不匹配，返回None
            return None
        
        punctuations.append(punct)
    
    return punctuations

def add_punctuation_to_grid(grid_data, cipai_id, pattern_index):
    """
    为填词格子数据添加标点符号
    
    参数:
        grid_data: API返回的grid数据
        cipai_id: 词牌ID
        pattern_index: 格律索引
    
    返回:
        更新后的grid_data（添加了punctuation字段）
    """
    sentences_data = grid_data.get('sentences', [])
    if not sentences_data:
        return grid_data
    
    # 获取标点
    punctuations = get_punctuation_for_pattern(cipai_id, pattern_index, sentences_data)
    
    if punctuations:
        # 添加标点到sentences
        for i, sent in enumerate(sentences_data):
            if i < len(punctuations):
                sent['punctuation'] = punctuations[i]
    
    return grid_data


def test_extraction():
    """测试标点提取"""
    # 测试水调歌头
    rep_works = load_rep_works()
    
    # 词牌ID 1 是水调歌头
    cipai_id = '1'
    pattern_index = 0
    
    cipai_reps = rep_works.get(cipai_id, {})
    print(f"词牌 {cipai_id} 的代表作数据结构: {list(cipai_reps.keys())}")
    
    # 尝试获取代表作
    if str(pattern_index) in cipai_reps:
        works = cipai_reps[str(pattern_index)]
    elif 'main' in cipai_reps:
        works = cipai_reps['main']
    else:
        works = []
    
    if works and len(works) > 0:
        text = works[0].get('text', works[0].get('content', ''))
        print(f"\n代表作文本:\n{text}\n")
        
        # 提取标点
        sentences = extract_punctuation_from_text(text)
        print(f"提取的句子和标点 ({len(sentences)} 句):")
        for i, (sent, punct) in enumerate(sentences):
            print(f"  {i+1}. [{len(sent)}字] {sent}{punct}")


if __name__ == '__main__':
    test_extraction()
