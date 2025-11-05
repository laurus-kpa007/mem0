"""
Chat 서비스
"""
from typing import List, Dict, Optional
from .memory_service import MemoryService
from .ollama_service import OllamaService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """채팅 서비스"""

    def __init__(
        self,
        memory_service: MemoryService,
        ollama_service: OllamaService
    ):
        self.memory_service = memory_service
        self.ollama_service = ollama_service

    async def generate_response(
        self,
        message: str,
        user_id: str,
        model: str,
        use_memory: bool = True,
        memory_limit: int = 5
    ) -> Dict:
        """메모리 기반 응답 생성"""
        related_memories = []

        # 관련 메모리 검색
        if use_memory and memory_limit > 0:
            try:
                related_memories = await self.memory_service.search_memories(
                    query=message,
                    user_id=user_id,
                    limit=memory_limit
                )
            except Exception as e:
                logger.warning(f"Memory search failed: {e}")

        # 컨텍스트 메시지 구성
        context_messages = []

        if related_memories:
            context = "다음은 관련된 정보입니다:\n\n"
            for i, mem in enumerate(related_memories, 1):
                context += f"{i}. {mem.get('memory', mem.get('content', ''))}\n"

            context += "\n위 정보를 참고하여 사용자의 질문에 답변해주세요."

            context_messages.append({
                "role": "system",
                "content": context
            })

        # 사용자 메시지 추가
        context_messages.append({
            "role": "user",
            "content": message
        })

        # Ollama로 응답 생성
        try:
            response = await self.ollama_service.chat(
                model=model,
                messages=context_messages
            )

            return {
                "response": response["message"]["content"],
                "related_memories": [
                    {
                        "memory_id": mem.get("id"),
                        "content": mem.get("memory", mem.get("content", "")),
                        "score": mem.get("score")
                    }
                    for mem in related_memories
                ],
                "model_used": model,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
