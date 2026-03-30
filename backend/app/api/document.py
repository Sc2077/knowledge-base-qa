from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from typing import List
import os
import uuid
import asyncio
from app.core.database import get_db, engine
from app.core.config import settings
from app.schemas.document import DocumentResponse
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.core.deps import get_current_user
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])


async def process_document_task(document_id: str):
    """后台任务：处理文档"""
    # 创建新的数据库会话
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with AsyncSessionLocal() as db:
        try:
            document_service = DocumentService()
            await document_service.process_document(document_id, db)
        except Exception as e:
            print(f"Error processing document {document_id}: {str(e)}")


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    knowledge_base_id: str = Form(...),
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档"""
    # 验证知识库是否属于当前用户
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes"
        )
    
    # 获取文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_type_map = {
        '.pdf': 'pdf',
        '.docx': 'word',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    file_type = file_type_map.get(file_ext, 'unknown')
    if file_type == 'unknown':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )
    
    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, knowledge_base_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 创建文档记录
    document = Document(
        knowledge_base_id=knowledge_base_id,
        filename=file.filename,
        file_type=file_type,
        file_size=len(content),
        file_path=file_path,
        status="processing"
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # 添加后台任务处理文档
    background_tasks.add_task(process_document_task, document.id)
    
    return document


@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    knowledge_base_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库的文档列表"""
    # 验证知识库是否属于当前用户
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == knowledge_base_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge base not found"
        )
    
    # 获取文档列表
    result = await db.execute(
        select(Document).where(Document.knowledge_base_id == knowledge_base_id)
    )
    documents = result.scalars().all()
    
    return documents


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    # 获取文档并验证权限
    result = await db.execute(
        select(Document).join(KnowledgeBase).where(
            Document.id == doc_id,
            KnowledgeBase.user_id == current_user["user_id"]
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # 获取知识库信息
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == document.knowledge_base_id)
    )
    kb = result.scalar_one_or_none()
    
    # 删除文件
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # 从Milvus中删除相关向量
    if kb:
        document_service = DocumentService()
        await document_service.delete_document_vectors(doc_id, kb.collection_name)
    
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}