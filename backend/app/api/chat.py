from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.message import ChatRequest
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.models.message import Message
from app.core.deps import get_current_user
from app.services.rag_service import RAGService
from fastapi.responses import StreamingResponse
import json

router = APIRouter(prefix="/api/conversations", tags=["chat"])


async def chat_stream_generator(
    rag_service: RAGService,
    question: str,
    conversation_history: list,
    collection_name: str = None
):
    """流式响应生成器"""
    full_answer = ""
    
    try:
        async for chunk in rag_service.chat(
            question=question,
            conversation_history=conversation_history,
            collection_name=collection_name
        ):
            full_answer += chunk
            # 发送SSE格式数据
            yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        
        # 发送结束信号
        yield f"data: {json.dumps({'done': True, 'full_answer': full_answer}, ensure_ascii=False)}\n\n"
    except Exception as e:
        # 发送错误信息
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"


@router.post("/{conv_id}/chat")
async def chat(
    conv_id: str,
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息并获取回答（流式响应）"""
    # 验证对话是否属于当前用户
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conv_id,
            Conversation.user_id == current_user["user_id"]
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # 如果指定了知识库，验证知识库
    kb = None
    collection_name = None
    if chat_request.knowledge_base_id:
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == chat_request.knowledge_base_id,
                KnowledgeBase.user_id == current_user["user_id"]
            )
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base not found"
            )
        collection_name = kb.collection_name
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conv_id,
        role="user",
        content=chat_request.question
    )
    db.add(user_message)
    await db.commit()
    
    # 获取对话历史
    result = await db.execute(
        select(Message).where(Message.conversation_id == conv_id).order_by(Message.created_at)
    )
    messages = result.scalars().all()
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[:-1]  # 排除刚保存的用户消息
    ]
    
    # 创建RAG服务
    rag_service = RAGService()
    
    # 返回流式响应
    return StreamingResponse(
        chat_stream_generator(
            rag_service=rag_service,
            question=chat_request.question,
            conversation_history=conversation_history,
            collection_name=collection_name
        ),
        media_type="text/event-stream"
    )