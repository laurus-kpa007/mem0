"""
Ollama 서비스
"""
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Ollama API 통신 서비스"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)

    async def list_models(self) -> List[Dict]:
        """사용 가능한 모델 목록 조회"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise

    async def chat(
        self,
        model: str,
        messages: List[Dict],
        stream: bool = False
    ) -> Dict:
        """채팅 API 호출"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": stream
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            raise

    async def check_status(self) -> Dict:
        """Ollama 서버 상태 확인"""
        try:
            response = await self.client.get(f"{self.base_url}/api/version")
            response.raise_for_status()
            version_data = response.json()
            return {
                "status": "online",
                "version": version_data.get("version", "unknown")
            }
        except Exception:
            return {"status": "offline"}

    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()
