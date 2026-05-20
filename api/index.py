#!/usr/bin/env python3
"""
Vercel Python Serverless Function 入口
Vercel 会自动检测 Flask app 实例并将其作为 WSGI handler
"""
import sys
import os

# 将项目根目录加入 sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 将 backend 目录加入 sys.path
_backend_dir = os.path.join(_project_root, 'backend')
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# 标记运行在 Vercel 环境
os.environ['VERCEL'] = '1'

# Vercel 无服务器环境：/tmp 是唯一可写目录
os.environ.setdefault('DB_PATH', '/tmp/ci_scoring.db')
os.environ.setdefault('FLASK_ENV', 'production')

# 导入 Flask app
from backend.app import app

# Vercel Python runtime 会自动检测 app 变量并作为 WSGI handler
# 无需调用 app.run()
