# API规范

## 基础规范

### URL格式

```
/api/v1/{resource}
```

### HTTP方法

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 查询 | `GET /api/v1/notebooks` |
| POST | 创建 | `POST /api/v1/notebooks` |
| PUT | 全量更新 | `PUT /api/v1/notebooks/1` |
| PATCH | 部分更新 | `PATCH /api/v1/notebooks/1` |
| DELETE | 删除 | `DELETE /api/v1/notebooks/1` |

### 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | 成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 500 | Server Error | 服务器错误 |

## 响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "Notebook名称",
    "created_at": "2026-06-18T12:00:00Z"
  }
}
```

### 列表响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误响应

```json
{
  "code": 400,
  "message": "参数错误",
  "errors": [
    {
      "field": "name",
      "message": "名称不能为空"
    }
  ]
}
```

## 认证

### JWT Token

```http
Authorization: Bearer <token>
```

### Token刷新

```
POST /api/v1/auth/refresh
{
  "refresh": "<refresh_token>"
}
```

## 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |
| ordering | string | -created_at | 排序字段 |

## 筛选参数

```http
GET /api/v1/notebooks?search=关键词&tag=标签名&is_favorite=true
```

## 版本控制

- URL路径版本：`/api/v1/`, `/api/v2/`
- 当前版本：v1