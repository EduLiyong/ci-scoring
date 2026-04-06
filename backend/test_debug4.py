# -*- coding: utf-8 -*-
import sqlite3, os

DB = "d:/MyClaw/ci-scoring/backend/ci_scoring.db"
conn = sqlite3.connect(DB)
conn.text_factory = str  # 避免UTF-8解码问题
c = conn.cursor()
c.execute("SELECT id, username, phone FROM users")
users = c.fetchall()
print("数据库中的用户:")
for u in users:
    print(f"  id={u[0]}, username={repr(u[1])}, phone={u[2]}")
conn.close()
