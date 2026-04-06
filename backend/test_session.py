# -*- coding: utf-8 -*-
"""检查 Flask session cookie 设置"""
import requests

BASE = "http://localhost:5000"
session = requests.Session()

# 1. 发送验证码
r = session.post(f"{BASE}/api/sms/send", json={"phone": "18616996057"})
demo_code = r.json().get('demo_code')
print(f"demo_code: {demo_code}")

# 2. 注册新用户
register_data = {
    "username": "testuser_xyz",
    "phone": "18616996057",
    "password": "123456",
    "code": demo_code
}
r2 = session.post(f"{BASE}/api/auth/register", json=register_data)
print(f"注册: {r2.json()}")

# 3. 检查session cookie
print(f"Session cookies: {session.cookies.get_dict()}")

# 4. 检查状态
r3 = session.get(f"{BASE}/api/auth/status")
print(f"状态: {r3.json()}")

# 5. 测试 PUT (用 testuser_xyz，应该失败因为不是 edu)
r4 = session.put(f"{BASE}/api/cipai/1/representatives/0", json={
    "title": "测试",
    "author": "测试",
    "dynasty": "测试",
    "text": "测试"
})
print(f"PUT (testuser): {r4.status_code} {r4.json()}")
