# -*- coding: utf-8 -*-
import requests, json

BASE = "http://localhost:5000"

# 1. 先登录获取session
session = requests.Session()
login_data = {"phone": "18616996056", "code": "258"}
r = session.post(f"{BASE}/api/auth/login", json=login_data)
print("登录结果:", r.status_code, r.json())

# 2. 检查当前用户
r2 = session.get(f"{BASE}/api/auth/status")
print("当前状态:", r2.json())

# 3. 测试PUT更新代表作
update_data = {
    "title": "水调歌头",
    "author": "苏轼",
    "dynasty": "宋",
    "text": "明月几时有，把酒问青天",
    "zi": "子瞻",
    "hao": "东坡居士"
}
r3 = session.put(f"{BASE}/api/cipai/1/representatives/0", json=update_data)
print("PUT结果:", r3.status_code, r3.json())