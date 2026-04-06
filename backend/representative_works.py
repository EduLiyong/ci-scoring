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
    return data.get(str(cipai_id), None)

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
