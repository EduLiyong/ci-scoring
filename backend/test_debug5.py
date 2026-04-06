# -*- coding: utf-8 -*-
import sqlite3, requests, json

DB = "d:/MyClaw/ci-scoring/backend/ci_scoring.db"
conn = sqlite3.connect(DB)
conn.text_factory = str
c = conn.cursor()
c.execute("SELECT code, phone, used, created_at FROM sms_codes ORDER BY created_at DESC LIMIT 10")
codes = c.fetchall()
print("最近的验证码:")
for c_row in codes:
    print(f"  code={c_row[0]}, phone={c_row[1]}, used={c_row[2]}, created_at={c_row[3]}")
conn.close()

# 测试用手机号 18616996057 (edu的注册手机号) 获取验证码
BASE = "http://localhost:5000"
session = requests.Session()
r = session.post(f"{BASE}/api/sms/send", json={"phone": "18616996057"})
print(f"\n发送验证码到 edu 手机号: {r.status_code} {r.json()}")
