# -*- coding: utf-8 -*-
import sqlite3, requests, json

DB = "d:/MyClaw/ci-scoring/backend/ci_scoring.db"

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT id, username, phone FROM user")
users = c.fetchall()
print("数据库中的用户:")
for u in users:
    print(f"  id={u[0]}, username={u[1]}, phone={u[2]}")
conn.close()

# 测试 edu 登录
BASE = "http://localhost:5000"
session = requests.Session()

# 尝试直接用用户名密码登录（假设密码是 123456）
login_data = {"login": "edu", "password": "123456"}
r = session.post(f"{BASE}/api/auth/login", json=login_data)
print(f"\n登录结果: {r.status_code} {r.json()}")

# 检查状态
r2 = session.get(f"{BASE}/api/auth/status")
print(f"当前状态: {r2.json()}")

# 如果登录成功，测试 PUT
if r2.json().get('logged_in'):
    update_data = {
        "title": "水调歌头·明月几时有",
        "author": "苏轼",
        "dynasty": "宋",
        "text": "明月几时有，把酒问青天",
        "zi": "子瞻",
        "hao": "东坡居士"
    }
    r3 = session.put(f"{BASE}/api/cipai/1/representatives/0", json=update_data)
    print(f"PUT结果: {r3.status_code} {r3.json()}")
