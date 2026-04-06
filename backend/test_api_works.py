# -*- coding: utf-8 -*-
"""直接测试 api 是否正常"""
import requests, time

BASE = "http://localhost:5000"
session = requests.Session()

# 等一会儿避免频率限制
time.sleep(2)

# 1. 发送验证码
r = session.post(f"{BASE}/api/sms/send", json={"phone": "18616996057"})
print(f"SMS: {r.json()}")

# 2. 用新用户名注册（避免重复）
demo_code = r.json().get('demo_code')
if not demo_code:
    print("无法获取验证码，退出")
    exit()

import random
register_data = {
    "username": f"edu2_{random.randint(1000,9999)}",
    "phone": "18616996057",
    "password": "123456",
    "code": demo_code
}
r2 = session.post(f"{BASE}/api/auth/register", json=register_data)
print(f"注册: {r2.json()}")

# 3. GET 代表作列表（应该成功）
r3 = session.get(f"{BASE}/api/cipai/1/representatives")
print(f"GET 代表作: {r3.status_code} {r3.json().get('success')}")

# 4. PUT 更新
r4 = session.put(f"{BASE}/api/cipai/1/representatives/0", json={
    "title": "水调歌头",
    "author": "苏轼",
    "dynasty": "宋",
    "text": "明月几时有，把酒问青天",
    "zi": "子瞻",
    "hao": "东坡居士"
})
print(f"PUT 更新: {r4.status_code} {r4.json()}")
