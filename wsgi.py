# -*- coding: utf-8 -*-
"""
WSGI 入口点 - 用于生产环境（Gunicorn / uWSGI）
"""
import sys
import os

# 将 backend 目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
