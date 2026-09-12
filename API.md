# BlogAPI 接口文档

本文档根据项目当前 FastAPI 路由和 Pydantic Schema 整理，最后核对日期为 **2026-09-01**。

## 1. 基础信息

- API 前缀：`/api/v1`
- Swagger UI：仅在 `DJANGO_DEBUG=True` 时开放，路径为 `/docs`
- OpenAPI JSON：仅在 `DJANGO_DEBUG=True` 时开放，路径为 `/openapi.json`
- 媒体资源：`/media/...`
- 管理员接口认证：

```http
Authorization: Bearer <access_token>
```

### 1.1 通用响应结构

除认证刷新接口外，接口通常返回以下结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

`data` 没有业务数据时通常为 `null`。

### 1.2 分页结构

分页数据通常嵌套在资源名称下，例如 `data.articles`、`data.tags`：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 10,
  "total_pages": 0
}
```

分页参数：

| 参数 | 类型 | 默认值 | 约束 |
| --- | --- | ---: | --- |
| `page` | integer | `1` | 大于等于 `1` |
| `page_size` | integer | `10` | `1` 到 `100` |

### 1.3 常见状态码

| 状态码 | 含义 |
| ---: | --- |
| `200` | 请求成功 |
| `201` | 创建成功，目前黑名单创建接口使用 |
| `400` | 业务参数错误 |
| `401` | 未认证、Token 无效或已撤销 |
| `403` | 无权限、用户被禁用或 IP 被黑名单拦截 |
| `404` | 资源不存在 |
| `422` | 请求参数或请求体校验失败 |
| `429` | 访问频率超过限制 |
| `503` | Redis 等依赖服务暂不可用 |

## 2. 认证

### 2.1 登录

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
```

权限：公开访问  
限流：同一客户端 IP 每分钟最多 `5` 次。

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

请求示例：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your-password"
```

响应示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user": "admin",
    "access_token": "<access-token>",
    "refresh_token": "<refresh-token>",
    "token_type": "bearer"
  }
}
```

### 2.2 刷新 Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json
```

权限：公开访问，但必须提供有效的 Refresh Token。  
限流：同一客户端 IP 每分钟最多 `20` 次。

请求体：

```json
{
  "refresh_token": "<refresh-token>"
}
```

成功响应是**非通用响应包装**：

```json
{
  "access_token": "<new-access-token>",
  "refresh_token": "<new-refresh-token>",
  "token_type": "bearer"
}
```

Refresh Token 使用轮换机制。每次刷新都会使旧 Refresh Token 失效并签发新的 Token；检测到旧 Token 重放时，会撤销整个会话。

### 2.3 退出登录

```http
POST /api/v1/auth/logout
Authorization: Bearer <access-token>
```

权限：已登录用户。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

## 3. 站点设置

### 3.1 获取站点设置

```http
GET /api/v1/setting/
```

权限：公开访问。  
限流：每分钟最多 `60` 次。

响应字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `name` | string | 站点名称 |
| `web_name` | string | 网站名称 |
| `name_avatar` | string | 头像绝对地址 |
| `about_md` | string | Markdown 格式站点介绍 |
| `footer_text1` | string | 页脚文本一 |
| `footer_text2` | string | 页脚文本二 |
| `create_time` | datetime | 创建时间 |

### 3.2 修改站点设置

```http
PUT /api/v1/setting/
Content-Type: multipart/form-data
Authorization: Bearer <access-token>
```

权限：超级管理员。

表单字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `name` | string | 是 | 站点名称 |
| `web_name` | string | 是 | 网站名称 |
| `about_md` | string | 是 | 站点介绍 |
| `footer_text1` | string | 是 | 页脚文本一 |
| `footer_text2` | string | 是 | 页脚文本二 |
| `name_avatar` | file | 否 | 站点头像 |
| `create_time` | datetime | 否 | ISO 8601 日期时间 |

当前成功响应为：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

## 4. 文章

### 4.1 获取文章列表

```http
GET /api/v1/articles/?page=1&page_size=10
```

权限：公开访问。  
限流：每分钟最多 `60` 次。  
说明：只返回已发布文章，即 `is_draft=false`。

响应中 `data.articles.items` 的文章字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | string | 标题 |
| `slug` | string | 文章标识 |
| `cover` | string/null | 封面绝对地址 |
| `is_draft` | boolean | 是否草稿 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |
| `tags` | array | 标签列表 |

`tags` 项结构：

```json
{
  "id": 1,
  "name": "Python"
}
```

响应示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "articles": {
      "items": [
        {
          "title": "FastAPI 入门",
          "slug": "fastapi001",
          "cover": "http://localhost:8000/media/articles/covers/2026/09/fastapi001.jpg",
          "is_draft": false,
          "created_at": "2026-09-01T10:00:00+08:00",
          "updated_at": "2026-09-01T10:00:00+08:00",
          "tags": [
            {"id": 1, "name": "Python"},
            {"id": 2, "name": "FastAPI"}
          ]
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 10,
      "total_pages": 1
    }
  }
}
```

### 4.2 获取文章详情

```http
GET /api/v1/articles/{slug}
```

权限：公开访问。  
限流：每分钟最多 `120` 次。  
说明：只返回已发布文章。

响应的 `data` 为完整文章对象，除列表字段外还包含 `content`。

### 4.3 创建文章

```http
POST /api/v1/articles/
Content-Type: multipart/form-data
Authorization: Bearer <access-token>
```

权限：超级管理员。

表单字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | string | 是 | - | 标题 |
| `content` | string | 是 | - | 正文 |
| `is_draft` | boolean | 否 | `true` | 是否草稿 |
| `cover` | file | 否 | - | JPG 或 PNG 封面，最大 5MB |
| `tag_names` | string | 否 | - | 可重复提交，也支持逗号分隔 |

标签提交示例：

```text
tag_names=Python
tag_names=FastAPI
```

Swagger UI 如果将多个标签序列化为一个字段，也支持：

```text
tag_names=Python,FastAPI,Django
```

系统会自动去除标签首尾空格、拆分逗号、去重；不存在的标签会自动创建。

图片会校验文件大小、扩展名和真实图片格式，只接受扩展名与真实格式一致的 `.jpg`、`.png` 文件。

当前接口声明了文章响应模型，但代码实际返回：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### 4.4 修改文章

```http
PUT /api/v1/articles/
Content-Type: multipart/form-data
Authorization: Bearer <access-token>
```

权限：超级管理员。

表单字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `slug` | string | 是 | - | 要修改的文章 |
| `title` | string | 是 | - | 新标题 |
| `content` | string | 是 | - | 新正文 |
| `is_draft` | boolean | 否 | `true` | 是否草稿 |
| `cover` | file | 否 | - | 新封面，最大 5MB |
| `created_at` | datetime | 否 | - | ISO 8601 日期时间 |
| `tag_names` | string | 否 | - | 可重复提交或使用逗号分隔 |

标签更新规则：

- 省略 `tag_names`：保持原标签不变。
- 提交一个或多个 `tag_names`：整体替换标签。
- 提交空标签值：清空文章全部标签。
- 标签不存在时自动创建，重复名称自动复用。

当前接口实际返回 `data: null`，虽然文章更新接口的设计目标是返回更新后的完整文章数据。

### 4.5 批量删除文章

```http
DELETE /api/v1/articles/
Content-Type: application/json
Authorization: Bearer <access-token>
```

请求体：

```json
{
  "slugs": ["fastapi001", "django001"]
}
```

`slugs` 至少 1 个，最多 100 个。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "deleted_count": 2
  }
}
```

## 5. 标签

### 5.1 获取标签列表

```http
GET /api/v1/tags?page=1&page_size=10
```

权限：公开访问。  
限流：每分钟最多 `60` 次。  
说明：默认按标签名称升序排列；`article_count` 统计所有关联文章，包括草稿。

标签字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 标签 ID |
| `name` | string | 标签名称 |
| `created_at` | datetime | 创建时间 |
| `article_count` | integer | 关联文章数量 |

### 5.2 创建标签

```http
POST /api/v1/tags
Content-Type: application/json
Authorization: Bearer <access-token>
```

权限：超级管理员。

请求体：

```json
{
  "name": "Python"
}
```

标签名称会去除首尾空格，不能为空且最多 50 个字符。已存在同名标签时复用已有记录，不创建重复标签。

### 5.3 修改标签

```http
PUT /api/v1/tags/{tag_id}
Content-Type: application/json
Authorization: Bearer <access-token>
```

权限：超级管理员。

请求体：

```json
{
  "name": "FastAPI"
}
```

普通改名直接更新。若改为已有标签名称，原标签关联的文章会合并到已有标签，然后删除原标签。

### 5.4 删除标签

```http
DELETE /api/v1/tags/{tag_id}
Authorization: Bearer <access-token>
```

权限：超级管理员。

删除标签会自动解除文章关联，不删除文章。不存在时返回 `404`。

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "deleted_id": 1
  }
}
```

## 6. 评论

### 6.1 获取文章评论

```http
GET /api/v1/comment/{slug}/?page=1&page_size=10
```

权限：公开访问。  
限流：每分钟最多 `60` 次。

`data.comments.items` 字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `nickname` | string | 昵称 |
| `content` | string | 评论内容 |
| `created_at` | datetime | 创建时间 |

### 6.2 创建评论

```http
POST /api/v1/comment/{slug}/
Content-Type: application/json
```

权限：公开访问。  
限流：同一客户端 IP 每分钟最多 `10` 次。

请求体：

```json
{
  "nickname": "访客",
  "email": "visitor@example.com",
  "QQ": "123456",
  "content": "这是一条评论"
}
```

约束：

- `nickname`：1 到 20 个字符。
- `email`：可选，最多 30 个字符。
- `QQ`：可选，最多 20 个字符，当前实现按数字转换。
- `content`：1 到 200 个字符。
- 草稿文章不能评论。

### 6.3 管理员获取全部评论

```http
GET /api/v1/comment/admin?page=1&page_size=10
Authorization: Bearer <access-token>
```

权限：超级管理员。

响应中 `data.comments.items` 还包含 `id`、`IP`、`nickname`、`email`、`QQ`、`content`、`article_title`、`created_at`。

### 6.4 批量删除评论

```http
DELETE /api/v1/comment/
Content-Type: application/json
Authorization: Bearer <access-token>
```

请求体：

```json
{
  "ids": [1, 2]
}
```

`ids` 至少 1 个，最多 100 个。

## 7. 留言

### 7.1 获取留言列表

```http
GET /api/v1/message/?page=1&page_size=10
```

权限：公开访问。  
限流：每分钟最多 `60` 次。  
响应分页数据位于 `data.messages`。

### 7.2 创建留言

```http
POST /api/v1/message/
Content-Type: application/json
```

权限：公开访问。  
限流：同一客户端 IP 每分钟最多 `10` 次。

请求体与创建评论相同：

```json
{
  "nickname": "访客",
  "email": "visitor@example.com",
  "QQ": "123456",
  "content": "留言内容"
}
```

当前成功响应为 `data: null`。

### 7.3 管理员获取留言

```http
GET /api/v1/message/admin
Authorization: Bearer <access-token>
```

权限：超级管理员。

当前服务层返回分页字典，但路由声明的响应模型是数组，存在响应模型不一致风险，实际使用时应以运行结果和后续修复为准。

### 7.4 批量删除留言

```http
DELETE /api/v1/message/admin/
Content-Type: application/json
Authorization: Bearer <access-token>
```

请求体：

```json
{
  "ids": [1, 2]
}
```

`ids` 最多 20 个。响应数据为：

```json
{
  "deleted_count": 2
}
```

## 8. 笔记

### 8.1 获取笔记列表

```http
GET /api/v1/essay/?page=1&page_size=10
```

权限：公开访问。  
限流：每分钟最多 `60` 次。  
说明：列表只返回非草稿笔记，图片地址会转换为绝对地址，分页数据位于 `data.essayList`。

笔记字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `title` | string | 标题 |
| `slug` | string | 笔记标识 |
| `content` | string | 内容 |
| `imgs` | array/null | 图片绝对地址列表 |
| `updated_at` | datetime | 更新时间 |
| `created_at` | datetime | 创建时间 |



### 8.3 创建笔记

```http
POST /api/v1/essay/
Content-Type: multipart/form-data
Authorization: Bearer <access-token>
```

权限：超级管理员。

表单字段：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `title` | string | 是 | - | 标题 |
| `content` | string | 是 | - | 内容 |
| `is_draft` | boolean | 否 | `true` | 是否草稿 |
| `imgs` | file | 否 | - | 可重复上传，最多 6 张 |

每张图片最大 5MB，只接受真实类型和扩展名一致的 JPG、PNG 文件。

当前成功响应为 `data: null`。

### 8.4 批量删除笔记

```http
DELETE /api/v1/essay/slug
Content-Type: application/json
Authorization: Bearer <access-token>
```

请求体：

```json
{
  "slugs": ["essay001", "essay002"]
}
```

响应的 `data` 为删除数量，例如：

```json
{
  "code": 0,
  "message": "success",
  "data": 2
}
```

## 9. 访客与黑名单

### 9.1 记录访客

```http
POST /api/v1/visitor/track
Content-Type: application/json
```

权限：公开访问。  
限流：同一客户端 IP 每分钟最多 `30` 次。

请求体：

```json
{
  "device_type": "desktop"
}
```

`device_type` 可选；省略时根据 `User-Agent` 推断。IP 地址由服务端从请求中获取。

### 9.2 获取访客日志

```http
GET /api/v1/visitor/logs?page=1&page_size=10
Authorization: Bearer <access-token>
```

权限：超级管理员。  
响应分页数据位于 `data.logs`。

日志项字段：

```json
{
  "id": 1,
  "ip_address": "127.0.0.1",
  "user_agent": "Mozilla/5.0",
  "device_type": "desktop",
  "visited_at": "2026-09-01T10:00:00+08:00"
}
```

### 9.3 创建黑名单

```http
POST /api/v1/visitor/blacklist
Content-Type: application/json
Authorization: Bearer <access-token>
```

权限：超级管理员。  
成功状态码：`201`。

请求体：

```json
{
  "ip_address": "17.*.*.*",
  "reason": "异常访问",
  "expires_at": "2026-09-30T23:59:59+08:00"
}
```

`ip_address` 支持：

- 精确 IPv4 或 IPv6，例如 `127.0.0.1`。
- IPv4 通配格式，例如 `17.*.*.*`、`17.16.*.*`。
- 每段必须是 `0` 到 `255` 或 `*`。
- expires_at为空表示永久封禁

创建、修改、删除完成后会清空 Redis 黑名单缓存；下次访问时从数据库重新加载有效记录。

### 9.4 获取黑名单

```http
GET /api/v1/visitor/blacklist?page=1&page_size=10
Authorization: Bearer <access-token>
```

权限：超级管理员。  
响应分页数据位于 `data.blacklists`。

黑名单项字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 记录 ID |
| `ip_address` | string | 精确 IP 或通配网段 |
| `reason` | string | 原因 |
| `is_active` | boolean | 是否启用 |
| `created_at` | datetime | 创建时间 |
| `expires_at` | datetime/null | 过期时间 |

### 9.5 修改黑名单

```http
PUT /api/v1/visitor/blacklist/{blacklist_id}
Content-Type: application/json
Authorization: Bearer <access-token>
```

权限：超级管理员。所有字段可选，但至少要提供一个字段。

请求示例：

```json
{
  "ip_address": "127.*.*.*",
  "reason": "限制本地网段",
  "is_active": true,
  "expires_at": null
}
```

### 9.6 批量删除黑名单

```http
DELETE /api/v1/visitor/blacklist
Content-Type: application/json
Authorization: Bearer <access-token>
```

请求体：

```json
{
  "ids": [1, 2]
}
```

响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "deleted_count": 2
  }
}
```

## 10. 用户

### 10.1 修改用户名或密码

```http
POST /api/v1/user/
Content-Type: multipart/form-data
Authorization: Bearer <access-token>
```

权限：超级管理员。

表单字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `newName` | string | 新用户名；提供后执行改名 |
| `pwd` | string | 当前密码 |
| `newPwd` | string | 新密码；与 `pwd` 同时提供时执行改密 |

当前接口通过字段是否为空判断执行哪种操作：`newName` 优先于密码修改。

修改密码时会校验 Django 密码复杂度，并撤销该用户的全部登录会话，旧 Access Token 和 Refresh Token 将失效。

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

## 11. 限流规则汇总

限流器使用 Redis 滑动窗口，按客户端 IP 和路由分别统计。Redis 不可用时是否放行由 `RATE_LIMIT_FAIL_OPEN` 配置决定。

| 接口 | 每分钟限制 |
| --- | ---: |
| `POST /auth/login` | 5 |
| `POST /auth/refresh` | 20 |
| `GET /setting/` | 60 |
| `GET /articles/` | 60 |
| `GET /articles/{slug}` | 120 |
| `GET /tags` | 60 |
| `GET /comment/{slug}/` | 60 |
| `POST /comment/{slug}/` | 10 |
| `GET /message/` | 60 |
| `POST /message/` | 10 |
| `GET /essay/` | 60 |
| `POST /visitor/track` | 30 |

未列出的管理员写接口当前没有声明限流 Dependency。

## 12. 文件资源地址

上传文件保存在 Django `MEDIA_ROOT` 下，访问前缀为 `/media/`。例如数据库中保存：

```text
imgs/2026/09/AbCd1234/1xYz.jpg
```

对应访问地址为：

```text
http://localhost:8000/media/imgs/2026/09/AbCd1234/1xYz.jpg
```

文章封面和笔记图片接口会根据当前请求的 `base_url` 生成绝对地址。生产环境部署在反向代理后时，应正确配置受信任的 Host 和代理头。

## 13. 当前实现注意事项

以下内容是根据当前源码发现的实现差异，调用方需要留意：

1. 文章创建、文章修改、站点设置、笔记创建、留言创建、用户修改当前实际返回 `data: null`，不会返回接口声明中可能暗示的完整资源对象。
2. `GET /api/v1/essay/slug` 尚未实现。
3. `GET /api/v1/message/admin` 的路由响应模型声明为数组，但服务层返回分页字典，可能触发 `ResponseValidationError`。
4. `GET /api/v1/articles/test` 的声明顺序晚于 `GET /api/v1/articles/{slug}`，可能被动态 slug 路由匹配。
5. 评论和留言的 `QQ` 在 Schema 中可选，但服务层会尝试转换为整数；未提供或提供非数字值时可能产生异常。
6. 黑名单匹配由中间件统一执行，命中后所有接口都会返回 `403`。Redis 黑名单缓存不可用时会回退到数据库查询。
