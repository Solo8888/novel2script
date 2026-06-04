# Novel2Script Backend

小说转剧本工具后端服务。

## 技术栈

- Python 3.12+
- FastAPI
- Uvicorn
- SQLAlchemy (异步)
- PostgreSQL (通过 asyncpg)
- Redis (异步, 通过 hiredis)
- Alembic (数据库迁移)
- Loguru (日志)
- Pydantic Settings (配置管理)
- python-jose (JWT 认证)
- passlib (密码哈希)

## 快速开始

### 1. 创建虚拟环境

```powershell
python -m venv .venv
```

### 2. 激活虚拟环境

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 .env.example 为 .env:
```powershell
copy .env.example .env
```

编辑 .env 文件，填入正确的数据库连接信息等配置。

### 5. 启动服务

开发模式（带热重载）:
```powershell
uvicorn app.main:app --reload
```

生产模式:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. 访问服务

- 健康检查: http://localhost:8000/health
- 数据库连接检查: http://localhost:8000/db-check
- Redis 连接检查: http://localhost:8000/redis-check
- API 文档: http://localhost:8000/docs
- 替代文档: http://localhost:8000/redoc
- 配置调试（仅 DEBUG 模式）: http://localhost:8000/config/debug

## 项目结构

```
backend/
├── alembic/             # Alembic 数据库迁移配置
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py      # 依赖注入（如 get_current_user）
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── auth.py  # 认证路由（登录、受保护测试）
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py    # 应用配置（Pydantic Settings）
│   │   ├── database.py  # 异步数据库连接和会话管理
│   │   ├── redis.py     # 异步 Redis 连接池
│   │   ├── security.py  # JWT 认证和密码工具
│   │   └── logger.py    # 日志系统配置
│   ├── __init__.py
│   └── main.py          # FastAPI 应用入口
├── .env                 # 环境变量（不提交到 git）
├── .env.example         # 环境变量示例
├── .venv/               # 虚拟环境（已添加到 .gitignore）
├── alembic.ini          # Alembic 配置
├── requirements.txt     # 依赖包列表
└── README.md            # 项目说明
```

## API 端点

### GET /health

健康检查端点，返回服务状态。

**响应:**
```json
{
  "status": "ok",
  "app_name": "Novel2Script"
}
```

### GET /db-check

测试数据库连接状态。

**成功响应:**
```json
{
  "database": "connected"
}
```

**失败响应:**
```json
{
  "database": "disconnected",
  "reason": "连接错误信息"
}
```

### GET /redis-check

测试 Redis 连接状态。

**成功响应**：
```json
{
  "redis": "pong"
}
```

**失败响应**：
```json
{
  "redis": "disconnected",
  "reason": "连接错误信息"
}
```

### POST /api/v1/login

用户登录，获取 JWT 访问令牌。

**请求体**：
```json
{
  "username": "admin",
  "password": "secret"
}
```

**成功响应**：
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### GET /api/v1/protected

受保护的测试路由，需要 Bearer token。

**请求头**：
```
Authorization: Bearer <access_token>
```

**成功响应**：
```json
{
  "message": "You are authenticated",
  "user": {"sub": "admin"}
}
```

### GET /config/debug (DEBUG 模式)

查看配置信息（敏感信息已脱敏）。

## 数据库迁移

使用 Alembic 管理数据库迁移:

```powershell
# 生成新迁移
alembic revision --autogenerate -m "描述变更"

# 执行迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```
