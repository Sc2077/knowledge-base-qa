from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    title: str
    knowledge_base_id: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    knowledge_base_id: Optional[str]
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True