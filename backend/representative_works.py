# -*- coding: utf-8 -*-
"""词牌代表作 - 从 JSON 加载和保存"""
import json, os

def load_rep_works():
    path = os.path.join(os.path.dirname(__file__), 'representative_works.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_rep_works(data):
    """保存代表作数据到JSON文件"""
    path = os.path.join(os.path.dirname(__file__), 'representative_works.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def get_rep_works(cipai_id):
    data = load_rep_works()
    rep = data.get(str(cipai_id), None)
    if rep:
        rep = _normalize_works(rep)
    return rep

def _normalize_works(rep):
    """将 content 字段统一转换为 text，以兼容前端显示"""
    if isinstance(rep, list):
        return [_norm_one(w) for w in rep]
    if isinstance(rep, dict):
        result = {}
        for k, v in rep.items():
            if k == 'main':
                result[k] = [_norm_one(w) for w in v] if isinstance(v, list) else v
            elif k == 'variants':
                # 兼容两种格式：
                # 1. 字典格式: [{"name": "变体一", "works": [...]}, ...]
                # 2. 列表格式: [[{作品}], [{作品}], ...]
                normalized_variants = []
                for vk in v if isinstance(v, list) else []:
                    if isinstance(vk, list):
                        # 列表格式: 直接是作品数组
                        normalized_variants.append({
                            'name': '',
                            'works': [_norm_one(w) for w in vk]
                        })
                    elif isinstance(vk, dict):
                        # 字典格式: {"name":..., "works":[...]}
                        normalized_variants.append({
                            'name': vk.get('name', ''),
                            'works': [_norm_one(w) for w in vk.get('works', [])]
                        })
                result[k] = normalized_variants
            else:
                result[k] = _normalize_works(v) if isinstance(v, (dict, list)) else v
        return result
    return rep

def _norm_one(w):
    if isinstance(w, dict) and 'content' in w and 'text' not in w:
        w = dict(w)
        w['text'] = w.pop('content')
    return w

def get_all_rep_works():
    return load_rep_works()

def update_rep_work(cipai_id, work_index, work_data, work_type='main'):
    """更新单个代表作
    cipai_id: 词牌ID
    work_index: 作品索引
    work_data: 新的作品数据
    work_type: 'main' 或 'variant'
    """
    data = load_rep_works()
    key = str(cipai_id)
    
    if key not in data:
        return False
    
    if work_type == 'main':
        if work_index >= len(data[key].get('main', [])):
            return False
        data[key]['main'][work_index] = work_data
    else:
        # 变体处理暂不支持
        return False
    
    return save_rep_works(data)

def update_rep_works(cipai_id, rep_data):
    """更新整个词牌的代表作数据"""
    data = load_rep_works()
    key = str(cipai_id)
    data[key] = rep_data
    return save_rep_works(data)

def add_rep_work(cipai_id, work_data, work_type='main', variant_index=0):
    """新增一首代表作
    
    Args:
        cipai_id: 词牌ID
        work_data: 作品数据 {title, author, dynasty, text, zi, hao}
        work_type: 'main' 或 'variant'
        variant_index: 变体索引（仅work_type='variant'时有效）
    
    Returns:
        bool: 是否成功
    """
    data = load_rep_works()
    key = str(cipai_id)
    
    if key not in data:
        # 如果该词牌还没有代表作数据，创建一个空的
        data[key] = {'main': [], 'variants': []}
    
    if work_type == 'main':
        # 正体代表作：添加到main数组末尾
        if 'main' not in data[key]:
            data[key]['main'] = []
        data[key]['main'].append(work_data)
    else:
        # 变体代表作：添加到指定变体的works数组末尾
        if 'variants' not in data[key]:
            data[key]['variants'] = []
        
        # 确保变体索引存在
        while len(data[key]['variants']) <= variant_index:
            data[key]['variants'].append({'name': f'变体{len(data[key]["variants"]) + 1}', 'works': []})
        
        if 'works' not in data[key]['variants'][variant_index]:
            data[key]['variants'][variant_index]['works'] = []
        
        data[key]['variants'][variant_index]['works'].append(work_data)
    
    return save_rep_works(data)
