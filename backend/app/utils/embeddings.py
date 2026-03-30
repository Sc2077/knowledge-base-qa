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
            
            try:
                result = response.json()
            except Exception as e:
                raise ValueError(f"Failed to parse JSON response: {str(e)}. Response text: {response.text[:500]}")
            
            if not isinstance(result, dict):
                raise ValueError(f"Response is not a dictionary: {type(result).__name__}. Response: {str(result)[:500]}")
            
            embedding = result.get("embedding")
            if embedding is None:
                raise ValueError(f"'embedding' key not found in response. Available keys: {list(result.keys())}")
            
            if not isinstance(embedding, list):
                raise ValueError(f"Embedding is not a list: {type(embedding).__name__}")
            
            return embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量将文本转换为向量"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings