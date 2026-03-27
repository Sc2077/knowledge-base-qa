from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentUpload(BaseModel):
    knowledge_base_id: str


class DocumentResponse(BaseModel):
    id: str
    knowledge_base_id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True