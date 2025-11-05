"""
Ollama API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.ollama_service import OllamaService
from app.dependencies import get_ollama_service

router = APIRouter(prefix="/api/ollama")


class OllamaModel(BaseModel):
    """Ollama 모델 정보"""
    name: str
    size: Optional[str] = None
    modified_at: Optional[str] = None
    details: Optional[Dict] = None


class OllamaStatus(BaseModel):
    """Ollama 서버 상태"""
    status: str
    version: Optional[str] = None


@router.get("/models", summary="List available Ollama models")
async def list_models(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """
    사용 가능한 Ollama 모델 목록 조회 🤖

    Ollama 서버에서 다운로드된 모델 목록을 가져옵니다.

    **Returns:**
    - 모델 목록 (이름, 크기, 수정일 등)
    """
    try:
        models = await ollama_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch models: {str(e)}"
        )


@router.get("/status", response_model=OllamaStatus, summary="Check Ollama server status")
async def check_status(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """
    Ollama 서버 상태 확인 🔍

    Ollama 서버가 실행 중인지 확인합니다.

    **Returns:**
    - status: "online" 또는 "offline"
    - version: Ollama 버전 (온라인인 경우)
    """
    try:
        status = await ollama_service.check_status()
        return OllamaStatus(**status)
    except Exception as e:
        return OllamaStatus(status="offline")
