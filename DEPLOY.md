# 词韵 - 免费部署指南

词韵是一个 Python Flask 应用，使用 SQLite 数据库。以下是推荐的免费部署方案。

---

## 方案一：Railway（⭐ 最推荐）

Railway 提供 $5/月的免费额度，足够个人小站使用。最重要的是 **支持持久化磁盘**，SQLite 数据库可以直接使用，无需修改代码。

### 部署步骤

**Step 1：准备代码**

确保 `ci-scoring` 目录结构如下：

```
ci-scoring/
├── backend/
│   ├── app.py
│   ├── cipai_data.py
│   ├── rhythm_analyzer.py
│   ├── llm_scorer.py
│   ├── representative_works.py
│   ├── representative_works.json
│   └── ... (其他 .py 文件)
├── frontend/
│   ├── index.html
│   └── static/
├── wsgi.py           ← 新建
├── requirements.txt  ← 新建
└── railway.toml      ← 新建
```

**Step 2：推送到 GitHub**

```bash
cd d:\MyClaw\ci-scoring

git init
git add .
git commit -m "Initial commit: 词韵 v1.0"

# 在 GitHub 创建新仓库（如 ciyun-app），然后：
git remote add origin https://github.com/你的用户名/ciyun-app.git
git branch -M main
git push -u origin main
```

**Step 3：在 Railway 部署**

1. 访问 [railway.app](https://railway.app)，用 GitHub 账号登录
2. 点击 **New Project** → **Deploy from GitHub repo**
3. 选择 `ciyun-app` 仓库
4. Railway 会自动检测 Python 并部署

**Step 4：配置环境变量（重要！）**

在 Railway 项目的 **Variables** 中添加：

```
FLASK_ENV = production
PORT = 8000
SECRET_KEY = 随机字符串（用 python -c "import secrets; print(secrets.token_hex(32))" 生成）
```

**Step 5：配置持久化磁盘（SQLite 必须）**

Railway 的文件系统在重启后会清空，必须为 SQLite 数据库创建持久化卷：

1. 在 Railway 项目页面 → **Add a Disk**
2. 名称填 `data`，挂载到 `/var/data`
3. 在环境变量中添加：

```
DB_PATH = /var/data/ci_scoring.db
```

4. （可选）如果 SQLite 无法在磁盘上工作，改用 SQLite 内存模式（仅测试用）：

```
SQLITE_MEMORY = true
```

### Railway 部署检查清单

- ✅ `FLASK_ENV = production`（关闭 debug）
- ✅ `PORT = 8000`（Railway 要求）
- ✅ `SECRET_KEY` 设置了随机值
- ✅ SQLite 数据库路径指向持久化磁盘
- ✅ `requirements.txt` 包含 `gunicorn`
- ✅ Railway 会自动运行 `gunicorn wsgi:app`

---

## 方案二：Render

Render 免费额度：每月 750 小时，超时会休眠。不支持持久化磁盘，**SQLite 重启后会丢失用户数据**。适合无状态展示类应用。

### 部署步骤

**Step 1：推送代码到 GitHub（同上）**

**Step 2：在 Render 创建 Web Service**

1. 访问 [render.com](https://render.com)，用 GitHub 登录
2. 点击 **New** → **Web Service**
3. 选择 GitHub 仓库 `ciyun-app`
4. 设置：
   - **Name**: `ciyun`
   - **Region**: Singapore（离中国大陆近）
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free

5. 点击 **Create Web Service**，等待部署完成

**Step 3：配置环境变量**

在 Render Dashboard → Your Web Service → **Environment** 中添加：

```
FLASK_ENV = production
SECRET_KEY = 随机字符串
```

**⚠️ Render 免费版限制：**
- 实例休眠：15分钟无流量后休眠，冷启动慢
- 无持久化磁盘：SQLite 数据库在休眠后丢失（用户注册记录消失）
- 无 HTTPS 自定义域名（需要付费版）

### 解决方案：改用 PostgreSQL（免费）

Render 提供免费 PostgreSQL：

1. **New** → **PostgreSQL**，创建数据库
2. 在 PostgreSQL 页面的 **Connection Info** 中找到 `DATABASE_URL`
3. 在 Web Service 环境变量中添加：

```
DATABASE_URL = postgresql://用户名:密码@主机:端口/数据库名
```

4. 修改 `app.py` 中的数据库连接：

```python
import os
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres'):
    # Render PostgreSQL 需要这个兼容处理
    db_url = db_url.replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    db_path = os.environ.get('DB_PATH', os.path.join(BASE_DIR, 'ci_scoring.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
```

5. `requirements.txt` 中添加：`psycopg2-binary==2.9.10`

---

## 方案三：PythonAnywhere

专门为 Python Web 应用设计的托管平台，免费版受限制但对 Flask 支持好。

### 限制
- 免费版只能用 `yourusername.pythonanywhere.com` 域名
- 只支持 Python 3.x
- 不支持后台进程（但 Flask 本身是 Web 服务，不需要额外后台进程）

### 部署步骤

**Step 1：上传代码到 PythonAnywhere**

有两种方式：

**方式 A：直接从 GitHub 拉取（推荐）**

1. 注册 [PythonAnywhere](https://www.pythonanywhere.com)
2. 打开 **Bash** 终端：
```bash
cd ~
git clone https://github.com/你的用户名/ciyun-app.git
```

**方式 B：手动上传**

1. 在 PythonAnywhere 的 **Files** 页面直接上传 `ci-scoring` 文件夹

**Step 2：创建虚拟环境**

```bash
cd ~/ciyun-app
python -m venv venv
source venv/bin/activate  # 或在 PythonAnywhere bash 中运行
pip install -r requirements.txt
```

**Step 3：配置 Web App**

1. 进入 **Web** 页面
2. 点击 **Add a new web app**
3. 选择 **Manual configuration**
4. 选择 **Python 3.13**
5. 在 WSGI configuration file 点击链接，编辑 `mysite_wsgi.py`：

```python
import sys
path = '/home/你的用户名/ciyun-app'
if path not in sys.path:
    sys.path.insert(0, path)

from backend.app import app as application
```

6. 配置静态文件：
   - URL: `/static/`
   - Directory: `/home/你的用户名/ciyun-app/frontend/static/`

7. 设置环境变量（可选）：
   ```
   FLASK_ENV = production
   SECRET_KEY = 你的随机密钥
   ```

**Step 4：重载 Web App**

点击 **Reload** 按钮，访问 `https://你的用户名.pythonanywhere.com`

---

## 方案四：Fly.io

性能好，支持持久化磁盘，但配置相对复杂。

### 部署步骤

**Step 1：安装 flyctl**

Windows PowerShell:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Step 2：在项目目录初始化**

```bash
cd d:\MyClaw\ci-scoring
fly launch
```

创建 `Dockerfile`（flyctl 会自动生成，也可以手动创建）：

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .
EXPOSE 8000

ENV FLASK_ENV=production
ENV PORT=8000

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
```

**Step 3：创建持久化卷（用于 SQLite）**

```bash
fly volumes create data --size 1
```

**Step 4：编辑 `fly.toml`**

```toml
app = "ciyun"
primary_region = "hkg"  # 香港

[build]

[deploy]
  release_command = ""

[env]
  PORT = "8000"
  FLASK_ENV = "production"

[[services]]
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[[volumes]]
  source = "data"
  destination = "/var/data"

[processes]
  app = "gunicorn wsgi:app --bind 0.0.0.0:8000"
```

**Step 5：部署**

```bash
fly deploy
fly ssh console  # 首次部署后，创建数据目录
mkdir -p /var/data
```

---

## 部署后检查清单

### 功能验证

1. ✅ 访问首页是否正常显示
2. ✅ 注册/登录功能是否正常
3. ✅ 词牌列表是否显示（100个词牌）
4. ✅ 评分功能是否正常（需要配置 AI API Key）
5. ✅ 历史记录是否保存

### 安全检查

1. ✅ `FLASK_ENV = production`（debug=False）
2. ✅ `SECRET_KEY` 设置为随机值（不是默认值）
3. ✅ 没有暴露 `.git` 目录（GitHub 仓库设为 private）
4. ✅ `debug=True` 代码已从 `app.py` 移除

### AI 评分功能

词韵的 AI 评分依赖大模型 API（默认百度千帆）。部署后：
1. 在前端页面点击 **AI配置**
2. 填入你的 API Key 和模型（如有其他需求可换用 OpenAI 等兼容接口）

---

## 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `FLASK_ENV` | ✅ | 设为 `production` 关闭调试模式 |
| `PORT` | ✅ | Web 服务端口，各平台要求不同 |
| `SECRET_KEY` | ✅ | Session 加密密钥，用随机字符串 |
| `DB_PATH` | SQLite | SQLite 数据库路径，Railway/Fly.io 需指向持久化卷 |
| `DATABASE_URL` | PostgreSQL | PostgreSQL 连接字符串（使用 PostgreSQL 时必填） |
| `LLM_API_KEY` | AI评分 | 大模型 API Key（可选，页面内配置也有效） |
| `LLM_API_URL` | AI评分 | 大模型 API 地址 |
| `LLM_MODEL` | AI评分 | 大模型名称 |
