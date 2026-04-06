import sys
sys.path.insert(0, 'd:/MyClaw/ci-scoring/backend')
from cipai_data import CIPAI_DATABASE
for c in CIPAI_DATABASE:
    n = c.get('name', '')
    if any(k in n for k in ['甘州', '十六', '荷叶', '醉花', '迷神', '昼夜', '雨霖']):
        print(f'ID {c.get("id")}: {n}')