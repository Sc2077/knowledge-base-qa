from typing import List
from app.core.config import settings


class TextSplitter:
    """文本分割器"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def split_text(self, text: str) -> List[str]:
        """分割文本"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # 如果不是最后一个chunk，尝试在空格或换行符处分割
            if end < text_length:
                # 查找最后一个空格或换行符
                last_space = text.rfind(' ', start, end)
                last_newline = text.rfind('\n', start, end)
                
                # 选择最接近chunk_size的分割点
                split_pos = max(last_space, last_newline)
                if split_pos > start:
                    end = split_pos + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def split_text_with_metadata(self, text: str, doc_id: str) -> List[dict]:
        """分割文本并添加元数据"""
        chunks = self.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                "text": chunk,
                "chunk_index": i,
                "doc_id": doc_id
            })
        
        return chunks