# -*- coding: utf-8 -*-
"""作者简介 - 从 JSON 加载"""
import json, os

def load_author_bios():
    path = os.path.join(os.path.dirname(__file__), 'author_bios.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_author_bio(name):
    bios = load_author_bios()
    return bios.get(name, None)

def get_all_bios():
    return load_author_bios()
