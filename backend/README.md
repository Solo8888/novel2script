# Novel2Script Backend

小说转剧本工具后端服务。

## 技术栈

- Python 3.12+
- FastAPI
- Uvicorn

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

### 4. 启动服务

开发模式（带热重载）:
```powershell
uvicorn app.main:app --reload
```

生产模式:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 访问服务

- 健康检查: http://localhost:8000/health
- API 文档: http://localhost:8000/docs
- 替代文档: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI 应用入口
├── .venv/               # 虚拟环境（已添加到 .gitignore）
├── requirements.txt     # 依赖包列表
└── README.md            # 项目说明
```

## API 端点

### GET /health

健康检查端点，返回服务状态。

**响应:**
```json
{
  "status": "ok"
}
```
