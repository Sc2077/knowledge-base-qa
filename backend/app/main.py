from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api import auth, knowledge_base, document, conversation, chat

app = FastAPI(
    title="Knowledge Base QA API",
    description="通用知识库问答Agent应用API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(knowledge_base.router)
app.include_router(document.router)
app.include_router(conversation.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    await init_db()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Knowledge Base QA API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)