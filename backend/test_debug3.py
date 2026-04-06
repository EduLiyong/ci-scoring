# -*- coding: utf-8 -*-
import sqlite3

DB = "d:/MyClaw/ci-scoring/backend/ci_scoring.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT id, username, phone FROM users")
users = c.fetchall()
print("数据库中的用户:")
for u in users:
    print(f"  id={u[0]}, username={u[1]}, phone={u[2]}")
conn.close()
