"""
애플리케이션 설정
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # Server
    backend_port: int = 8000
    backend_host: str = "0.0.0.0"
    log_level: str = "INFO"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3.2:latest"
    ollama_embedding_model: str = "nomic-embed-text:latest"

    # Mem0
    vector_store_path: str = "../data/qdrant"
    history_db_path: str = "../data/memory_history.db"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# 디렉토리 생성
os.makedirs(os.path.dirname(settings.vector_store_path), exist_ok=True)
os.makedirs(os.path.dirname(settings.history_db_path), exist_ok=True)
