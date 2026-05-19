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
from representative_works import get_rep_works, get_all_rep_works, update_rep_works, add_rep_work
from cipai_intro import get_cipai_intro, get_all_intros
from rhyme_scheme import classify_rhyme_scheme, get_rhyme_scheme_info, RHYME_SCHEME_DISPLAY
from pingshui_yun import get_char_yunbu, get_yunbu_chars, check_yunbu_conflict, get_compatible_yunbus, get_all_compatible_chars
from punctuation_extractor import get_punctuation_for_pattern, get_sub_sentences_for_pattern, get_punctuation_positions_for_pattern
from author_bios import get_author_bio, get_all_bios

# ===== 应用配置 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')

print(f"BASE_DIR: {BASE_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"FRONTEND_DIR: {FRONTEND_DIR}")

if not os.path.exists(os.path.join(FRONTEND_DIR, 'templates', 'index.html')):
    print(f"WARNING: index.html not found at {os.path.join(FRONTEND_DIR, 'templates', 'index.html')}")

app = Flask(__name__, 
            static_folder=os.path.join(FRONTEND_DIR, 'static'),
            template_folder=os.path.join(FRONTEND_DIR, 'templates'))

# 禁用静态文件缓存（开发环境）
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 生产环境使用环境变量，本地开发使用默认值
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ci_scoring_secret_2026_wxyz')

# 数据库：Vercel 使用 /tmp（可写但每次冷启动重置），否则用环境变量或本地 SQLite
if os.environ.get('VERCEL'):
    db_path = os.environ.get('DB_PATH', '/tmp/ci_scoring.db')
else:
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
    # 为每个词牌添加pattern_count和韵格摘要
    list_data = []
    for cipai in result:
        # get_all_cipai()只有基本字段，需要调用get_cipai_by_id获取patterns数量
        if 'pattern_count' in cipai:
            pc = cipai['pattern_count']
        else:
            full_cp = get_cipai_by_id(cipai['id'])
            pc = len(full_cp.get('patterns', [])) if full_cp else 0
        
        # 获取韵格摘要（取正体的韵格）
        rhyme_scheme_summary = None
        if pc > 0:
            full_cp = get_cipai_by_id(cipai['id'])
            patterns = full_cp.get('patterns', []) if full_cp else []
            if patterns:
                p0 = patterns[0]
                rs_stanza_split = p0.get('stanza_split')
                rs_description = p0.get('description', '') or cipai.get('description', '')
                rs_info = classify_rhyme_scheme(p0, rs_stanza_split, rs_description)
                rs_display = RHYME_SCHEME_DISPLAY.get(rs_info, {})
                rhyme_scheme_summary = {
                    'type': rs_info,
                    'name': rs_display.get('name', '未知'),
                    'icon': rs_display.get('icon', '⚪'),
                }
        
        item = {
            'id': cipai.get('id'),
            'name': cipai.get('name'),
            'alias': cipai.get('alias', ''),
            'description': cipai.get('description', ''),
            'dynasty': cipai.get('dynasty', ''),
            'pattern_count': pc,
            'rhyme_scheme': rhyme_scheme_summary,
        }
        list_data.append(item)
    return jsonify({'success': True, 'data': list_data, 'total': len(list_data)})


@app.route('/api/cipai/<int:cipai_id>', methods=['GET'])
def cipai_detail(cipai_id):
    """获取词牌详情"""
    cipai = get_cipai_by_id(cipai_id)
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'}), 404
    
    # 为每个pattern添加韵格信息
    patterns = cipai.get('patterns', [])
    rhyme_schemes = []
    for p in patterns:
        rs_stanza_split = p.get('stanza_split')
        rs_description = p.get('description', '') or cipai.get('description', '')
        rs_info = get_rhyme_scheme_info(p, rs_stanza_split, rs_description)
        rhyme_schemes.append(rs_info)
    
    cipai['rhyme_schemes'] = rhyme_schemes
    return jsonify({'success': True, 'data': cipai})


@app.route('/api/cipai/<int:cipai_id>/representatives', methods=['GET'])
def cipai_representatives(cipai_id):
    """获取词牌代表作（支持按格律筛选）"""
    cipai = get_cipai_by_id(cipai_id)
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'}), 404

    rep_data = get_rep_works(cipai_id)
    
    # 获取格律参数（可选）
    pattern_index = request.args.get('pattern', None, type=int)
    
    if not rep_data:
        # 如果没有代表作数据，返回空
        return jsonify({'success': True, 'data': {
            'name': cipai['name'],
            'main': [],
            'variants': []
        }})
    
    # 获取格律名称
    patterns = cipai.get('patterns', [])
    
    # 检查数据格式并返回对应格律的代表作
    if pattern_index is not None:
        pattern_name = patterns[pattern_index].get('name', f'格律{pattern_index + 1}') if pattern_index < len(patterns) else f'格律{pattern_index + 1}'
        works = None
        
        # 格式1：数组格式（如沁园春），每个作品有pattern_idx
        if isinstance(rep_data, list):
            for work in rep_data:
                if work.get('pattern_idx') == pattern_index:
                    works = [work]
                    break

        # 格式2：字典格式
        elif isinstance(rep_data, dict):
            # 先检查从0开始的索引（如菩萨蛮）
            if str(pattern_index) in rep_data:
                works = rep_data.get(str(pattern_index), [])
                if not isinstance(works, list):
                    works = [works]
            # 再检查从1开始的索引（如水调歌头）
            elif str(pattern_index + 1) in rep_data:
                works = rep_data.get(str(pattern_index + 1), [])
                if not isinstance(works, list):
                    works = [works]

        if works:
            return jsonify({'success': True, 'data': {
                'name': cipai['name'],
                'pattern_name': pattern_name,
                'pattern_index': pattern_index,
                'works': works
            }})
    
    # 标准格式：返回 main 和 variants 或 0索引格式
    if isinstance(rep_data, dict):
        # 如果有main/variants格式
        if 'main' in rep_data or 'variants' in rep_data:
            # 如果传了pattern参数，返回works字段
            if pattern_index is not None:
                works = []
                variants = rep_data.get('variants', [])
                main = rep_data.get('main', [])
                num_patterns = len(patterns)
                
                # 判断数据格式：
                # 情况1：variants数量 == patterns数量（如临江仙11格），则格律0对应variants[0]
                # 情况2：variants数量 == patterns数量-1（如水调歌头8格），则格律0对应main
                if len(variants) == num_patterns:
                    # 情况1：所有格律都在variants中
                    if pattern_index < len(variants):
                        variant_item = variants[pattern_index]
                        if isinstance(variant_item, list):
                            works = variant_item
                        else:
                            works = variant_item.get('works', [])
                else:
                    # 情况2：main是正体，variants是变体
                    if pattern_index == 0:
                        works = main
                    else:
                        # 变体：variants[pattern_index - 1]
                        if pattern_index - 1 < len(variants):
                            variant_item = variants[pattern_index - 1]
                            # 兼容字典格式 {"works": [...]} 和列表格式 [...]
                            if isinstance(variant_item, list):
                                works = variant_item
                            else:
                                works = variant_item.get('works', [])
                
                pattern_name = patterns[pattern_index].get('name', f'格律{pattern_index + 1}') if pattern_index < len(patterns) else f'格律{pattern_index + 1}'
                
                return jsonify({'success': True, 'data': {
                    'name': cipai['name'],
                    'pattern_name': pattern_name,
                    'pattern_index': pattern_index,
                    'works': works
                }})
            else:
                return jsonify({'success': True, 'data': {
                    'name': cipai['name'],
                    'main': rep_data.get('main', []),
                    'variants': rep_data.get('variants', [])
                }})
        # 否则检查是否为0索引格式
        elif '0' in rep_data:
            # 将0索引格式转换为main/variants格式
            main_works = rep_data.get('0', [])
            if not isinstance(main_works, list):
                main_works = [main_works]
            
            variants = []
            for i in range(1, len(patterns)):
                pattern_key = str(i)
                if pattern_key in rep_data:
                    pattern_works = rep_data[pattern_key]
                    if not isinstance(pattern_works, list):
                        pattern_works = [pattern_works]
                    variants.append({
                        'name': patterns[i].get('name', f'变体{i}'),
                        'works': pattern_works
                    })
            
            return jsonify({'success': True, 'data': {
                'name': cipai['name'],
                'main': main_works,
                'variants': variants
            }})
    
    # 数组格式：转换为main/variants格式
    if isinstance(rep_data, list):
        # 按pattern_idx分组
        main_works = []
        variants_map = {}
        
        for work in rep_data:
            pattern_idx = work.get('pattern_idx', 0)
            if pattern_idx == 0:
                main_works.append(work)
            else:
                if pattern_idx not in variants_map:
                    variants_map[pattern_idx] = []
                variants_map[pattern_idx].append(work)
        
        # 构建variants列表
        variants = []
        for idx in sorted(variants_map.keys()):
            if idx < len(patterns):
                variants.append({
                    'name': patterns[idx].get('name', f'变体{idx}'),
                    'works': variants_map[idx]
                })
        
        return jsonify({'success': True, 'data': {
            'name': cipai['name'],
            'main': main_works,
            'variants': variants
        }})
    
    # 数组格式或其他
    return jsonify({'success': True, 'data': {
        'name': cipai['name'],
        'main': [],
        'variants': []
    }})


@app.route('/api/cipai/<int:cipai_id>/representatives/<int:work_index>', methods=['PUT'])
def update_cipai_representative(cipai_id, work_index):
    """更新单个代表作（仅Edu可编辑，支持正体和变体）"""
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
        if not rep_data:
            return jsonify({'success': False, 'message': '代表作数据不存在'}), 404
        
        # 支持两种数据格式：main/variants 或 0索引格式
        is_zero_indexed = 'main' not in rep_data and '0' in rep_data
        
        if is_zero_indexed:
            # 转换0索引格式为main/variants格式
            main_works = rep_data.get('0', [])
            if not isinstance(main_works, list):
                main_works = [main_works]
            
            patterns = cipai.get('patterns', [])
            variants = []
            for i in range(1, len(patterns)):
                pattern_key = str(i)
                if pattern_key in rep_data:
                    pattern_works = rep_data[pattern_key]
                    if not isinstance(pattern_works, list):
                        pattern_works = [pattern_works]
                    variants.append({
                        'name': patterns[i].get('name', f'变体{i}'),
                        'works': pattern_works
                    })
            
            # 创建临时main/variants格式用于编辑
            rep_data = {
                'main': main_works,
                'variants': variants
            }

        # 判断是正体还是变体
        work_type = data.get('type', 'main')
        variant_index = data.get('variant_index', 0)

        # 验证必填字段
        required_fields = ['title', 'author', 'dynasty', 'text']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

        # 根据类型更新对应数据
        if work_type == 'variant':
            # 变体代表作
            variants = rep_data.get('variants', [])
            if variant_index < 0 or variant_index >= len(variants):
                return jsonify({'success': False, 'message': '变体索引无效'}), 400
            variant_works = variants[variant_index].get('works', [])
            if work_index < 0 or work_index >= len(variant_works):
                return jsonify({'success': False, 'message': '作品索引无效'}), 400
            variants[variant_index]['works'][work_index] = {
                'title': data['title'],
                'author': data['author'],
                'dynasty': data['dynasty'],
                'text': data['text'],
                'zi': data.get('zi', ''),
                'hao': data.get('hao', '')
            }
            saved_work = variants[variant_index]['works'][work_index]
        else:
            # 正体代表作
            if work_index < 0 or work_index >= len(rep_data['main']):
                return jsonify({'success': False, 'message': '作品索引无效'}), 400
            rep_data['main'][work_index] = {
                'title': data['title'],
                'author': data['author'],
                'dynasty': data['dynasty'],
                'text': data['text'],
                'zi': data.get('zi', ''),
                'hao': data.get('hao', '')
            }
            saved_work = rep_data['main'][work_index]

        # 保存
        # 如果原始数据是0索引格式，转换回去
        save_data = rep_data
        if is_zero_indexed:
            # 转换main/variants格式回0索引格式
            save_data = {'0': rep_data['main']}
            patterns = cipai.get('patterns', [])
            for i, variant in enumerate(rep_data.get('variants', []), start=1):
                save_data[str(i)] = variant.get('works', [])
        
        if update_rep_works(cipai_id, save_data):
            return jsonify({'success': True, 'message': '保存成功', 'data': saved_work})
        else:
            return jsonify({'success': False, 'message': '保存失败'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500


@app.route('/api/cipai/<int:cipai_id>/representatives', methods=['POST'])
def add_cipai_representative(cipai_id):
    """新增代表作（仅Edu可操作，支持正体和变体）"""
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

        # 判断是正体还是变体
        work_type = data.get('type', 'main')
        variant_index = data.get('variant_index', 0)

        # 验证必填字段
        required_fields = ['title', 'author', 'dynasty', 'text']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400

        # 构建作品数据
        work_data = {
            'title': data['title'],
            'author': data['author'],
            'dynasty': data['dynasty'],
            'text': data['text'],
            'zi': data.get('zi', ''),
            'hao': data.get('hao', '')
        }

        # 添加作品
        if add_rep_work(cipai_id, work_data, work_type, variant_index):
            return jsonify({'success': True, 'message': '新增成功', 'data': work_data})
        else:
            return jsonify({'success': False, 'message': '新增失败'}), 500
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


# ---- 作者简介 ----

@app.route('/api/authors/bios', methods=['GET'])
def all_author_bios():
    """获取所有作者简介"""
    bios = get_all_bios()
    return jsonify({'success': True, 'data': bios})


@app.route('/api/authors/<name>/bio', methods=['GET'])
def author_bio(name):
    """获取指定作者简介"""
    bio = get_author_bio(name)
    if bio:
        return jsonify({'success': True, 'name': name, 'bio': bio})
    return jsonify({'success': False, 'message': '未找到该作者简介'}), 404


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


# ---- 填词辅助 ----

from rhyme_helper import get_char_info, check_pingze, check_rhyme, get_rhyme_chars, get_rhyme_chars_with_base, analyze_sentence_pattern

def get_repr_work_for_pattern(cipai_id, pattern_index):
    """获取指定格律的代表作完整数据（包含text和lineGroups）"""
    # 从representative_works.json加载
    import json
    import os

    repr_path = os.path.join(os.path.dirname(__file__), 'representative_works.json')
    if not os.path.exists(repr_path):
        return None

    with open(repr_path, 'r', encoding='utf-8') as f:
        rep_works = json.load(f)

    # 代表作数据和格律数据使用相同的ID
    cipai_id_str = str(cipai_id)
    pattern_idx_str = str(pattern_index)

    if cipai_id_str in rep_works:
        rep_data = rep_works[cipai_id_str]
        
        # 格式1：main/variants格式（如鹊桥仙）
        if 'main' in rep_data or 'variants' in rep_data:
            work_data = None
            if pattern_index == 0:
                # 正体：从main获取
                main_works = rep_data.get('main', [])
                if main_works:
                    work_data = main_works[0]
            else:
                # 变体：从variants获取
                variants = rep_data.get('variants', [])
                if pattern_index - 1 < len(variants):
                    variant_item = variants[pattern_index - 1]
                    # 兼容两种格式：
                    # 1. 字典格式: {"name": "变体一", "works": [...]}
                    # 2. 列表格式: [{'title': ..., 'text': ...}, ...]
                    if isinstance(variant_item, list):
                        variant_works = variant_item
                    else:
                        variant_works = variant_item.get('works', [])
                    if variant_works:
                        work_data = variant_works[0]
            
            if work_data:
                text = work_data.get('text', '') or work_data.get('content', '')
                lineGroups = work_data.get('lineGroups', None)
                if text:
                    return {
                        'text': text,
                        'lineGroups': lineGroups
                    }
        
        # 格式2：0/1/2索引格式
        elif pattern_idx_str in rep_data:
            work_data = rep_data[pattern_idx_str]

            # 支持多种格式：
            # 1. 数组格式: [{'title': ..., 'text': ..., 'lineGroups': ...}, ...]
            # 2. 对象格式: {'title': ..., 'text': ..., 'lineGroups': ...}
            work_obj = None
            if isinstance(work_data, list) and len(work_data) > 0:
                # 数组格式：取第一个作品
                work_obj = work_data[0]
            elif isinstance(work_data, dict):
                # 对象格式
                work_obj = work_data
            
            if work_obj:
                # 提取text字段（支持text和content两种字段名）
                text = work_obj.get('text', '') or work_obj.get('content', '')
                lineGroups = work_obj.get('lineGroups', None)
                
                if text:
                    return {
                        'text': text,
                        'lineGroups': lineGroups
                    }

    return None

@app.route('/api/cipai/<int:cipai_id>/grid', methods=['GET'])
def get_cipai_grid(cipai_id):
    """获取词牌填词格子（支持选择格律）"""
    from grid_builder import build_grid_from_repr
    
    cipai = get_cipai_by_id(cipai_id)
    if not cipai:
        return jsonify({'success': False, 'message': '词牌不存在'}), 404
    
    # 获取格律参数（默认为第一个，即正体）
    pattern_index = request.args.get('pattern', 0, type=int)
    
    # 获取所有格律
    patterns = cipai.get('patterns', [])
    if not patterns:
        return jsonify({'success': False, 'message': '该词牌暂无格律数据'}), 400
    
    # 验证pattern_index是否有效
    if pattern_index < 0 or pattern_index >= len(patterns):
        return jsonify({'success': False, 'message': '格律索引无效'}), 400
    
    selected_pattern = patterns[pattern_index]
    sentences = selected_pattern.get('sentences', [])
    
    # 如果没有sentences字段，尝试从chars+tone构建
    if not sentences:
        chars_array = selected_pattern.get('chars', [])
        tone_array = selected_pattern.get('tone', [])
        rhyme_positions = selected_pattern.get('rhyme_positions', [])
        
        if chars_array and tone_array:
            # 从chars+tone格式构建sentences
            sentences = []
            for i, (chars_count, tone_list) in enumerate(zip(chars_array, tone_array)):
                # 将tone数组转换为字符串
                tone_str = ''.join(tone_list) if isinstance(tone_list, list) else str(tone_list)
                # 检查是否为韵脚句
                is_rhyme = i in rhyme_positions
                sentences.append({
                    'chars': chars_count,
                    'tone': tone_str,
                    'rhyme': is_rhyme
                })
    
    if not sentences:
        return jsonify({'success': False, 'message': '该词牌正体暂无句子数据'}), 400
    
    # 尝试获取代表作数据
    repr_work = get_repr_work_for_pattern(cipai_id, pattern_index)
    
    # 如果有代表作数据，按代表作分行构建grid
    use_original_linebreaks = False  # 默认使用韵脚分组
    if repr_work:
        repr_text = repr_work['text']
        lineGroups = repr_work.get('lineGroups', None)
        # 使用pattern级别的description（包含该格律的前段X句信息）
        description = selected_pattern.get('description', '') or cipai.get('description', '')
        result = build_grid_from_repr(repr_text, sentences, description, lineGroups)
        if result:
            grid, line_groups, stanza_split, rhyme_positions = result
            # build_grid_from_repr已返回正确的line_groups（基于原文换行符）
        else:
            # 构建失败，使用按原文分行的fallback（保持与formatWorkContent一致）
            use_original_linebreaks = True

    if not repr_work or use_original_linebreaks:
        # 否则使用原来的逻辑（按韵脚分行）
        import re
        # 使用pattern级别的description（包含该格律的前段X句信息），fallback到cipai级别
        description = selected_pattern.get('description', '') or cipai.get('description', '')
        # 优先使用pattern级别的stanza_split（精确匹配sentence拆分）
        stanza_split = selected_pattern.get('stanza_split', None)
        cn_nums = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
                   '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18,'十九':19,'二十':20}

        # 尝试解析前段韵脚数（更准确）
        rhyme_split = None
        m = re.search(r'前段.*?(\d+)[仄平]韵', description)
        if m:
            rhyme_split = int(m.group(1))
        else:
            m = re.search(r'前段.*?([一二三四五六七八九十]+)[仄平]韵', description)
            if m:
                rhyme_split = cn_nums.get(m.group(1))

        # 解析前段句数
        m = re.search(r'前段(\d+)句', description)
        if m:
            stanza_split = int(m.group(1))
        else:
            m = re.search(r'前段([一二三四五六七八九十]+)句', description)
            if m:
                stanza_split = cn_nums.get(m.group(1))
            else:
                # 匹配"前后段各X句"格式
                m = re.search(r'前后段各(\d+)句', description)
                if m:
                    stanza_split = int(m.group(1))
                else:
                    m = re.search(r'前后段各([一二三四五六七八九十]+)句', description)
                    if m:
                        stanza_split = cn_nums.get(m.group(1))

        # 只有在没有成功解析到前段句数时，才使用韵脚位置推算stanza_split
        if not stanza_split and rhyme_split:
            rhyme_sent_indices = [i for i, s in enumerate(sentences) if s.get('rhyme', False)]
            if len(rhyme_sent_indices) >= rhyme_split:
                # 第rhyme_split个韵脚句的索引
                last_rhyme_idx = rhyme_sent_indices[rhyme_split - 1]
                stanza_split = last_rhyme_idx + 1  # 上阕结束于该句

        # 构建填词格子
        grid = []
        char_index = 0
        rhyme_positions = []

        # 如果有repr_work但build_grid_from_repr失败，使用按原文分行的新fallback
        if repr_work and use_original_linebreaks:
            from grid_builder import parse_repr_to_sentences
            repr_text = repr_work['text']
            repr_sentences, repr_line_groups = parse_repr_to_sentences(repr_text)

            # 使用description中的句数来计算stanza_split（而不是按标点分句）
            stanza_split_from_desc = None
            cn_nums_fallback = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
                       '十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18,'十九':19,'二十':20}
            m = re.search(r'前段(\d+)句', description)
            if m:
                stanza_split_from_desc = int(m.group(1))
            else:
                m = re.search(r'前段([一二三四五六七八九十]+)句', description)
                if m:
                    stanza_split_from_desc = cn_nums_fallback.get(m.group(1))
                else:
                    m = re.search(r'前后段各(\d+)句', description)
                    if m:
                        stanza_split_from_desc = int(m.group(1))
                    else:
                        m = re.search(r'前后段各([一二三四五六七八九十]+)句', description)
                        if m:
                            stanza_split_from_desc = cn_nums_fallback.get(m.group(1))

            if stanza_split_from_desc:
                stanza_split = stanza_split_from_desc
            else:
                # 计算stanza_split（按原文的上下阕分隔）
                parts = repr_text.split('\n\n')
                if len(parts) == 2:
                    upper_repr, _ = parse_repr_to_sentences(parts[0])
                    stanza_split = len(upper_repr) if upper_repr else stanza_split
                else:
                    stanza_split = len(repr_sentences) // 2 if repr_sentences else stanza_split
            
            # 使用repr的分行结构构建line_groups（扁平化：每组包含单个句子索引）
            # 这样line_groups反映原文的换行结构，与formatWorkContent一致
            line_groups = []
            for group in repr_line_groups:
                for s_idx in group:
                    line_groups.append([s_idx])
            
            # 构建grid（使用sentences数据）
            punctuation_list = get_punctuation_for_pattern(cipai_id, pattern_index, sentences)
            punct_positions = get_punctuation_positions_for_pattern(cipai_id, pattern_index)
            
            for sent_idx, sent_data in enumerate(sentences):
                sent_tone = sent_data.get('tone', '')
                chars_in_sentence = len(sent_tone) if sent_tone else sent_data.get('chars', 0)
                is_rhyme_sentence = sent_data.get('rhyme', False)
                is_last_sentence = (sent_idx == len(sentences) - 1)
                
                if punctuation_list and sent_idx < len(punctuation_list):
                    punctuation = punctuation_list[sent_idx]
                elif is_last_sentence:
                    punctuation = '。'
                elif is_rhyme_sentence:
                    punctuation = '。'
                else:
                    punctuation = '，'
                
                sentence_grid = {
                    'sentence_index': sent_idx,
                    'char_count': chars_in_sentence,
                    'tone_pattern': sent_tone,
                    'is_rhyme': is_rhyme_sentence,
                    # punctuation置空，标点统一由punctuation_after展示（字下方）
                    'punctuation': '',
                    'chars': []
                }
                
                punctuation_positions = {}
                if punct_positions:
                    for i in range(chars_in_sentence):
                        if (char_index + i) in punct_positions:
                            punctuation_positions[i] = punct_positions[char_index + i]
                
                for i in range(chars_in_sentence):
                    tone_char = sent_tone[i] if i < len(sent_tone) else '中'
                    char_info = {
                        'global_index': char_index,
                        'local_index': i,
                        'expected_tone': tone_char,
                        'is_rhyme': False,
                        'user_char': '',
                        # punctuation_after：字下方的标点，由代表作文本提取
                        'punctuation_after': punctuation_positions.get(i, '')
                    }
                    sentence_grid['chars'].append(char_info)
                    char_index += 1
                
                if is_rhyme_sentence and sentence_grid['chars']:
                    last_char = sentence_grid['chars'][-1]
                    last_char['is_rhyme'] = True
                    rhyme_positions.append(last_char['global_index'])
                
                grid.append(sentence_grid)
        else:
            # 尝试从代表作中提取标点符号
            punctuation_list = get_punctuation_for_pattern(cipai_id, pattern_index, sentences)
            
            # 尝试从代表作中提取子句断句信息
            sub_sentences_list = get_sub_sentences_for_pattern(cipai_id, pattern_index, sentences)
            
            # 新方法：获取标点位置（按全局字符位置）
            punct_positions = get_punctuation_positions_for_pattern(cipai_id, pattern_index)

            # 按韵脚分行：将连续的非韵脚句与紧接的韵脚句合并为一行
            line_groups = []  # 每个元素是 [句索引列表]
            current_line = []
            
            # 记录全局字符位置（用于标点位置查询）
            global_char_pos = 0

            for sent_idx, sent_data in enumerate(sentences):
                # sent_data: {'chars': 7, 'rhyme': True, 'tone': '中平中仄中平平', ...}
                sent_tone = sent_data.get('tone', '')
                # 使用tone字段的实际长度，而不是chars字段
                chars_in_sentence = len(sent_tone) if sent_tone else sent_data.get('chars', 0)
                is_rhyme_sentence = sent_data.get('rhyme', False)

                # 确定标点符号
                is_last_sentence = (sent_idx == len(sentences) - 1)
                
                # 优先使用从代表作中提取的标点
                if punctuation_list and sent_idx < len(punctuation_list):
                    punctuation = punctuation_list[sent_idx]
                elif is_last_sentence:
                    punctuation = '。'
                elif is_rhyme_sentence:
                    punctuation = '。'
                else:
                    punctuation = '，'

                sentence_grid = {
                    'sentence_index': sent_idx,
                    'char_count': chars_in_sentence,
                    'tone_pattern': sent_tone,
                    'is_rhyme': is_rhyme_sentence,
                    # punctuation置空，标点统一由punctuation_after展示（字下方）
                    'punctuation': '',
                    'chars': []
                }

                # 获取该句的子句断句信息（旧方法，仅用于按句号分句的格律数据）
                sub_sentences = None
                if sub_sentences_list and sent_idx < len(sub_sentences_list):
                    sub_sentences = sub_sentences_list[sent_idx]
                
                # 计算每个字后面是否需要标点
                punctuation_positions = {}  # {字符位置: 标点符号}
                
                # 优先使用新方法（按全局字符位置）
                if punct_positions:
                    for i in range(chars_in_sentence):
                        if (global_char_pos + i) in punct_positions:
                            punctuation_positions[i] = punct_positions[global_char_pos + i]
                # 如果新方法没有标点，尝试旧方法
                elif sub_sentences:
                    pos = 0
                    for sub in sub_sentences:
                        sub_chars = sub['chars']
                        sub_punct = sub['punctuation']
                        # 这个子句的最后一个字后面有标点
                        punctuation_positions[pos + sub_chars - 1] = sub_punct
                        pos += sub_chars

                # 为每个字创建格子
                for i in range(chars_in_sentence):
                    tone_char = sent_tone[i] if i < len(sent_tone) else '中'
                    char_info = {
                        'global_index': char_index,
                        'local_index': i,
                        'expected_tone': tone_char,
                        'is_rhyme': False,  # 只有句末才标记韵脚
                        'user_char': '',
                        # punctuation_after：字下方的标点，由代表作文本提取
                        'punctuation_after': punctuation_positions.get(i, '')
                    }
                    sentence_grid['chars'].append(char_info)
                    char_index += 1
                    global_char_pos += 1

                # 标记韵脚：如果是韵脚句，标记最后一个字为韵脚
                if is_rhyme_sentence and sentence_grid['chars']:
                    last_char = sentence_grid['chars'][-1]
                    last_char['is_rhyme'] = True
                    rhyme_positions.append(last_char['global_index'])

                grid.append(sentence_grid)

                # 构建分行信息
                current_line.append(sent_idx)
                if is_rhyme_sentence or is_last_sentence:
                    line_groups.append(current_line)
                    current_line = []

            # 如果还有未闭合的行（最后一句不是韵脚的情况）
            if current_line:
                line_groups.append(current_line)
    

    # 计算韵组分组：按 rhyme_type 连续相同分组
    rhyme_groups = []  # [{index, type, positions}]
    current_rhyme_type = None
    current_group_index = -1
    for sent_idx, sent_data in enumerate(sentences):
        if not sent_data.get('rhyme', False):
            continue
        rt = sent_data.get('rhyme_type', '平')
        if rt != current_rhyme_type:
            current_rhyme_type = rt
            current_group_index += 1
            rhyme_groups.append({
                'index': current_group_index,
                'type': rt,
                'positions': []
            })
        # 找到该句在grid中的韵脚char的global_index
        if sent_idx < len(grid):
            for ch in grid[sent_idx]['chars']:
                if ch.get('is_rhyme'):
                    rhyme_groups[current_group_index]['positions'].append(ch['global_index'])
                    break
    
    # 为grid中每个韵脚char添加rhyme_group_index
    rhyme_pos_to_group = {}
    for rg in rhyme_groups:
        for pos in rg['positions']:
            rhyme_pos_to_group[pos] = rg['index']
    for sentence in grid:
        for ch in sentence['chars']:
            if ch.get('is_rhyme') and ch['global_index'] in rhyme_pos_to_group:
                ch['rhyme_group_index'] = rhyme_pos_to_group[ch['global_index']]

    # 计算韵格类型
    # 优先使用pattern级别的stanza_split（精确匹配sentence拆分）
    rs_stanza_split = selected_pattern.get('stanza_split', stanza_split)
    rs_description = selected_pattern.get('description', '') or cipai.get('description', '')
    rhyme_scheme_info = get_rhyme_scheme_info(selected_pattern, rs_stanza_split, rs_description)

    return jsonify({
        'success': True,
        'data': {
            'cipai_name': cipai['name'],
            'cipai_id': cipai_id,
            'pattern_name': selected_pattern.get('name', f'格律{pattern_index + 1}'),
            'pattern_index': pattern_index,
            'total_patterns': len(patterns),  # 总格律数量
            'total_chars': selected_pattern.get('total_chars', 0),
            'sentence_count': len(sentences),
            'grid': grid,
            'rhyme_positions': rhyme_positions,
            'rhyme_groups': rhyme_groups,  # 韵组分组 [{index, type, positions}]
            'rhyme_scheme': rhyme_scheme_info,  # 韵格分类信息
            'stanza_split': stanza_split,  # 上阕句数（None表示无法解析）
            'line_groups': line_groups  # 按韵脚分行的分组，每组是句子索引数组
        }
    })


@app.route('/api/check/char', methods=['POST'])
@login_required
def check_char():
    """检查单个字的平仄和韵脚"""
    data = request.get_json(silent=True) or {}
    char = data.get('char', '')
    expected_tone = data.get('expected_tone', '中')
    rhyme_base_char = data.get('rhyme_base_char')  # 基准韵脚字（可选）
    
    if not char or len(char) != 1:
        return jsonify({'success': False, 'message': '请提供单个汉字'}), 400
    
    # 获取字符信息
    info = get_char_info(char)
    if not info:
        return jsonify({'success': False, 'message': '无法识别该字'}), 400
    
    # 检查平仄
    pingze_result = check_pingze(char, expected_tone)
    
    # 检查韵脚（如果提供了基准字）
    rhyme_result = None
    if rhyme_base_char:
        rhyme_result = check_rhyme(char, rhyme_base_char)
    
    return jsonify({
        'success': True,
        'data': {
            'char': char,
            'pinyin': info['pinyin'],
            'tone': info['tone'],
            'is_ping': info['is_ping'],
            'actual_tone': '平' if info['is_ping'] else '仄',
            'expected_tone': expected_tone,
            'pingze_match': pingze_result['match'],
            'rhyme_check': rhyme_result
        }
    })


@app.route('/api/rhyme/chars', methods=['GET'])
@login_required
def get_rhyme_char_list():
    """获取同韵字列表"""
    char = request.args.get('char', '')
    limit = request.args.get('limit', 50, type=int)
    
    if not char:
        return jsonify({'success': False, 'message': '请提供基准字'}), 400
    
    chars = get_rhyme_chars(char, limit)
    
    return jsonify({
        'success': True,
        'data': {
            'base_char': char,
            'rhyme_chars': chars
        }
    })


@app.route('/api/rhyme/yunbu', methods=['GET'])
def get_char_yunbu_info():
    """查询字所属的平水韵韵部"""
    char = request.args.get('char', '')
    
    if not char or len(char) != 1:
        return jsonify({'success': False, 'message': '请提供单个汉字'}), 400
    
    yunbus = get_char_yunbu(char)
    
    if not yunbus:
        # 平水韵数据库未收录，降级使用简化韵组提供同韵字
        from rhyme_helper import get_char_info as _get_char_info, get_rhyme_chars_with_base
        char_info = _get_char_info(char)
        rhyme_chars = []
        rhyme_group_label = ''
        if char_info and char_info.get('rhyme_group'):
            rhyme_chars = get_rhyme_chars_with_base(char, limit=50)
            pingze = '平' if char_info.get('is_ping') else '仄'
            rhyme_group_label = f"简化韵组 [{char_info['rhyme_group']}]（{pingze}声）"
        
        if rhyme_chars:
            return jsonify({
                'success': True,
                'data': {
                    'char': char,
                    'yunbus': [],
                    'main_yunbu': None,
                    'yunbu_chars': rhyme_chars,
                    'rhyme_group_label': rhyme_group_label,
                    'fallback': True
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'char': char,
                    'yunbus': [],
                    'message': '该字不在平水韵数据库中'
                }
            })
    
    # 获取通用韵组的所有字（合并所有通用韵部）
    yunbu_chars = []
    compat_yunbus = []
    if yunbus:
        # 获取主韵部的通用韵组
        compat_yunbus = get_compatible_yunbus(yunbus[0])
        yunbu_chars = get_all_compatible_chars(yunbus[0])
    
    return jsonify({
        'success': True,
        'data': {
            'char': char,
            'yunbus': yunbus,
            'main_yunbu': yunbus[0] if yunbus else None,
            'compat_yunbus': compat_yunbus,
            'yunbu_chars': yunbu_chars
        }
    })


@app.route('/api/rhyme/check-conflict', methods=['POST'])
@login_required
def check_rhyme_conflict():
    """检查多个韵脚字是否存在韵部冲突"""
    data = request.get_json()
    chars = data.get('chars', [])
    
    if not chars or len(chars) < 2:
        return jsonify({
            'success': True,
            'data': {
                'has_conflict': False,
                'message': '韵脚字数量不足，无法检测冲突'
            }
        })
    
    result = check_yunbu_conflict(chars)
    
    return jsonify({
        'success': True,
        'data': result
    })


# ===== 初始化数据库 =====
try:
    with app.app_context():
        db.create_all()
        print("数据库初始化完成")
except Exception as e:
    print(f"数据库初始化跳过（可能在只读文件系统上）: {e}")


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
