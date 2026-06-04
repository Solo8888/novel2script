# AI小说转剧本工具 - API 接口文档

## 文档修订记录

| 版本 | 日期 | 作者 | 修订内容 |
|------|------|------|---------|
| v1.0 | 2026-06-05 | API架构师 | 初始版本，18个核心端点完整定义 |

---

## 1. 概述

### 1.1 基本信息

| 项目 | 说明 |
|------|------|
| 协议 | HTTPS（生产）/ HTTP（开发） |
| 基础路径 | `/api/v1` |
| 数据格式 | JSON（请求/响应），multipart/form-data（文件上传） |
| 字符编码 | UTF-8 |
| 认证方式 | Bearer Token（JWT），通过 `Authorization` 请求头传递 |
| 时间格式 | ISO 8601 UTC（`2026-06-05T10:30:00Z`） |

### 1.2 通用规范

#### 请求头

```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

#### 通用响应结构

**成功响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

**分页响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

**错误响应**：

```json
{
  "code": 400,
  "message": "参数校验失败",
  "detail": "小说至少需要包含3个章节，当前检测到2章",
  "errors": [
    {
      "field": "file",
      "reason": "chapter_count_too_few",
      "message": "小说至少需要包含3个章节"
    }
  ]
}
```

#### HTTP 状态码一览

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功，返回数据 |
| 201 | Created | 资源创建成功 |
| 202 | Accepted | 异步任务已接受 |
| 204 | No Content | 删除成功，无响应体 |
| 400 | Bad Request | 请求参数校验失败 |
| 401 | Unauthorized | 未认证或 Token 过期 |
| 403 | Forbidden | 无权限访问该资源 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如重复操作） |
| 413 | Payload Too Large | 上传文件超过大小限制 |
| 415 | Unsupported Media Type | 不支持的文件格式 |
| 422 | Unprocessable Entity | 请求体格式正确但语义错误 |
| 429 | Too Many Requests | 请求频率超限 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务暂不可用（如 LLM API 不可达） |

#### 业务错误码

| 错误码 | 含义 |
|--------|------|
| `AUTH_INVALID_CREDENTIALS` | 邮箱或密码错误 |
| `AUTH_EMAIL_EXISTS` | 邮箱已被注册 |
| `AUTH_TOKEN_EXPIRED` | Token 已过期 |
| `AUTH_TOKEN_BLACKLISTED` | Token 已被登出失效 |
| `AUTH_ACCOUNT_LOCKED` | 账户已锁定，请稍后重试 |
| `VALIDATION_ERROR` | 参数校验失败 |
| `FILE_TOO_LARGE` | 文件大小超过限制 |
| `FILE_FORMAT_UNSUPPORTED` | 文件格式不支持 |
| `FILE_CHAPTER_TOO_FEW` | 章节数不足 |
| `PROJECT_NOT_FOUND` | 项目不存在 |
| `PROJECT_NOT_OWNED` | 无权访问该项目 |
| `PROJECT_STATUS_INVALID` | 项目当前状态不允许此操作 |
| `CONVERSION_ALREADY_RUNNING` | 转换任务已在运行中 |
| `CONVERSION_FAILED` | 转换任务失败 |
| `SCRIPT_SCHEMA_INVALID` | 剧本 YAML 结构不符合 Schema |
| `LLM_SERVICE_UNAVAILABLE` | LLM 服务暂不可用 |
| `QUOTA_EXCEEDED` | 超出转换字数配额 |
| `RATE_LIMITED` | 请求频率超限 |

---

## 2. 认证接口

### 2.1 用户注册

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/auth/register` |
| **认证** | 否 |
| **描述** | 使用邮箱和密码注册新账号 |

**请求体**：

```json
{
  "email": "user@example.com",
  "password": "Abc12345!",
  "display_name": "张三"
}
```

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `email` | string | 是 | 合法邮箱格式，最长 255 字符 |
| `password` | string | 是 | 8-64 字符，至少含 1 个字母和 1 个数字 |
| `display_name` | string | 是 | 1-100 字符 |

**成功响应（201）**：

```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "id": "a1b2c3d4e5f6789012345678abcdef00",
    "email": "user@example.com",
    "display_name": "张三",
    "created_at": "2026-06-05T10:00:00Z"
  }
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | 请求参数格式错误 |
| 409 | `AUTH_EMAIL_EXISTS` | 该邮箱已被注册 |
| 422 | `VALIDATION_ERROR` | 密码强度不足 |

---

### 2.2 用户登录

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/auth/login` |
| **认证** | 否 |
| **描述** | 邮箱+密码登录，返回 JWT Token 对 |

**请求体**（`application/x-www-form-urlencoded`）：

```
username=user@example.com&password=Abc12345!
```

> 注：遵循 OAuth2 密码模式规范，使用 `application/x-www-form-urlencoded` 格式

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `username` | string | 是 | 注册邮箱 |
| `password` | string | 是 | 明文密码 |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "a1b2c3d4e5f6789012345678abcdef00",
      "email": "user@example.com",
      "display_name": "张三"
    }
  }
}
```

| 字段 | 说明 |
|------|------|
| `access_token` | 访问令牌，后续请求通过 `Authorization: Bearer xxx` 携带 |
| `refresh_token` | 刷新令牌，用于续期 access_token |
| `token_type` | 固定值 `bearer` |
| `expires_in` | access_token 有效期（秒），默认 86400（24小时） |

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | 缺少必填字段 |
| 401 | `AUTH_INVALID_CREDENTIALS` | 邮箱或密码错误 |
| 423 | `AUTH_ACCOUNT_LOCKED` | 连续 5 次错误，账户锁定 15 分钟 |

---

### 2.3 用户登出

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/auth/logout` |
| **认证** | 是 |
| **描述** | 将当前 Token 加入 Redis 黑名单，立即失效 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | `AUTH_TOKEN_EXPIRED` | Token 已过期 |

---

### 2.4 刷新 Token

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/auth/refresh` |
| **认证** | 否（使用 refresh_token） |
| **描述** | 使用 refresh_token 获取新的 access_token |

**请求体**：

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "Token 刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

---

## 3. 用户信息接口

### 3.1 获取当前用户信息

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/users/me` |
| **认证** | 是 |
| **描述** | 获取当前登录用户的详细信息与配额 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "a1b2c3d4e5f6789012345678abcdef00",
    "email": "user@example.com",
    "display_name": "张三",
    "quota": {
      "daily_used": 120000,
      "daily_limit": 500000,
      "monthly_used": 1200000,
      "monthly_limit": 10000000
    },
    "created_at": "2026-06-01T08:00:00Z"
  }
}
```

### 3.2 更新用户信息

| 属性 | 内容 |
|------|------|
| **端点** | `PATCH /api/v1/users/me` |
| **认证** | 是 |
| **描述** | 更新当前用户信息（如显示名称） |

**请求体**：

```json
{
  "display_name": "张三（编剧）"
}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "a1b2c3d4e5f6789012345678abcdef00",
    "display_name": "张三（编剧）"
  }
}
```

---

## 4. 项目管理接口

### 4.1 创建项目（上传小说）

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/projects` |
| **认证** | 是 |
| **Content-Type** | `multipart/form-data` |
| **描述** | 上传小说文件并创建项目，自动解析章节 |

**请求头**：

```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求体（multipart/form-data）**：

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `file` | file | 是 | `.txt` 或 `.md`，UTF-8 编码，单文件上限 50 万字（约 1.5 MB） |
| `title` | string | 是 | 项目名称，1-200 字符 |
| `novel_title` | string | 否 | 原小说标题，不填则从文件名推断 |
| `novel_author` | string | 否 | 原小说作者 |

**cURL 示例**：

```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/novel.txt" \
  -F "title=我的剧本项目" \
  -F "novel_title=原小说名" \
  -F "novel_author=原作者"
```

**成功响应（201）**：

```json
{
  "code": 201,
  "message": "项目创建成功",
  "data": {
    "project": {
      "id": "b2c3d4e5f6789012345678abcdef0011",
      "title": "我的剧本项目",
      "novel_title": "原小说名",
      "novel_author": "原作者",
      "file_id": "novels/2026/06/05/b2c3d4e5f6_abc123.txt",
      "file_size_bytes": 204800,
      "status": "draft",
      "created_at": "2026-06-05T10:00:00Z"
    },
    "chapters": [
      {
        "id": "c3d4e5f6789012345678abcdef001122",
        "title": "第一章 大梦初醒",
        "chapter_index": 1,
        "char_count": 4520,
        "status": "pending"
      },
      {
        "id": "d4e5f6789012345678abcdef00112233",
        "title": "第二章 初入江湖",
        "chapter_index": 2,
        "char_count": 3800,
        "status": "pending"
      }
    ],
    "total_chapters": 12
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `project.id` | string | UUID 32位十六进制 |
| `project.title` | string | 项目名称 |
| `project.novel_title` | string | 原小说标题 |
| `project.novel_author` | string | 原小说作者 |
| `project.file_id` | string | 上传文件的存储路径（MinIO 对象名或本地路径） |
| `project.file_size_bytes` | int | 上传文件大小（字节） |
| `project.status` | string | 项目状态：`draft` / `parsing` / `converting` / `completed` / `failed` |
| `chapters[].id` | string | 章节 ID |
| `chapters[].title` | string | 章节标题 |
| `chapters[].chapter_index` | int | 章节序号 |
| `chapters[].char_count` | int | 字符数 |
| `chapters[].status` | string | 章节状态：`pending` |
| `total_chapters` | int | 总章节数 |

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | 缺少必填字段 |
| 401 | `AUTH_TOKEN_EXPIRED` | Token 过期 |
| 413 | `FILE_TOO_LARGE` | 文件超过 50 万字限制 |
| 415 | `FILE_FORMAT_UNSUPPORTED` | 不支持的文件格式（非 .txt/.md） |
| 422 | `FILE_CHAPTER_TOO_FEW` | 检测到的章节数 < 3 |

---

### 4.2 获取项目列表

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/projects` |
| **认证** | 是 |
| **描述** | 分页获取当前用户的项目列表，支持搜索和排序 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `page_size` | int | 否 | 10 | 每页条数，范围 1-50 |
| `search` | string | 否 | - | 按项目名称模糊搜索 |
| `status` | string | 否 | - | 按状态筛选：`draft` / `converting` / `completed` / `failed` |
| `sort_by` | string | 否 | `updated_at` | 排序字段：`created_at` / `updated_at` |
| `sort_order` | string | 否 | `desc` | 排序方向：`asc` / `desc` |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "b2c3d4e5f6789012345678abcdef0011",
        "title": "三体-电视剧改编",
        "script_type": null,
        "status": "draft",
        "novel_title": "三体",
        "total_chapters": 36,
        "completed_chapters": 0,
        "progress": 0,
        "created_at": "2026-06-05T10:00:00Z",
        "updated_at": "2026-06-05T10:00:00Z"
      },
      {
        "id": "c3d4e5f6789012345678abcdef0022",
        "title": "流浪地球-电影版",
        "script_type": "movie",
        "status": "completed",
        "novel_title": "流浪地球",
        "total_chapters": 8,
        "completed_chapters": 8,
        "progress": 100,
        "created_at": "2026-06-01T08:30:00Z",
        "updated_at": "2026-06-04T14:22:00Z"
      }
    ],
    "total": 15,
    "page": 1,
    "page_size": 10,
    "total_pages": 2
  }
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | `AUTH_TOKEN_EXPIRED` | Token 过期 |

---

### 4.3 获取项目详情

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/projects/{id}` |
| **认证** | 是 |
| **描述** | 获取项目完整信息，包括章节列表和转换任务状态 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 项目 ID（32位 UUID） |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "b2c3d4e5f6789012345678abcdef0011",
    "title": "三体-电视剧改编",
    "script_type": "tv_series",
    "script_config": {
      "episode_count": 30
    },
    "status": "converting",
    "novel_title": "三体",
    "novel_author": "刘慈欣",
    "file_id": "novels/2026/06/05/b2c3d4e5f6_abc123.txt",
    "file_size_bytes": 204800,
    "total_chapters": 36,
    "completed_chapters": 12,
    "progress": 35,
    "error_message": null,
    "created_at": "2026-06-05T10:00:00Z",
    "updated_at": "2026-06-05T10:15:30Z",
    "chapters": [
      {
        "id": "d4e5f6789012345678abcdef00112233",
        "title": "第一章 疯狂年代",
        "chapter_index": 1,
        "char_count": 4520,
        "token_count": 5800,
        "status": "completed"
      },
      {
        "id": "e5f6789012345678abcdef0011223344",
        "title": "第二章 寂静的春天",
        "chapter_index": 2,
        "char_count": 5100,
        "token_count": 6500,
        "status": "completed"
      },
      {
        "id": "f6789012345678abcdef001122334455",
        "title": "第三章 红岸基地",
        "chapter_index": 3,
        "char_count": 4800,
        "token_count": 6100,
        "status": "converting"
      }
    ],
    "conversion_tasks": [
      {
        "id": "task_001",
        "chapter_id": "d4e5f6789012345678abcdef00112233",
        "chapter_index": 1,
        "status": "success",
        "duration_ms": 18500,
        "started_at": "2026-06-05T10:01:00Z",
        "completed_at": "2026-06-05T10:01:18Z"
      },
      {
        "id": "task_002",
        "chapter_id": "e5f6789012345678abcdef0011223344",
        "chapter_index": 2,
        "status": "success",
        "duration_ms": 22300,
        "started_at": "2026-06-05T10:01:20Z",
        "completed_at": "2026-06-05T10:01:42Z"
      },
      {
        "id": "task_003",
        "chapter_id": "f6789012345678abcdef001122334455",
        "chapter_index": 3,
        "status": "started",
        "duration_ms": null,
        "started_at": "2026-06-05T10:01:45Z",
        "completed_at": null
      }
    ]
  }
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | `AUTH_TOKEN_EXPIRED` | Token 过期 |
| 403 | `PROJECT_NOT_OWNED` | 项目不属于当前用户 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在 |

---

### 4.4 更新项目配置

| 属性 | 内容 |
|------|------|
| **端点** | `PATCH /api/v1/projects/{id}` |
| **认证** | 是 |
| **描述** | 更新项目标题、剧本类型配置等 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**请求体**：

```json
{
  "title": "三体-电视剧改编 v2",
  "script_type": "tv_series",
  "script_config": {
    "episode_count": 30
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 否 | 项目名称 |
| `script_type` | string | 否 | `movie` / `tv_series` / `mini_series` |
| `script_config` | object | 否 | 剧本类型配置，`tv_series` 时需 `episode_count` |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": "b2c3d4e5f6789012345678abcdef0011",
    "title": "三体-电视剧改编 v2",
    "script_type": "tv_series",
    "script_config": {
      "episode_count": 30
    },
    "updated_at": "2026-06-05T10:30:00Z"
  }
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | 参数校验失败 |
| 403 | `PROJECT_NOT_OWNED` | 无权限 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在 |
| 409 | `PROJECT_STATUS_INVALID` | 项目正在转换中，不允许修改 |

---

### 4.5 删除项目

| 属性 | 内容 |
|------|------|
| **端点** | `DELETE /api/v1/projects/{id}` |
| **认证** | 是 |
| **描述** | 删除项目及关联的所有数据（章节、任务、剧本片段、文件）。此操作不可逆。 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 项目 ID（32位 UUID） |

**成功响应（204 No Content）**：

无响应体。HTTP 状态码 `204` 表示删除成功。

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | `AUTH_TOKEN_EXPIRED` | Token 过期 |
| 403 | `PROJECT_NOT_OWNED` | 无权限 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在 |
| 409 | `PROJECT_STATUS_INVALID` | 项目正在转换中，不允许删除 |

---

## 5. 转换接口

### 5.1 启动 AI 转换

| 属性 | 内容 |
|------|------|
| **端点** | `POST /api/v1/projects/{id}/convert` |
| **认证** | 是 |
| **描述** | 启动异步 AI 转换任务，将小说章节逐一转换为剧本 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 项目 ID |

**请求体**：

```json
{
  "script_type": "tv_series",
  "script_config": {
    "episode_count": 30
  },
  "llm_model": "deepseek-chat"
}
```

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `script_type` | string | 是 | `movie` / `tv_series` / `mini_series` |
| `script_config` | object | 条件 | `tv_series` 时需包含 `episode_count`（10-60） |
| `llm_model` | string | 否 | 默认 `deepseek-chat`，可选 `deepseek-r1-0528` |

**成功响应（202）**：

```json
{
  "code": 202,
  "message": "转换任务已启动",
  "data": {
    "project_id": "b2c3d4e5f6789012345678abcdef0011",
    "status": "converting",
    "total_chapters": 36,
    "ws_progress_url": "/ws/projects/b2c3d4e5f6789012345678abcdef0011/progress?token={jwt_token}",
    "started_at": "2026-06-05T10:30:00Z"
  }
}
```

> 转换启动后，前端应通过 WebSocket 连接 `ws_progress_url` 获取实时进度更新。

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | `script_type` 非法或 `script_config` 缺失 |
| 401 | `AUTH_TOKEN_EXPIRED` | Token 过期 |
| 403 | `PROJECT_NOT_OWNED` | 无权限 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在 |
| 409 | `CONVERSION_ALREADY_RUNNING` | 转换任务已在运行中 |
| 422 | `PROJECT_STATUS_INVALID` | 项目状态不允许转换（如章节未解析） |
| 429 | `QUOTA_EXCEEDED` | 超出每日/每月转换字数配额 |
| 503 | `LLM_SERVICE_UNAVAILABLE` | LLM 服务暂不可用 |

---

## 6. 章节接口

### 6.1 获取章节列表

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/projects/{id}/chapters` |
| **认证** | 是 |
| **描述** | 获取项目的章节列表（含转换状态） |

**请求头**：

```
Authorization: Bearer {access_token}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "chapters": [
      {
        "id": "d4e5f6789012345678abcdef00112233",
        "title": "第一章 疯狂年代",
        "chapter_index": 1,
        "char_count": 4520,
        "token_count": 5800,
        "status": "completed"
      },
      {
        "id": "e5f6789012345678abcdef0011223344",
        "title": "第二章 寂静的春天",
        "chapter_index": 2,
        "char_count": 5100,
        "token_count": 6500,
        "status": "completed"
      }
    ],
    "total": 36
  }
}
```

### 6.2 更新章节划分

| 属性 | 内容 |
|------|------|
| **端点** | `PUT /api/v1/projects/{id}/chapters` |
| **认证** | 是 |
| **描述** | 手动调整章节划分（合并、拆分、重命名） |

**请求体**：

```json
{
  "chapters": [
    {
      "id": "d4e5f6789012345678abcdef00112233",
      "title": "第一章 疯狂年代（修订）",
      "chapter_index": 1
    },
    {
      "id": null,
      "title": "新章节",
      "chapter_index": 2,
      "content": "这是手动拆分出的新章节内容..."
    }
  ]
}
```

> `id` 为 `null` 表示新增章节；若某个已有章节不在列表中，则表示删除该章节。

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "章节划分已更新",
  "data": {
    "chapters": [ ... ],
    "total": 37
  }
}
```

---

## 7. 剧本接口

### 7.1 获取剧本内容

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/projects/{id}/script` |
| **认证** | 是 |
| **描述** | 获取当前项目的完整剧本 YAML 内容 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "project_id": "b2c3d4e5f6789012345678abcdef0011",
    "script_type": "tv_series",
    "version": 3,
    "content_yaml": "schema_version: \"1.0\"\nmeta:\n  title: \"三体-电视剧改编\"\n  source_novel: \"三体\"\n  ...",
    "is_complete": true,
    "failed_chapters": [],
    "created_at": "2026-06-05T10:00:00Z",
    "updated_at": "2026-06-05T12:30:00Z"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `content_yaml` | string | 完整的剧本 YAML 字符串 |
| `version` | int | 剧本版本号（每次保存递增） |
| `is_complete` | bool | 是否所有章节都已成功转换 |
| `failed_chapters` | list | 转换失败的章节 ID 列表 |

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 404 | `PROJECT_NOT_FOUND` | 项目不存在或剧本尚未生成 |
| 403 | `PROJECT_NOT_OWNED` | 无权限 |

---

### 7.2 保存编辑后的剧本

| 属性 | 内容 |
|------|------|
| **端点** | `PUT /api/v1/projects/{id}/script` |
| **认证** | 是 |
| **描述** | 保存用户编辑后的完整剧本 YAML，后端进行 Schema 校验 |

**请求头**：

```
Authorization: Bearer {access_token}
```

**请求体**：

```json
{
  "content_yaml": "schema_version: \"1.0\"\nmeta:\n  title: \"三体-电视剧改编\"\n  source_novel: \"三体\"\n  author: \"刘慈欣\"\n  script_type: \"tv_series\"\n  total_episodes: 30\n  estimated_duration: 1350\n  language: \"zh-CN\"\n  version: 1\n  created_at: \"2026-06-05T10:00:00Z\"\ncharacters:\n  - id: \"char_001\"\n    name: \"汪淼\"\n    gender: \"male\"\n    age: 35\n    personality_tags:\n      - \"理性\"\n      - \"执着\"\n    role: \"protagonist\"\n    description: \"纳米材料科学家\"\n    first_appearance: \"ep1_scene_001\"\nscript:\n  episodes:\n    - episode: 1\n      title: \"倒计时\"\n      acts:\n        - act: 1\n          scenes:\n            - scene_id: \"ep1_scene_001\"\n              location: \"汪淼实验室\"\n              setting: \"interior\"\n              time: \"day\"\n              characters_present:\n                - \"char_001\"\n              content:\n                - type: \"action\"\n                  text: \"汪淼盯着显微镜，额头上渗出细密的汗珠。\"\n                - type: \"dialogue\"\n                  character: \"char_001\"\n                  text: \"不可能...这不可能。\""
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `content_yaml` | string | 是 | 完整的剧本 YAML 字符串 |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "剧本保存成功",
  "data": {
    "project_id": "b2c3d4e5f6789012345678abcdef0011",
    "version": 4,
    "schema_valid": true,
    "updated_at": "2026-06-05T12:35:00Z"
  }
}
```

**错误响应（Schema 校验失败）**：

```json
{
  "code": 422,
  "message": "Schema 校验失败",
  "detail": "剧本结构不符合规范，请修正以下问题后重新保存",
  "errors": [
    {
      "field": "script.episodes[0].acts[0].scenes[0].content[1]",
      "reason": "SCRIPT_SCHEMA_INVALID",
      "message": "对白节点角色 'char_005' 未在角色列表中定义"
    },
    {
      "field": "meta.total_episodes",
      "reason": "SCRIPT_SCHEMA_INVALID",
      "message": "tv_series 模式缺少必填字段 total_episodes"
    }
  ]
}
```

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `VALIDATION_ERROR` | `content_yaml` 为空或格式错误 |
| 403 | `PROJECT_NOT_OWNED` | 无权限 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在 |
| 422 | `SCRIPT_SCHEMA_INVALID` | YAML 结构不符合 Schema，返回具体错误列表 |

---

### 7.3 导出剧本

| 属性 | 内容 |
|------|------|
| **端点** | `GET /api/v1/projects/{id}/export` |
| **认证** | 是 |
| **描述** | 导出剧本 YAML 文件，返回下载 URL |

**请求头**：

```
Authorization: Bearer {access_token}
```

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | `yaml` | 导出格式，当前仅支持 `yaml` |

**成功响应（200）**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "download_url": "https://storage.example.com/exports/b2c3d4e5f6_三体-电视剧改编_tv_series_20260605.yaml",
    "filename": "三体-电视剧改编_tv_series_20260605.yaml",
    "file_size_bytes": 245760,
    "expires_at": "2026-06-05T13:30:00Z"
  }
}
```

| 字段 | 说明 |
|------|------|
| `download_url` | 预签名下载 URL，有效期 1 小时 |
| `filename` | 文件名格式：`{项目标题}_{script_type}_{日期}.yaml` |
| `expires_at` | 下载链接过期时间 |

> 前端拿到 `download_url` 后，可直接通过 `<a href="...">` 下载或 `window.open()` 触发浏览器下载。

**错误响应**：

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 403 | `PROJECT_NOT_OWNED` | 无权限 |
| 404 | `PROJECT_NOT_FOUND` | 项目不存在或剧本未生成 |
| 422 | `PROJECT_STATUS_INVALID` | 项目状态不允许导出（如转换中/失败） |

---

## 8. WebSocket 接口

### 8.1 转换进度推送

| 属性 | 内容 |
|------|------|
| **端点** | `WebSocket /ws/projects/{id}/progress` |
| **认证** | 是（通过 URL 查询参数传递 Token） |
| **描述** | 建立 WebSocket 连接，接收实时转换进度推送 |

**连接 URL**：

```
ws://localhost:8000/ws/projects/{id}/progress?token={jwt_access_token}
```

**服务器推送消息格式**：

```json
{
  "project_id": "b2c3d4e5f6789012345678abcdef0011",
  "status": "converting",
  "current_chapter": 12,
  "total_chapters": 36,
  "progress": 35,
  "message": "正在转换第12章 '红岸基地' ...",
  "timestamp": "2026-06-05T10:35:30Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `project_id` | string | 项目 ID |
| `status` | string | 当前状态：`converting` / `merging` / `completed` / `failed` |
| `current_chapter` | int | 当前已完成转换的章节序号 |
| `total_chapters` | int | 总章节数 |
| `progress` | int | 百分比 0-100 |
| `message` | string | 人类可读的进度描述 |
| `timestamp` | string | ISO 8601 时间戳 |

**状态流转示例**：

```
# 连接建立
→ 连接成功

# 转换开始
← {"status": "converting", "current_chapter": 0, "progress": 10, "message": "正在解析章节..."}

# 逐章推进
← {"status": "converting", "current_chapter": 1, "progress": 12, "message": "正在转换第1章 '疯狂年代' ..."}
← {"status": "converting", "current_chapter": 2, "progress": 15, "message": "正在转换第2章 '寂静的春天' ..."}
← {"status": "converting", "current_chapter": 3, "progress": 18, "message": "正在转换第3章 '红岸基地' ..."}
...

# 全部转换完成，开始合并
← {"status": "merging", "current_chapter": 36, "progress": 95, "message": "正在合并全部章节..."}

# 完成
← {"status": "completed", "current_chapter": 36, "progress": 100, "message": "剧本生成完毕！"}

# 连接关闭
→ 客户端断开
```

**错误推送**：

```json
{
  "project_id": "b2c3d4e5f6789012345678abcdef0011",
  "status": "failed",
  "current_chapter": 7,
  "total_chapters": 36,
  "progress": 25,
  "message": "第7章转换失败: LLM API 超时，已自动重试3次",
  "timestamp": "2026-06-05T10:40:00Z"
}
```

**连接关闭码**：

| 关闭码 | 含义 |
|--------|------|
| 1000 | 正常关闭（客户端主动断开） |
| 4001 | 未提供认证 Token |
| 4002 | Token 无效或已过期 |
| 4003 | 无权访问该项目 |
| 4004 | 项目不存在 |

---

## 附录 A：完整端点速查表

| 方法 | 路径 | 认证 | 说明 |
|------|------|:----:|------|
| `POST` | `/api/v1/auth/register` | 否 | 用户注册 |
| `POST` | `/api/v1/auth/login` | 否 | 用户登录 |
| `POST` | `/api/v1/auth/logout` | 是 | 用户登出 |
| `POST` | `/api/v1/auth/refresh` | 否 | 刷新 Token |
| `GET` | `/api/v1/users/me` | 是 | 获取当前用户信息 |
| `PATCH` | `/api/v1/users/me` | 是 | 更新用户信息 |
| `POST` | `/api/v1/projects` | 是 | 创建项目（上传小说） |
| `GET` | `/api/v1/projects` | 是 | 获取项目列表（分页） |
| `GET` | `/api/v1/projects/{id}` | 是 | 获取项目详情 |
| `PATCH` | `/api/v1/projects/{id}` | 是 | 更新项目配置 |
| `DELETE` | `/api/v1/projects/{id}` | 是 | 删除项目 |
| `POST` | `/api/v1/projects/{id}/convert` | 是 | 启动 AI 转换 |
| `GET` | `/api/v1/projects/{id}/chapters` | 是 | 获取章节列表 |
| `PUT` | `/api/v1/projects/{id}/chapters` | 是 | 更新章节划分 |
| `GET` | `/api/v1/projects/{id}/script` | 是 | 获取剧本内容 |
| `PUT` | `/api/v1/projects/{id}/script` | 是 | 保存编辑后的剧本 |
| `GET` | `/api/v1/projects/{id}/export` | 是 | 导出剧本文件 |
| `WS` | `/ws/projects/{id}/progress` | 是 | 实时进度推送 |

## 附录 B：CORS 配置

```python
# 开发环境
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 生产环境
ALLOWED_ORIGINS = [
    "https://your-domain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## 附录 C：速率限制

| 端点类别 | 限制 | 窗口 |
|---------|------|------|
| 认证接口（register/login） | 10 次 | 每分钟 |
| 文件上传 | 5 次 | 每分钟 |
| 启动转换 | 3 次 | 每分钟 |
| 普通查询 | 60 次 | 每分钟 |

超限时返回 `429 Too Many Requests`，响应头 `X-RateLimit-Reset` 指示重置时间