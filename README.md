# 通用知识库问答Agent应用

基于 FastAPI + React 的智能知识库问答系统，支持文件上传、向量化存储、RAG智能问答功能。

## 技术栈

- **后端**: FastAPI + Python 3.12
- **前端**: React + TypeScript
- **向量数据库**: Milvus
- **关系数据库**: MySQL 8.0
- **问答模型**: DeepSeek API
- **向量模型**: Ollama (本地部署)
- **部署**: Docker Compose
- **认证**: JWT

## 核心功能

- ✅ 用户注册/登录（JWT认证）
- ✅ 多知识库管理
- ✅ 文件上传（PDF/Word/Markdown/TXT）
- ✅ 自动文本分割和向量化
- ✅ 语义相似度检索
- ✅ RAG智能问答（支持上下文关联）
- ✅ 多轮对话支持
- ✅ 流式响应

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- DeepSeek API Key

### 环境配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env`，配置必要的环境变量：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_change_this
```

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

### 首次启动后配置

启动服务后，需要下载Ollama向量模型：

```bash
# 进入Ollama容器
docker exec -it kb_qa_ollama bash

# 下载向量模型
ollama pull all-minilm

# 退出容器
exit
```

### 访问应用

- 前端: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
knowledge-base-qa/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据库模型
│   │   ├── schemas/     # Pydantic模式
│   │   ├── services/    # 业务逻辑
│   │   ├── utils/       # 工具函数
│   │   └── main.py      # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # 前端服务
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   ├── components/  # 通用组件
│   │   ├── services/    # API服务
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker/              # Docker配置
│   └── init.sql         # 数据库初始化脚本
├── docker-compose.yml   # Docker Compose配置
└── README.md
```

## 使用说明

### 1. 用户注册和登录

- 访问 http://localhost
- 点击"注册"标签，填写用户名、邮箱和密码
- 注册成功后，使用用户名和密码登录

### 2. 创建知识库

- 登录后，点击左侧菜单的"知识库"
- 点击"新建知识库"按钮
- 输入知识库名称和描述（可选）
- 点击确定创建

### 3. 上传文档

- 进入知识库详情页面
- 点击上传区域，或拖拽文件到上传区域
- 支持的文件格式：PDF、Word、Markdown、TXT
- 文件上传后会自动进行解析、分割和向量化处理

### 4. 创建对话

- 点击左侧菜单的"对话"
- 点击"新建对话"按钮
- 输入对话标题
- 点击确定创建

### 5. 进行问答

- 进入对话详情页面
- 在输入框中输入问题
- 可选择关联的知识库（可选）
- 点击"发送"按钮
- 系统会检索相关文档并生成答案（流式响应）

### 6. 多轮对话

- 在同一个对话中，可以继续提问
- 系统会记住对话历史，支持上下文关联
- 例如：
  - User: 什么是RAG？
  - Assistant: RAG是检索增强生成...
  - User: 有什么优势？
  - Assistant: 主要优势包括...

## 开发指南

### 后端开发

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## API文档

启动服务后访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/knowledge-bases` - 获取知识库列表
- `POST /api/knowledge-bases` - 创建知识库
- `POST /api/documents/upload` - 上传文档
- `GET /api/conversations` - 获取对话列表
- `POST /api/conversations` - 创建对话
- `POST /api/conversations/{id}/chat` - 发送消息（流式响应）

## 常见问题

### 1. 服务启动失败

检查Docker和Docker Compose是否正确安装：
```bash
docker --version
docker-compose --version
```

### 2. 无法连接到数据库

确保MySQL服务已启动：
```bash
docker-compose logs mysql
```

### 3. 向量化失败

确保Ollama模型已下载：
```bash
docker exec kb_qa_ollama ollama list
```

### 4. 问答失败

检查DeepSeek API Key是否正确配置：
```bash
docker-compose exec backend env | grep DEEPSEEK
```

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据（谨慎使用）
docker-compose down -v
```

## 许可证

MIT License