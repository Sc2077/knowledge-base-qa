import httpx
from typing import List
from app.core.config import settings


class EmbeddingService:
    """向量化服务"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
    
    async def embed_text(self, text: str) -> List[float]:
        """将文本转换为向量"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings