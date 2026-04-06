# -*- coding: utf-8 -*-
"""
词作评分系统 - Flask 主应用
"""
import os
import sys
import json
import random
import string
import hashlib
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 将backend目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from cipai_data import get_all_cipai, search_cipai, get_cipai_by_id
from rhythm_analyzer import score_rhythm
from llm_scorer import score_yijing_with_llm
from representative_works import get_rep_works, get_all_rep_works, update_rep_works
from cipai_intro import get_cipai_intro, get_all_intros

# ===== 应用配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'frontend')

app = Flask(__name__, 
            static_folder=os.path.join(FRONTEND_DIR, 'static'),
            template_folder=os.path.join(FRONTEND_DIR, 'templates'))

# 禁用静态文件缓存（开发环境）
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 生产环境使用环境变量，本地开发使用默认值
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ci_scoring_secret_2026_wxyz')

# 数据库：优先使用环境变量（Render 持久磁盘），否则用本地 SQLite
db_path = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'ci_scoring.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# CORS：生产环境允许所有来源（Render 域名动态分配）
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)

# ===== 数据模型 =====

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    works = db.relationship('Work', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'phone': self.phone,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }


class Work(db.Model):
    __tablename__ = 'works'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), default='')
    cipai_id = db.Column(db.Integer, nullable=False)
    cipai_name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # 评分结果
    rhythm_score = db.Column(db.Float, default=0.0)   # 韵律分 (0-50)
    yijing_score = db.Column(db.Float, default=0.0)   # 意境分 (0-50)
    total_score = db.Column(db.Float, default=0.0)    # 总分 (0-100)
    
    # 评分详情
    rhythm_detail = db.Column(db.Text, default='{}')  # JSON
    yijing_detail = db.Column(db.Text, default='{}')  # JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    score_count = db.Column(db.Integer, default=1)  # 评分次数

    def to_dict(self, include_detail=False):
        d = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'cipai_id': self.cipai_id,
            'cipai_name': self.cipai_name,
            'content': self.content,
            'rhythm_score': round(self.rhythm_score, 1),
            'yijing_score': round(self.yijing_score, 1),
            'total_score': round(self.total_score, 1),
            'score_count': self.score_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M'),
        }
        if include_detail:
            try:
                d['rhythm_detail'] = json.loads(self.rhythm_detail)
            except:
                d['rhythm_detail'] = {}
            try:
                d['yijing_detail'] = json.loads(self.yijing_detail)
            except:
                d['yijing_detail'] = {}
        return d


class SmsCode(db.Model):
    """短信验证码（模拟）"""
    __tablename__ = 'sms_codes'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        """验证码5分钟内有效"""
        return not self.used and (datetime.utcnow() - self.created_at).seconds < 300


# ===== 工具函数 =====

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])


# ===== 路由 =====

@app.route('/')
def index():
    return send_from_directory(os.path.join(FRONTEND_DIR, 'templates'), 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'static'), filename)


# ---- 用户认证 ----

@app.route('/api/sms/send', methods=['POST'])
def send_sms():
    """发送验证码（模拟）"""
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    
    if not phone or len(phone) != 11 or not phone.isdigit():
        return jsonify({'success': False, 'message': '请输入正确的手机号'})
    
    # 限流：同一手机号1分钟内只能发1次
    recent = SmsCode.query.filter_by(phone=phone).filter(
        SmsCode.created_at > datetime.utcnow() - timedelta(minutes=1)
    ).first()
    if recent:
        return jsonify({'success': False, 'message': '发送太频繁，请1分钟后再试'})
    
    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    
    sms = SmsCode(phone=phone, code=code)
    db.session.add(sms)
    db.session.commit()
    
    # 实际项目中这里调用短信API，此处模拟
    print(f"[SMS模拟] 向 {phone} 发送验证码: {code}")
    
    return jsonify({
        'success': True,
        'message': '验证码已发送（演示模式）',
        'demo_code': code  # 演示模式下直接返回，生产环境应删除
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '').strip()
    code = data.get('code', '').strip()
    
    # 验证字段
    if not username or len(username) < 2 or len(username) > 20:
        return jsonify({'success': False, 'message': '用户名长度应为2-20个字符'})
    if not phone or len(phone) != 11 or not phone.isdigit():
        return jsonify({'success': False, 'message': '请输入正确的手机号'})
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'})
    if not code:
        return jsonify({'success': False, 'message': '请输入验证码'})
    
    # 验证验证码
    sms = SmsCode.query.filter_by(phone=phone, code=code, used=False).order_by(
        SmsCode.created_at.desc()
    ).first()
    if not sms or not sms.is_valid():
        return jsonify({'success': False, 'message': '验证码错误或已过期'})
    
    # 检查用户名/手机号重复
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已被使用'})
    if User.query.filter_by(phone=phone).first():
        return jsonify({'success': False, 'message': '该手机号已注册'})
    
    # 创建用户
    user = User(
        username=username,
        phone=phone,
        password_hash=hash_password(password)
    )
    db.session.add(user)
    
    # 标记验证码已使用
    sms.used = True
    db.session.commit()
    
    # 自动登录
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({'success': True, 'message': '注册成功', 'user': user.to_dict()})


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True) or {}
    login_field = data.get('login', '').strip()  # 用户名或手机号
    password = data.get('password', '').strip()
    
    if not login_field or not password:
        return jsonify({'success': False, 'message': '请输入用户名/手机号和密码'})
    
    # 支持用户名或手机号登录
    user = User.query.filter(
        (User.username == login_field) | (User.phone == login_field)
    ).first()
    
    if not user or user.password_hash != hash_password(password):
        return jsonify({'success': False, 'message': '用户名/手机号或密码错误'})
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({'success': True, 'message': '登录成功', 'user': user.to_dict()})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """获取当前登录状态"""
    user = get_current_user()
    if user:
        return jsonify({'success': True, 'logged_in': True, 'user': user.to_dict()})
    return jsonify({'success': True, 'logged_in': False})


# ---- 词牌相关 ----

@app.route('/api/cipai/list', methods=['GET'])
def cipai_list():
    """获取所有词牌"""
    keyword = request.args.get('q', '').strip()
    if keyword:
        result = search_cipai(keyword)
    else:
        result = get_all_cipai()
    return jsonify({'success': True, 'data': result, 'total': len(result)})


@app.route('/api/cipai/<int:cipai_id>', methods=['GET'])
def cipai_detail(cipai_id):
    """获取词牌详情"""
    cipai = get_cipai_by_id(cipai_id)
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'}), 404
    return jsonify({'success': True, 'data': cipai})


@app.route('/api/cipai/<int:cipai_id>/representatives', methods=['GET'])
def cipai_representatives(cipai_id):
    """获取词牌代表作"""
    cipai = get_cipai_by_id(cipai_id)
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'}), 404

    rep_data = get_rep_works(cipai_id)
    if not rep_data:
        return jsonify({'success': True, 'data': {
            'name': cipai['name'],
            'main': [],
            'variants': []
        }})

    return jsonify({'success': True, 'data': {
        'name': cipai['name'],
        'main': rep_data.get('main', []),
        'variants': rep_data.get('variants', [])
    }})


@app.route('/api/cipai/<int:cipai_id>/representatives/<int:work_index>', methods=['PUT'])
def update_cipai_representative(cipai_id, work_index):
    """更新单个代表作（仅Edu可编辑）"""
    try:
        # 获取当前用户
        username = session.get('username')

        # 权限检查：只有Edu可以编辑（不区分大小写）
        if not username or username.lower() != 'edu':
            return jsonify({'success': False, 'message': '无编辑权限，仅Edu可编辑'}), 403

        # 获取请求数据
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': '请求数据无效'}), 400

        # 验证词牌存在
        cipai = get_cipai_by_id(cipai_id)
        if not cipai:
            return jsonify({'success': False, 'message': '词牌不存在'}), 404

        # 获取当前代表作数据
        rep_data = get_rep_works(cipai_id)
        if not rep_data or 'main' not in rep_data:
            return jsonify({'success': False, 'message': '代表作数据不存在'}), 404

        # 检查索引是否有效
        if work_index < 0 or work_index >= len(rep_data['main']):
            return jsonify({'success': False, 'message': '作品索引无效'}), 400

        # 验证必填字段
        required_fields = ['title', 'author', 'dynasty', 'text']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

        # 更新作品数据（保留zi和hao字段）
        rep_data['main'][work_index] = {
            'title': data['title'],
            'author': data['author'],
            'dynasty': data['dynasty'],
            'text': data['text'],
            'zi': data.get('zi', ''),
            'hao': data.get('hao', '')
        }

        # 保存
        if update_rep_works(cipai_id, rep_data):
            return jsonify({'success': True, 'message': '保存成功', 'data': rep_data['main'][work_index]})
        else:
            return jsonify({'success': False, 'message': '保存失败'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/cipai/all-representatives', methods=['GET'])
def all_cipai_representatives():
    """获取所有词牌的代表作列表"""
    all_rep = get_all_rep_works()
    return jsonify({'success': True, 'data': all_rep})


@app.route('/api/cipai/<int:cipai_id>/intro', methods=['GET'])
def cipai_intro(cipai_id):
    """获取词牌解说"""
    intro = get_cipai_intro(cipai_id)
    if intro:
        return jsonify({'success': True, 'data': intro})
    return jsonify({'success': False, 'message': '未找到该词牌解说'})


@app.route('/api/cipai/all-intros', methods=['GET'])
def all_cipai_intros():
    """获取所有词牌解说"""
    intros = get_all_intros()
    return jsonify({'success': True, 'data': intros})


# ---- 词作评分 ----

@app.route('/api/score/check-duplicate', methods=['POST'])
@login_required
def check_duplicate():
    """检查是否已有完全相同的作品"""
    data = request.get_json(silent=True) or {}
    cipai_id = data.get('cipai_id')
    content = data.get('content', '').strip()
    
    if not cipai_id or not content:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    user_id = session['user_id']
    
    # 查找该用户是否有完全相同的作品（词牌ID相同，内容完全一致）
    existing = Work.query.filter_by(
        user_id=user_id,
        cipai_id=int(cipai_id),
        content=content
    ).first()
    
    if existing:
        return jsonify({
            'success': True,
            'is_duplicate': True,
            'existing_work': existing.to_dict(include_detail=True)
        })
    
    return jsonify({'success': True, 'is_duplicate': False})


@app.route('/api/score', methods=['POST'])
@login_required
def score_poem():
    """对词作进行评分"""
    data = request.get_json(silent=True) or {}
    cipai_id = data.get('cipai_id')
    content = data.get('content', '').strip()
    title = data.get('title', '').strip()
    work_id = data.get('work_id')  # 如果是重新评分，传入现有作品ID
    force_new = data.get('force_new', False)  # 是否强制新建（忽略重复检测）
    
    if not cipai_id:
        return jsonify({'success': False, 'message': '请选择词牌'})
    if not content:
        return jsonify({'success': False, 'message': '请输入词作内容'})
    if len(content) > 2000:
        return jsonify({'success': False, 'message': '词作内容过长'})
    
    cipai = get_cipai_by_id(int(cipai_id))
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'})
    
    cipai_name = cipai['name']
    user_id = session['user_id']
    
    # 检查是否已有完全相同的作品（如果不是强制新建且不是更新已有作品）
    if not work_id and not force_new:
        existing = Work.query.filter_by(
            user_id=user_id,
            cipai_id=int(cipai_id),
            content=content
        ).first()
        
        if existing:
            return jsonify({
                'success': True,
                'is_duplicate': True,
                'message': '您已有完全相同的作品',
                'existing_work': existing.to_dict(include_detail=True)
            })
    
    # 1. 韵律评分（满分50分）
    rhythm_result = score_rhythm(content, cipai)
    rhythm_raw = rhythm_result['score']  # 0-100
    rhythm_weighted = round(rhythm_raw * 0.5, 1)  # 转为0-50
    
    # 2. 意境评分（满分50分）
    yijing_result = score_yijing_with_llm(content, cipai_name)
    yijing_raw = yijing_result.get('total_score', 60)  # 0-100
    yijing_weighted = round(yijing_raw * 0.5, 1)  # 转为0-50
    
    # 3. 总分
    total_score = round(rhythm_weighted + yijing_weighted, 1)
    
    # 保存或更新作品
    if work_id:
        # 更新已有作品
        work = Work.query.filter_by(id=work_id, user_id=user_id).first()
        if not work:
            return jsonify({'success': False, 'message': '作品不存在或无权限'})
        work.cipai_id = cipai_id
        work.cipai_name = cipai_name
        work.content = content
        work.title = title or work.title
        work.rhythm_score = rhythm_weighted
        work.yijing_score = yijing_weighted
        work.total_score = total_score
        work.rhythm_detail = json.dumps(rhythm_result, ensure_ascii=False)
        work.yijing_detail = json.dumps(yijing_result, ensure_ascii=False)
        work.updated_at = datetime.utcnow()
        work.score_count += 1
    else:
        # 新建作品
        if not title:
            title = f"{cipai_name} · {datetime.now().strftime('%Y%m%d%H%M')}"
        work = Work(
            user_id=user_id,
            title=title,
            cipai_id=cipai_id,
            cipai_name=cipai_name,
            content=content,
            rhythm_score=rhythm_weighted,
            yijing_score=yijing_weighted,
            total_score=total_score,
            rhythm_detail=json.dumps(rhythm_result, ensure_ascii=False),
            yijing_detail=json.dumps(yijing_result, ensure_ascii=False),
        )
        db.session.add(work)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '评分完成',
        'is_duplicate': False,
        'data': {
            'work_id': work.id,
            'title': work.title,
            'cipai_name': cipai_name,
            'rhythm_score': rhythm_weighted,
            'yijing_score': yijing_weighted,
            'total_score': total_score,
            'rhythm_detail': rhythm_result,
            'yijing_detail': yijing_result,
            'score_count': work.score_count
        }
    })


# ---- 历史作品 ----

@app.route('/api/works', methods=['GET'])
@login_required
def get_works():
    """获取用户历史作品列表"""
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Work.query.filter_by(user_id=user_id).order_by(Work.updated_at.desc())
    total = query.count()
    works = query.offset((page-1)*per_page).limit(per_page).all()
    
    return jsonify({
        'success': True,
        'data': [w.to_dict() for w in works],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })


@app.route('/api/works/<int:work_id>', methods=['GET'])
@login_required
def get_work(work_id):
    """获取单个作品详情"""
    user_id = session['user_id']
    work = Work.query.filter_by(id=work_id, user_id=user_id).first()
    if not work:
        return jsonify({'success': False, 'message': '作品不存在'}), 404
    return jsonify({'success': True, 'data': work.to_dict(include_detail=True)})


@app.route('/api/works/<int:work_id>', methods=['DELETE'])
@login_required
def delete_work(work_id):
    """删除作品"""
    user_id = session['user_id']
    work = Work.query.filter_by(id=work_id, user_id=user_id).first()
    if not work:
        return jsonify({'success': False, 'message': '作品不存在'}), 404
    db.session.delete(work)
    db.session.commit()
    return jsonify({'success': True, 'message': '删除成功'})


@app.route('/api/works/<int:work_id>/title', methods=['PUT'])
@login_required
def update_work_title(work_id):
    """更新作品标题"""
    user_id = session['user_id']
    work = Work.query.filter_by(id=work_id, user_id=user_id).first()
    if not work:
        return jsonify({'success': False, 'message': '作品不存在'}), 404
    data = request.json or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': '标题不能为空'})
    work.title = title
    db.session.commit()
    return jsonify({'success': True, 'message': '更新成功'})


# ---- 配置管理 ----

@app.route('/api/config/llm', methods=['GET', 'POST'])
@login_required  
def llm_config():
    """获取或设置大模型配置（仅当前会话有效）"""
    if request.method == 'POST':
        data = request.json or {}
        api_key = data.get('api_key', '')
        api_url = data.get('api_url', '')
        model = data.get('model', '')
        
        if api_key:
            os.environ['LLM_API_KEY'] = api_key
        if api_url:
            os.environ['LLM_API_URL'] = api_url
        if model:
            os.environ['LLM_MODEL'] = model
            
        # 重新加载配置
        import llm_scorer
        llm_scorer.LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
        llm_scorer.LLM_API_URL = os.environ.get('LLM_API_URL', 'https://qianfan.baidubce.com/v2/chat/completions')
        llm_scorer.LLM_MODEL = os.environ.get('LLM_MODEL', 'ernie-4.0-turbo-8k')
        
        return jsonify({'success': True, 'message': '配置已更新'})
    else:
        import llm_scorer
        return jsonify({
            'success': True,
            'data': {
                'api_url': llm_scorer.LLM_API_URL,
                'model': llm_scorer.LLM_MODEL,
                'has_key': bool(llm_scorer.LLM_API_KEY)
            }
        })


# ===== 初始化数据库 =====
with app.app_context():
    db.create_all()
    print("数据库初始化完成")


if __name__ == '__main__':
    import os
    debug = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("词作评分系统启动中...")
    print(f"访问地址: http://localhost:{port}")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print("=" * 50)
    app.run(debug=debug, host='0.0.0.0', port=port)
