# -*- coding: utf-8 -*-
"""测试完整的注册+PUT流程"""
import requests, json

BASE = "http://localhost:5000"
session = requests.Session()

# 1. 发送验证码到 edu 的手机号
r = session.post(f"{BASE}/api/sms/send", json={"phone": "18616996057"})
print("发送验证码:", r.json())
demo_code = r.json().get('demo_code')
if not demo_code:
    print("无法获取demo_code，退出")
    exit()

# 2. 用验证码注册（如果已注册会失败，但session可能已经建立）
#    尝试用已有账户登录
register_data = {
    "username": "edu_test",
    "phone": "18616996057",
    "password": "123456",
    "code": demo_code
}
r2 = session.post(f"{BASE}/api/auth/register", json=register_data)
print("注册结果:", r2.status_code, r2.json())

# 3. 检查当前状态
r3 = session.get(f"{BASE}/api/auth/status")
print("当前状态:", r3.json())

# 4. 测试 PUT
update_data = {
    "title": "水调歌头·明月几时有",
    "author": "苏轼",
    "dynasty": "宋",
    "text": "明月几时有，把酒问青天。不知天上宫阙，今夕是何年。",
    "zi": "子瞻",
    "hao": "东坡居士"
}
r4 = session.put(f"{BASE}/api/cipai/1/representatives/0", json=update_data)
print("PUT结果:", r4.status_code, r4.json())
