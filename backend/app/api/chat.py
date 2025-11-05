"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service

router = APIRouter(prefix="/api/chat")


class ChatRequest(BaseModel):
    """채팅 요청"""
    message: str = Field(..., description="사용자 메시지", min_length=1)
    user_id: str = Field(..., description="사용자 ID")
    session_id: str = Field(..., description="세션 ID")
    model: str = Field(default="llama3.2:latest", description="사용할 LLM 모델")
    use_memory: bool = Field(default=True, description="메모리 사용 여부")
    memory_limit: int = Field(default=5, ge=1, le=20, description="검색할 메모리 수")


class MemoryInfo(BaseModel):
    """메모리 정보"""
    memory_id: Optional[str] = None
    content: str
    score: Optional[float] = None


class ChatResponse(BaseModel):
    """채팅 응답"""
    response: str = Field(..., description="AI 응답")
    related_memories: List[MemoryInfo] = Field(default_factory=list, description="관련 메모리")
    model_used: str = Field(..., description="사용된 모델")
    timestamp: str = Field(..., description="응답 타임스탬프")


@router.post("", response_model=ChatResponse, summary="Send chat message")
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    메모리 기반 채팅 메시지 전송 💬

    사용자의 메시지를 받아 관련 메모리를 검색하고,
    LLM을 사용하여 컨텍스트 기반 응답을 생성합니다.

    **Parameters:**
    - **message**: 사용자 메시지
    - **user_id**: 사용자 식별자
    - **session_id**: 세션 식별자
    - **model**: Ollama 모델 이름 (예: llama3.2:latest)
    - **use_memory**: 메모리 사용 여부
    - **memory_limit**: 검색할 메모리 개수 (1-20)

    **Returns:**
    - AI 응답 메시지
    - 관련된 메모리 목록
    - 사용된 모델 정보
    - 타임스탬프
    """
    try:
        result = await chat_service.generate_response(
            message=request.message,
            user_id=request.user_id,
            model=request.model,
            use_memory=request.use_memory,
            memory_limit=request.memory_limit,
        )

        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
