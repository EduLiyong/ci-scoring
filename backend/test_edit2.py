# -*- coding: utf-8 -*-
import requests, json

BASE = "http://localhost:5000"
session = requests.Session()

# 方法：用 register API（手机号已注册过会报错，但 session 可能已有了）
# 尝试直接用 register 走一遍
register_data = {
    "username": "edu",
    "phone": "18616996056",
    "password": "123456",
    "code": "258"
}
r = session.post(f"{BASE}/api/auth/register", json=register_data)
print("注册结果:", r.status_code, r.json())

# 检查状态
r2 = session.get(f"{BASE}/api/auth/status")
print("当前状态:", r2.json())
