# -*- coding: utf-8 -*-
import cipai_data, re
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Find actual IDs for each ci pattern
patterns_needed = ['满江红', '沁园春', '永遇乐', '贺新郎', '八声甘州', '六州歌头', '暗香', '疏影',
                   '夜飞鹊', '更漏子', '祝英台近', '风入松', '惜秋华', '桂枝香', '雨霖铃',
                   '尾犯', '尾犯', '凄凉犯', '水龙吟', '更漏子', '疏影', '霜花腴']

found = {}
for entry in cipai_data.CIPAI_DATABASE:
    name = entry['name']
    if name in patterns_needed:
        tc = entry['patterns'][0]['total_chars']
        desc = entry['patterns'][0]['description']
        found[name] = (entry['id'], tc, desc)
        print(f"ID {entry['id']:3d} {name:8s}: total_chars={tc}, {desc}")

print("\n\nAll patterns:")
for entry in cipai_data.CIPAI_DATABASE:
    tc = entry['patterns'][0]['total_chars']
    print(f"ID {entry['id']:3d} {entry['name']:8s}: {tc}字")
