# 项目上下文文档

## 项目概述

通用知识库问答Agent应用 - 基于 FastAPI + React 的智能知识库问答系统，支持文件上传、向量化存储、RAG智能问答功能。

### 核心技术栈

**后端:**
- FastAPI 0.109.0 (Python 3.12)
- SQLAlchemy 2.0.25 (异步 ORM)
- MySQL 8.0 (关系数据库)
- Milvus 2.3.4 (向量数据库)
- PyMilvus (Milvus Python 客户端)
- DeepSeek API (问答模型)
- Ollama (本地向量模型服务，使用 all-minilm)
- JWT 认证

**前端:**
- React 18.2.0
- TypeScript 5.3.3
- Vite 5.0.11 (构建工具)
- React Router DOM 6.21.0 (路由)
- Ant Design 5.12.8 (UI 组件库)
- Axios 1.6.5 (HTTP 客户端)

**部署:**
- Docker Compose
- Nginx (前端反向代理)

### 主要功能

- 用户注册/登录（JWT 认证）
- 多知识库管理（创建、查看、更新、删除）
- 文件上传（PDF、Word、Markdown、TXT）
- 自动文本分割和向量化
- 语义相似度检索（基于 Milvus）
- RAG 智能问答（支持上下文关联）
- 多轮对话支持
- 流式响应

## 项目结构

```
knowledge-base-qa/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证相关 API
│   │   │   ├── knowledge_base.py  # 知识库 API
│   │   │   ├── document.py    # 文档 API
│   │   │   ├── conversation.py    # 对话 API
│   │   │   └── chat.py        # 聊天 API
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   ├── deps.py        # 依赖注入
│   │   │   └── security.py    # 安全相关
│   │   ├── models/            # SQLAlchemy 数据库模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── knowledge_base.py  # 知识库模型
│   │   │   ├── document.py    # 文档模型
│   │   │   ├── conversation.py    # 对话模型
│   │   │   └── message.py     # 消息模型
│   │   ├── schemas/           # Pydantic 模式
│   │   │   ├── user.py        # 用户模式
│   │   │   ├── knowledge_base.py  # 知识库模式
│   │   │   ├── document.py    # 文档模式
│   │   │   ├── conversation.py    # 对话模式
│   │   │   └── message.py     # 消息模式
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── document_service.py  # 文档处理服务
│   │   │   └── rag_service.py       # RAG 问答服务
│   │   ├── utils/             # 工具函数
│   │   │   ├── embeddings.py  # 向量嵌入服务
│   │   │   ├── file_parser.py # 文件解析器
│   │   │   ├── milvus_store.py     # Milvus 存储服务
│   │   │   └── text_splitter.py    # 文本分割器
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile             # 后端 Docker 配置
│   └── .env.example           # 环境变量模板
├── frontend/                  # 前端服务
│   ├── src/
│   │   ├── pages/             # 页面组件
│   │   │   ├── Login.tsx      # 登录页
│   │   │   ├── KnowledgeBaseList.tsx  # 知识库列表
│   │   │   ├── KnowledgeBaseDetail.tsx  # 知识库详情
│   │   │   ├── ConversationList.tsx    # 对话列表
│   │   │   └── ConversationDetail.tsx  # 对话详情
│   │   ├── components/        # 通用组件
│   │   │   └── Layout.tsx     # 布局组件
│   │   ├── services/          # API 服务
│   │   │   ├── api.ts         # API 客户端配置
│   │   │   ├── auth.ts        # 认证 API
│   │   │   ├── conversation.ts    # 对话 API
│   │   │   ├── document.ts    # 文档 API
│   │   │   └── knowledgeBase.ts    # 知识库 API
│   │   ├── App.tsx            # 应用入口
│   │   ├── main.tsx           # React 入口
│   │   └── index.css          # 全局样式
│   ├── package.json           # Node.js 依赖
│   ├── tsconfig.json          # TypeScript 配置
│   ├── vite.config.ts         # Vite 配置
│   ├── nginx.conf             # Nginx 配置
│   └── Dockerfile             # 前端 Docker 配置
├── docker/                    # Docker 配置
│   └── init.sql               # 数据库初始化脚本
├── docker-compose.yml         # Docker Compose 配置
├── .env.example               # 环境变量模板
└── README.md                  # 项目说明文档
```

## 构建和运行

### Docker Compose 方式（推荐）

**启动所有服务:**
```bash
docker-compose up -d
```

**查看服务状态:**
```bash
docker-compose ps
```

**查看日志:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**首次启动后配置（下载 Ollama 向量模型）:**
```bash
# 进入 Ollama 容器
docker exec -it kb_qa_ollama bash

# 下载向量模型
ollama pull all-minilm

# 退出容器
exit
```

**访问应用:**
- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

**停止服务:**
```bash
docker-compose down
```

**停止并删除所有数据:**
```bash
docker-compose down -v
```

### 开发方式

**后端开发:**
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端开发:**
```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 环境变量配置

必需的环境变量（在 `.env` 文件中配置）：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_change_this
```

其他重要配置（可通过 `.env` 覆盖）：
- `DATABASE_URL`: MySQL 连接字符串
- `MILVUS_HOST`: Milvus 服务地址
- `OLLAMA_BASE_URL`: Ollama 服务地址
- `OLLAMA_MODEL`: 向量模型名称（默认: all-minilm）
- `DEEPSEEK_BASE_URL`: DeepSeek API 地址
- `DEEPSEEK_MODEL`: DeepSeek 模型名称（默认: deepseek-chat）

## 主要 API 端点

**认证:**
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

**知识库:**
- `GET /api/knowledge-bases` - 获取知识库列表
- `POST /api/knowledge-bases` - 创建知识库
- `GET /api/knowledge-bases/{id}` - 获取知识库详情
- `PUT /api/knowledge-bases/{id}` - 更新知识库
- `DELETE /api/knowledge-bases/{id}` - 删除知识库

**文档:**
- `POST /api/documents/upload` - 上传文档
- `GET /api/documents` - 获取文档列表
- `DELETE /api/documents/{id}` - 删除文档

**对话:**
- `GET /api/conversations` - 获取对话列表
- `POST /api/conversations` - 创建对话
- `GET /api/conversations/{id}` - 获取对话详情
- `DELETE /api/conversations/{id}` - 删除对话

**聊天:**
- `POST /api/conversations/{id}/chat` - 发送消息（流式响应）

## 开发约定

### 后端开发规范

**异步编程:**
- 所有数据库操作使用 `async/await`
- 使用 `AsyncSession` 进行数据库会话管理
- 外部 API 调用（Ollama、DeepSeek）使用异步 HTTP 客户端

**数据验证:**
- 所有 API 输入使用 Pydantic 模式进行验证
- 在 `app/schemas/` 目录定义请求和响应模式

**数据库模型:**
- 在 `app/models/` 目录定义 SQLAlchemy 模型
- 使用 UUID 作为主键
- 所有表包含 `created_at` 和 `updated_at` 字段
- 使用 `ondelete="CASCADE"` 定义级联删除

**依赖注入:**
- 在 `app/core/deps.py` 定义依赖项
- 使用 `Depends()` 进行依赖注入

**服务层:**
- 在 `app/services/` 目录实现业务逻辑
- RAG 服务位于 `app/services/rag_service.py`
- 文档处理服务位于 `app/services/document_service.py`

### 前端开发规范

**组件组织:**
- 页面组件放在 `src/pages/`
- 通用组件放在 `src/components/`
- API 服务放在 `src/services/`

**状态管理:**
- 使用 React Hooks 进行本地状态管理
- 认证状态存储在 localStorage
- API 响应数据通过 Props 传递

**样式:**
- 使用 Ant Design 组件库
- 全局样式在 `src/index.css`
- 避免使用内联样式

**API 调用:**
- 统一使用 `src/services/` 中的 API 函数
- 使用 Axios 进行 HTTP 请求
- 自动在请求头中添加 JWT token

**路由:**
- 使用 React Router DOM v6
- 所有路由在 `App.tsx` 中定义
- 使用 `<Navigate>` 进行重定向

### 代码风格

**后端:**
- 使用 Black 进行代码格式化
- 函数名使用 snake_case
- 类名使用 PascalCase
- 私有方法使用 `_` 前缀

**前端:**
- 函数组件使用 PascalCase
- 变量名使用 camelCase
- 常量使用 UPPER_SNAKE_CASE

## 关键实现细节

### RAG 问答流程

1. **文档处理流程:**
   - 文件上传 → 解析（PDF/Word/Markdown/TXT）→ 文本分割（Chunking）→ 向量化 → 存储到 Milvus

2. **问答流程:**
   - 用户问题 → 向量化 → Milvus 检索（Top-K）→ 构建 Prompt（包含文档内容和对话历史）→ DeepSeek API 生成答案 → 流式返回

3. **配置参数:**
   - `CHUNK_SIZE`: 文本块大小（默认: 500）
   - `CHUNK_OVERLAP`: 文本块重叠（默认: 50）
   - `TOP_K`: 检索文档数量（默认: 5）

### 认证机制

- 使用 JWT（JSON Web Token）进行认证
- Token 有效期: 7 天（可配置）
- 存储位置: localStorage（前端）
- 在请求头中添加: `Authorization: Bearer <token>`

### Milvus 集合管理

- 每个知识库对应一个 Milvus 集合
- 集合名称格式: `kb_{uuid}`
- 向量维度: 由嵌入模型决定（all-minilm 为 384 维）
- 删除知识库时自动删除对应的 Milvus 集合

## 数据库初始化

数据库初始化脚本位于 `docker/init.sql`，包含：
- 用户表
- 知识库表
- 文档表
- 对话表
- 消息表

## 常见问题排查

**服务启动失败:**
- 检查 Docker 和 Docker Compose 是否正确安装
- 查看服务日志: `docker-compose logs -f <service_name>`

**数据库连接失败:**
- 检查 MySQL 容器是否正常运行
- 验证数据库连接字符串配置

**向量化失败:**
- 确认 Ollama 容器正常运行
- 验证向量模型已下载: `docker exec kb_qa_ollama ollama list`

**问答失败:**
- 检查 DeepSeek API Key 是否正确配置
- 验证 API 连接和可用性

**Milvus 连接失败:**
- 确认 Milvus 容器正常运行
- 检查依赖服务（etcd、MinIO）状态

## 测试建议

**后端测试:**
- 使用 pytest 进行单元测试
- 测试 API 端点
- 测试服务层逻辑
- 使用测试数据库

**前端测试:**
- 使用 React Testing Library
- 测试组件渲染
- 测试用户交互
- Mock API 调用

## 性能优化

**后端:**
- 使用连接池管理数据库连接
- 异步处理文件上传和向量化
- 缓存常用查询结果

**前端:**
- 使用 React.memo 优化组件渲染
- 懒加载页面组件
- 优化大文件上传（分片上传）

## 安全注意事项

- JWT_SECRET_KEY 必须在生产环境中修改
- 使用环境变量管理敏感信息
- 实施文件上传大小限制
- 验证用户输入，防止 SQL 注入和 XSS
- 使用 HTTPS 保护 API 通信
- 定期更新依赖包

## 下一步开发建议

1. 添加单元测试和集成测试
2. 实现文件上传进度显示
3. 支持更多文件格式（Excel、PPT 等）
4. 添加文档版本管理
5. 实现知识库分享功能
6. 添加用户权限管理（RBAC）
7. 优化向量检索算法
8. 支持多种向量模型
9. 添加问答质量评估
10. 实现知识库导出功能