import sys, json, urllib.request

# 先检查词牌数据
try:
    req = urllib.request.urlopen('http://localhost:5000/api/cipai/list', timeout=5)
    data = json.loads(req.read().decode('utf-8'))
    print(f"词牌数量: {data.get('total', 0)}")
    if data.get('data'):
        print(f"前3个: {[c['name'] for c in data['data'][:3]]}")
    else:
        print("WARNING: 词牌数据为空！")
except Exception as e:
    print(f"API错误: {e}")

# 检查数据库
try:
    import sqlite3
    db_path = r'd:\MyClaw\ci-scoring\backend\ci_scoring.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"\n数据库表: {tables}")
    cur.execute("SELECT COUNT(*) FROM user")
    print(f"用户数: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM work")
    print(f"作品数: {cur.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"数据库错误: {e}")
