"""
FastAPI 의존성 주입
"""
from functools import lru_cache
from app.services.memory_service import MemoryService
from app.services.ollama_service import OllamaService
from app.services.chat_service import ChatService
from app.services.tag_service import TagService, get_tag_service as _get_tag_service
from app.config import settings


@lru_cache()
def get_memory_service() -> MemoryService:
    """MemoryService 싱글톤 인스턴스 반환"""
    return MemoryService(
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_default_model,
        embedding_model=settings.ollama_embedding_model,
        vector_store_path=settings.vector_store_path,
        history_db_path=settings.history_db_path
    )


@lru_cache()
def get_ollama_service() -> OllamaService:
    """OllamaService 싱글톤 인스턴스 반환"""
    return OllamaService(base_url=settings.ollama_base_url)


def get_chat_service(
    memory_service: MemoryService = None,
    ollama_service: OllamaService = None
) -> ChatService:
    """ChatService 인스턴스 반환"""
    if memory_service is None:
        memory_service = get_memory_service()
    if ollama_service is None:
        ollama_service = get_ollama_service()
    return ChatService(memory_service, ollama_service)


def get_tag_service() -> TagService:
    """TagService 싱글톤 인스턴스 반환"""
    ollama_service = get_ollama_service()
    return _get_tag_service(ollama_service)
