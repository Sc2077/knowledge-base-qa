from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的对话列表"""
    result = await db.execute(
        select(Conversation).where(Conversation.user_id == current_user["user_id"])
    )
    conversations = result.scalars().all()
    return conversations


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conv_data: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建对话"""
    # 如果指定了知识库，验证知识库是否属于当前用户
    if conv_data.knowledge_base_id:
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == conv_data.knowledge_base_id,
                KnowledgeBase.user_id == current_user["user_id"]
            )
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base not found"
            )
    
    conversation = Conversation(
        user_id=current_user["user_id"],
        title=conv_data.title,
        knowledge_base_id=conv_data.knowledge_base_id
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.get("/{conv_id}", response_model=ConversationResponse)
async def get_conversation(
    conv_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话详情"""
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
    
    return conversation


@router.delete("/{conv_id}")
async def delete_conversation(
    conv_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除对话"""
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
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}


@router.get("/{conv_id}/messages")
async def get_conversation_messages(
    conv_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取对话的消息列表"""
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
    
    # 获取消息列表，按创建时间升序排列（最早的在前，最新的在后）
    from app.models.message import Message
    from app.schemas.message import MessageResponse
    
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    
    return [MessageResponse.model_validate(msg) for msg in messages]