# -*- coding: utf-8 -*-
"""检查 Flask session cookie 设置"""
import requests

BASE = "http://localhost:5000"
session = requests.Session()

# 1. 发送验证码
r = session.post(f"{BASE}/api/sms/send", json={"phone": "18616996057"})
print(f"验证码 response: {r.status_code} {r.text[:200]}")

# 2. 先获取验证码
demo_code = r.json().get('demo_code')
print(f"demo_code: {demo_code}")

# 3. 注册 - 用户名用一个新的
import time
register_data = {
    "username": f"test_{int(time.time())}",
    "phone": "18616996057",
    "password": "123456",
    "code": demo_code
}
r2 = session.post(f"{BASE}/api/auth/register", json=register_data)
print(f"注册 response: {r2.status_code} {r2.text[:300]}")

if r2.status_code != 200:
    print("注册失败，检查错误")
else:
    data = r2.json()
    print(f"注册结果: {data}")

    # 4. 检查session cookie
    print(f"Session cookies: {session.cookies.get_dict()}")

    # 5. 检查状态
    r3 = session.get(f"{BASE}/api/auth/status")
    print(f"状态: {r3.json()}")
