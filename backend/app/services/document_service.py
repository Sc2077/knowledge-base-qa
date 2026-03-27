from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.utils.file_parser import FileParser
from app.utils.text_splitter import TextSplitter
from app.utils.embeddings import EmbeddingService
from app.utils.milvus_store import MilvusStore
from app.core.config import settings


class DocumentService:
    """文档处理服务"""
    
    def __init__(self):
        self.file_parser = FileParser()
        self.text_splitter = TextSplitter()
        self.embedding_service = EmbeddingService()
        self.milvus_store = MilvusStore()
    
    async def process_document(
        self,
        document_id: str,
        db: AsyncSession
    ):
        """
        处理文档：
        1. 解析文件内容
        2. 分割文本
        3. 生成向量
        4. 存储到Milvus
        5. 更新文档状态
        """
        # 获取文档信息
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return
        
        # 获取知识库信息
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == document.knowledge_base_id)
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            await self._update_document_status(
                document_id, db, "failed", "Knowledge base not found"
            )
            return
        
        try:
            # 1. 解析文件
            text = self.file_parser.parse_file(document.file_type, document.file_path)
            
            if not text.strip():
                await self._update_document_status(
                    document_id, db, "failed", "Empty document content"
                )
                return
            
            # 2. 分割文本
            chunks_data = self.text_splitter.split_text_with_metadata(text, document_id)
            
            if not chunks_data:
                await self._update_document_status(
                    document_id, db, "failed", "Failed to split text"
                )
                return
            
            # 3. 生成向量
            texts = [chunk["text"] for chunk in chunks_data]
            embeddings = await self.embedding_service.embed_texts(texts)
            
            # 4. 确保Milvus集合存在
            self.milvus_store.create_collection(kb.collection_name)
            
            # 5. 存储到Milvus
            self.milvus_store.insert_chunks(kb.collection_name, chunks_data, embeddings)
            
            # 6. 更新文档状态
            await self._update_document_status(
                document_id, db, "completed", None, len(chunks_data)
            )
            
        except Exception as e:
            await self._update_document_status(
                document_id, db, "failed", str(e)
            )
    
    async def _update_document_status(
        self,
        document_id: str,
        db: AsyncSession,
        status: str,
        error_message: str = None,
        chunk_count: int = None
    ):
        """更新文档状态"""
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message
        if chunk_count is not None:
            update_data["chunk_count"] = chunk_count
        
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await db.commit()
    
    async def delete_document_vectors(
        self,
        document_id: str,
        collection_name: str
    ):
        """删除文档的向量"""
        try:
            self.milvus_store.delete_by_doc_id(collection_name, document_id)
        except Exception as e:
            # 记录错误但不抛出异常
            print(f"Failed to delete vectors: {str(e)}")