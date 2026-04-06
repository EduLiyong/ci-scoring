import sqlite3

db_path = r'd:\MyClaw\ci-scoring\backend\ci_scoring.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 列出所有表
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("所有表:", [t[0] for t in tables])

# 查每个表的数据量
for t in tables:
    name = t[0]
    if name.startswith('sqlite_'):
        continue
    cur.execute(f"SELECT COUNT(*) FROM {name}")
    print(f"  {name}: {cur.fetchone()[0]} 行")

conn.close()
