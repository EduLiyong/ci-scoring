import sqlite3, json, urllib.request

db_path = r'd:\MyClaw\ci-scoring\backend\ci_scoring.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("=== 数据库状态 ===")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for t in cur.fetchall():
    name = t[0]
    if name.startswith('sqlite_'): continue
    cur.execute(f"SELECT COUNT(*) FROM {name}")
    print(f"  {name}: {cur.fetchone()[0]} 行")

print("\n=== 用户数据 ===")
cur.execute("SELECT id, username, phone FROM users")
for u in cur.fetchall():
    print(f"  用户: {u}")

print("\n=== 作品记录 ===")
cur.execute("SELECT id, title, cipai_name, total_score FROM works")
for w in cur.fetchall():
    print(f"  作品: {w}")

conn.close()

print("\n=== API 测试 ===")
try:
    req = urllib.request.urlopen('http://localhost:5000/api/cipai/list', timeout=5)
    data = json.loads(req.read().decode('utf-8'))
    print(f"词牌列表 API: {data.get('total', 0)} 个词牌 ✓")
    if data.get('data'):
        print(f"  前3个: {[c['name'] for c in data['data'][:3]]}")
except Exception as e:
    print(f"词牌列表 API 失败: {e}")

try:
    req2 = urllib.request.urlopen('http://localhost:5000/api/cipai/1', timeout=5)
    d2 = json.loads(req2.read().decode('utf-8'))
    print(f"词牌详情 API: ID=1 的词牌是 '{d2['data']['name']}' ✓")
except Exception as e:
    print(f"词牌详情 API 失败: {e}")
