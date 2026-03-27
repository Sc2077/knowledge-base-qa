from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse
from app.models.knowledge_base import KnowledgeBase
from app.core.deps import get_current_user
import uuid

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])


@router.get("", response_model=List[KnowledgeBaseResponse])
async def get_knowledge_bases(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的知识库列表"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.user_id == current_user["user_id"])
    )
    knowledge_bases = result.scalars().all()
    return knowledge_bases


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识库"""
    # 生成唯一的集合名称
    collection_name = f"kb_{uuid.uuid4().hex[:16]}"
    
    knowledge_base = KnowledgeBase(
        user_id=current_user["user_id"],
        name=kb_data.name,
        description=kb_data.description,
        collection_name=collection_name
    )
    
    db.add(knowledge_base)
    await db.commit()
    await db.refresh(knowledge_base)
    
    # 在Milvus中创建集合
    from app.utils.milvus_store import MilvusStore
    from app.utils.embeddings import EmbeddingService
    import asyncio
    
    try:
        # 创建Milvus集合
        milvus_store = MilvusStore()
        
        # 获取向量维度
        embedding_service = EmbeddingService()
        test_embedding = await asyncio.create_task(
            embedding_service.embed_text("test")
        )
        dimension = len(test_embedding)
        
        milvus_store.create_collection(collection_name, dimension)
    except Exception as e:
        # 记录错误但不阻止创建
        print(f"Failed to create Milvus collection: {str(e)}")
    
    return knowledge_base


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库详情"""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    knowledge_base = result.scalar_one_or_none()
    
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    return knowledge_base


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: str,
    kb_data: KnowledgeBaseUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    knowledge_base = result.scalar_one_or_none()
    
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # 更新字段
    if kb_data.name is not None:
        knowledge_base.name = kb_data.name
    if kb_data.description is not None:
        knowledge_base.description = kb_data.description
    
    await db.commit()
    await db.refresh(knowledge_base)
    
    return knowledge_base


@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识库"""
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    knowledge_base = result.scalar_one_or_none()
    
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # 删除Milvus中的集合
    from app.utils.milvus_store import MilvusStore
    milvus_store = MilvusStore()
    try:
        milvus_store.drop_collection(knowledge_base.collection_name)
    except Exception as e:
        # 记录错误但不阻止删除
        print(f"Failed to drop Milvus collection: {str(e)}")
    
    await db.delete(knowledge_base)
    await db.commit()
    
    return {"message": "Knowledge base deleted successfully"}