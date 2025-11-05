"""
Memory 관련 Pydantic 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class MemoryAddRequest(BaseModel):
    """메모리 추가 요청"""
    content: str = Field(..., description="저장할 메모리 내용", min_length=1)
    user_id: str = Field(..., description="사용자 ID")
    metadata: Optional[Dict] = Field(default=None, description="추가 메타데이터 (태그 포함)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "나는 파이썬 개발자입니다",
                "user_id": "user123",
                "metadata": {
                    "tags": ["개발", "파이썬"]
                }
            }
        }


class MemorySearchRequest(BaseModel):
    """메모리 검색 요청"""
    query: str = Field(..., description="검색 쿼리")
    user_id: str = Field(..., description="사용자 ID")
    limit: int = Field(default=10, ge=1, le=50, description="결과 개수")


class MemoryResponse(BaseModel):
    """메모리 응답"""
    memory_id: str
    content: str
    score: Optional[float] = None
    metadata: Optional[Dict] = None
    created_at: Optional[str] = None


class MemoryListResponse(BaseModel):
    """메모리 목록 응답"""
    memories: List[MemoryResponse]
    total: int


class TagSuggestionRequest(BaseModel):
    """태그 제안 요청"""
    content: str = Field(..., description="태그를 생성할 텍스트", min_length=1)
    max_tags: int = Field(default=5, ge=1, le=10, description="최대 태그 개수")
    language: str = Field(default="auto", description="태그 언어 (auto, ko, en)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "나는 서울에 살고 있고, 파이썬 개발자로 5년째 일하고 있습니다.",
                "max_tags": 5,
                "language": "ko"
            }
        }


class TagSuggestionResponse(BaseModel):
    """태그 제안 응답"""
    tags: List[str] = Field(..., description="제안된 태그 목록")
    confidence: Optional[float] = Field(None, description="신뢰도 (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "tags": ["개발", "파이썬", "서울", "직업", "백엔드"],
                "confidence": 0.92
            }
        }


class TagAutoCompleteRequest(BaseModel):
    """태그 자동완성 요청"""
    prefix: str = Field(..., description="태그 접두사", min_length=1)
    user_id: str = Field(..., description="사용자 ID")
    limit: int = Field(default=10, ge=1, le=20, description="결과 개수")


class TagAutoCompleteResponse(BaseModel):
    """태그 자동완성 응답"""
    suggestions: List[str] = Field(..., description="자동완성 제안")

    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": ["개발", "개발자", "개발환경"]
            }
        }


class TagStatsResponse(BaseModel):
    """태그 통계 응답"""
    tag: str
    count: int
    last_used: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "tag": "개발",
                "count": 25,
                "last_used": "2025-11-05T12:00:00Z"
            }
        }


class PopularTagsResponse(BaseModel):
    """인기 태그 응답"""
    tags: List[TagStatsResponse]
    total_tags: int

    class Config:
        json_schema_extra = {
            "example": {
                "tags": [
                    {"tag": "개발", "count": 25, "last_used": "2025-11-05T12:00:00Z"},
                    {"tag": "파이썬", "count": 20, "last_used": "2025-11-04T15:30:00Z"}
                ],
                "total_tags": 2
            }
        }
