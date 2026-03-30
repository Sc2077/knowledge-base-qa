from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql://root:password@mysql:3306/kb_qa"
    
    # Milvus
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "nomic-embed-text"
    
    # DeepSeek
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080
    
    # File Upload
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()