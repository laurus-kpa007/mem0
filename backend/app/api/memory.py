"""
Memory 관련 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from app.models.memory import (
    MemoryAddRequest,
    MemorySearchRequest,
    MemoryResponse,
    MemoryListResponse,
    TagSuggestionRequest,
    TagSuggestionResponse,
    TagAutoCompleteRequest,
    TagAutoCompleteResponse,
    PopularTagsResponse
)
from app.services.memory_service import MemoryService
from app.services.tag_service import TagService
from app.dependencies import get_memory_service, get_ollama_service, get_tag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory", tags=["memory"])


# ============================================================================
# Memory CRUD APIs
# ============================================================================

@router.post("/add")
async def add_memory(
    request: MemoryAddRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    메모리 추가

    텍스트를 mem0에 저장합니다. mem0가 자동으로 fact extraction을 수행하고
    임베딩을 생성하여 vector DB에 저장합니다.

    - **content**: 저장할 텍스트 내용
    - **user_id**: 사용자 ID
    - **metadata**: 추가 메타데이터 (선택사항)
        - **tags**: 태그 목록 (예: ["개발", "파이썬"])
    """
    try:
        result = await memory_service.add_memory(
            content=request.content,
            user_id=request.user_id,
            metadata=request.metadata
        )
        return {
            "success": True,
            "results": result
        }
    except Exception as e:
        logger.error(f"Error adding memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_memories(
    query: str = Query(..., description="검색 쿼리"),
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(10, ge=1, le=50, description="결과 개수"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    메모리 검색

    쿼리와 의미적으로 유사한 메모리를 검색합니다.
    Vector similarity search를 사용하여 관련도가 높은 순으로 정렬됩니다.

    - **query**: 검색 쿼리
    - **user_id**: 사용자 ID
    - **limit**: 반환할 결과 개수 (기본: 10, 최대: 50)
    """
    try:
        results = await memory_service.search_memories(
            query=query,
            user_id=user_id,
            limit=limit
        )
        return {
            "memories": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_memories(
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(50, ge=1, le=100, description="결과 개수"),
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    전체 메모리 조회

    사용자의 모든 메모리를 조회합니다.

    - **user_id**: 사용자 ID
    - **limit**: 반환할 결과 개수 (기본: 50, 최대: 100)
    """
    try:
        results = await memory_service.get_all_memories(
            user_id=user_id,
            limit=limit
        )
        return {
            "memories": results,
            "total": len(results)
        }
    except Exception as e:
        logger.error(f"Error listing memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """
    메모리 삭제

    특정 메모리를 삭제합니다.

    - **memory_id**: 삭제할 메모리 ID
    """
    try:
        result = await memory_service.delete_memory(memory_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tag APIs
# ============================================================================

@router.post("/suggest-tags", response_model=TagSuggestionResponse)
async def suggest_tags(
    request: TagSuggestionRequest,
    tag_service: TagService = Depends(get_tag_service)
):
    """
    태그 자동 제안 🏷️

    텍스트 내용을 분석하여 적절한 태그를 자동으로 제안합니다.
    LLM을 사용하여 텍스트의 핵심 주제와 카테고리를 추출합니다.

    **사용 예시:**
    1. 사용자가 메모리 입력
    2. "태그 제안" 버튼 클릭
    3. 이 API 호출하여 태그 목록 받기
    4. 사용자가 태그 선택/수정/추가
    5. 최종 태그와 함께 메모리 저장

    **Parameters:**
    - **content**: 분석할 텍스트
    - **max_tags**: 최대 태그 개수 (기본: 5, 최대: 10)
    - **language**: 태그 언어
        - "auto": 자동 감지 (기본)
        - "ko": 한글
        - "en": 영어

    **Returns:**
    - **tags**: 제안된 태그 목록
    - **confidence**: 신뢰도 점수 (0.0-1.0)
    """
    try:
        result = await tag_service.suggest_tags(
            content=request.content,
            max_tags=request.max_tags,
            language=request.language
        )
        return TagSuggestionResponse(
            tags=result["tags"],
            confidence=result.get("confidence")
        )
    except Exception as e:
        logger.error(f"Error suggesting tags: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"태그 생성 실패: {str(e)}"
        )


@router.get("/tags/autocomplete", response_model=TagAutoCompleteResponse)
async def autocomplete_tags(
    prefix: str = Query(..., description="태그 접두사", min_length=1),
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(10, ge=1, le=20, description="결과 개수"),
    tag_service: TagService = Depends(get_tag_service)
):
    """
    태그 자동완성

    사용자가 입력한 접두사로 시작하는 기존 태그를 제안합니다.
    사용자가 이전에 사용한 태그를 기반으로 자동완성을 제공합니다.

    **사용 예시:**
    - 사용자가 "개" 입력 → ["개발", "개발자", "개발환경"] 제안
    - 사용자가 "py" 입력 → ["python", "pytorch"] 제안

    **Parameters:**
    - **prefix**: 태그 접두사
    - **user_id**: 사용자 ID
    - **limit**: 반환할 제안 개수 (기본: 10)
    """
    try:
        suggestions = await tag_service.autocomplete_tags(
            prefix=prefix,
            user_id=user_id,
            limit=limit
        )
        return TagAutoCompleteResponse(suggestions=suggestions)
    except Exception as e:
        logger.error(f"Error autocompleting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/popular", response_model=PopularTagsResponse)
async def get_popular_tags(
    user_id: str = Query(..., description="사용자 ID"),
    limit: int = Query(10, ge=1, le=50, description="결과 개수"),
    tag_service: TagService = Depends(get_tag_service)
):
    """
    인기 태그 조회

    사용자가 가장 많이 사용한 태그를 조회합니다.
    빈도수와 최근 사용 시간을 포함합니다.

    **사용 예시:**
    - 대시보드에서 인기 태그 표시
    - 태그 선택 시 자주 사용하는 태그 우선 표시

    **Parameters:**
    - **user_id**: 사용자 ID
    - **limit**: 반환할 태그 개수 (기본: 10)

    **Returns:**
    - **tags**: 태그 목록 (빈도순 정렬)
        - **tag**: 태그명
        - **count**: 사용 횟수
        - **last_used**: 마지막 사용 시간
    - **total_tags**: 전체 태그 개수
    """
    try:
        tags = await tag_service.get_popular_tags(
            user_id=user_id,
            limit=limit
        )
        return PopularTagsResponse(
            tags=tags,
            total_tags=len(tags)
        )
    except Exception as e:
        logger.error(f"Error getting popular tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))
