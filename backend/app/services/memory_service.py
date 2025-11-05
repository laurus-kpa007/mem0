"""
Memory 서비스 (mem0 wrapper)
"""
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.configs.llms.base import LlmConfig
from mem0.configs.embedders.base import EmbedderConfig
from mem0.configs.vector_stores.base import VectorStoreConfig
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """mem0 Memory 관리 서비스"""

    def __init__(
        self,
        ollama_base_url: str,
        ollama_model: str,
        embedding_model: str,
        vector_store_path: str,
        history_db_path: str
    ):
        self.config = MemoryConfig(
            llm=LlmConfig(
                provider="ollama",
                config={
                    "model": ollama_model,
                    "base_url": ollama_base_url,
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            ),
            embedder=EmbedderConfig(
                provider="ollama",
                config={
                    "model": embedding_model,
                    "base_url": ollama_base_url
                }
            ),
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "path": vector_store_path,
                    "collection_name": "mem0_memories"
                }
            ),
            history_db_path=history_db_path
        )

        self.memory = Memory(config=self.config)
        logger.info("MemoryService initialized successfully")

    async def add_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """메모리 추가"""
        try:
            result = self.memory.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                metadata=metadata or {}
            )
            logger.info(f"Memory added for user {user_id}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            raise

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """메모리 검색"""
        try:
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            logger.info(f"Found {len(results)} memories for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            raise

    async def get_all_memories(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """전체 메모리 조회"""
        try:
            results = self.memory.get_all(
                user_id=user_id,
                limit=limit
            )
            return results
        except Exception as e:
            logger.error(f"Error getting all memories: {e}")
            raise

    async def delete_memory(self, memory_id: str) -> Dict:
        """메모리 삭제"""
        try:
            self.memory.delete(memory_id=memory_id)
            return {"success": True, "message": "Memory deleted"}
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            raise

    async def update_memory(self, memory_id: str, data: str) -> Dict:
        """메모리 업데이트"""
        try:
            result = self.memory.update(memory_id=memory_id, data=data)
            return result
        except Exception as e:
            logger.error(f"Error updating memory: {e}")
            raise
