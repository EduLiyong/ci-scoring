#!/usr/bin/env python3
"""
Vercel 构建脚本：
1. 将 public/ 下的静态文件复制到 dist/
2. 将 frontend/templates/index.html 复制到 dist/index.html
   （Vercel 会自动将 dist/ 作为静态文件根目录）
"""
import os
import shutil

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, 'public')
DIST = os.path.join(BASE, 'dist')

# 清理并创建 dist 目录
if os.path.exists(DIST):
    shutil.rmtree(DIST)
shutil.copytree(PUBLIC, DIST)
print(f"✓ 静态文件已输出到 {DIST}")
