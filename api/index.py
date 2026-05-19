import sys
import os

# 将项目根目录加入 sys.path，使 backend 模块可被导入
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 将 backend 目录也加入 sys.path
_backend_dir = os.path.join(_project_root, 'backend')
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# 标记运行在 Vercel 环境
os.environ['VERCEL'] = '1'

# 使用 /tmp 作为数据库目录（Vercel 唯一可写目录，每次冷启动会重置）
os.environ.setdefault('DB_PATH', '/tmp/ci_scoring.db')

# 生产环境
os.environ.setdefault('FLASK_ENV', 'production')

from backend.app import app

# Vercel Python runtime 会自动检测 Flask app 实例并作为 WSGI handler
