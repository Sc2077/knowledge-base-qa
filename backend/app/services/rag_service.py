from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.milvus_store import MilvusStore
from app.utils.embeddings import EmbeddingService


class RAGService:
    """RAG问答服务"""
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.milvus_store = MilvusStore()
        self.openai_client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        self.model = settings.DEEPSEEK_MODEL
    
    async def chat(
        self,
        question: str,
        conversation_history: List[dict],
        knowledge_base_id: Optional[str] = None,
        collection_name: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        执行RAG问答
        
        Args:
            question: 用户问题
            conversation_history: 对话历史
            knowledge_base_id: 知识库ID
            collection_name: Milvus集合名称
        
        Yields:
            生成的答案片段
        """
        # 1. 检索相关文档（仅基于当前问题）
        relevant_docs = []
        if collection_name:
            query_embedding = await self.embedding_service.embed_text(question)
            search_results = self.milvus_store.search(
                collection_name=collection_name,
                query_embedding=query_embedding,
                top_k=settings.TOP_K
            )
            relevant_docs = [result["chunk_text"] for result in search_results]
        
        # 2. 构建Prompt
        prompt = self._build_prompt(question, conversation_history, relevant_docs)
        
        # 3. 调用DeepSeek API（流式）
        stream = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个智能问答助手，基于提供的文档内容回答用户问题。如果文档中没有相关信息，请诚实地告诉用户。"},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.7
        )
        
        # 4. 流式返回答案
        full_answer = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield content
    
    def _build_prompt(
        self,
        question: str,
        conversation_history: List[dict],
        relevant_docs: List[str]
    ) -> str:
        """构建Prompt"""
        # 添加文档内容
        docs_section = ""
        if relevant_docs:
            docs_section = "\n\n以下是相关的文档内容：\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                docs_section += f"【文档片段{i}】\n{doc}\n\n"
        else:
            docs_section = "\n\n（未找到相关文档）\n\n"
        
        # 添加对话历史（只保留最近3轮）
        history_section = ""
        if conversation_history:
            history_section = "对话历史：\n\n"
            # 获取最近6条消息（3轮对话）
            recent_history = conversation_history[-6:]
            for msg in recent_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_section += f"{role}: {msg['content']}\n\n"
            history_section += "\n"
        
        # 组合完整Prompt
        full_prompt = f"""{docs_section}{history_section}当前问题：{question}

请根据文档内容和对话历史，给出准确、详细的回答。"""
        
        return full_prompt