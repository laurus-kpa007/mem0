# Mem0 테스트 프로그램 구현 가이드

## 목차
1. [환경 준비](#1-환경-준비)
2. [백엔드 구현](#2-백엔드-구현)
3. [프론트엔드 구현](#3-프론트엔드-구현)
4. [Docker 설정](#4-docker-설정)
5. [테스트 및 실행](#5-테스트-및-실행)

---

## 1. 환경 준비

### 1.1 필수 소프트웨어
```bash
# Python 3.10+
python --version

# Node.js 18+
node --version
npm --version

# Docker & Docker Compose (선택사항)
docker --version
docker-compose --version

# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh
```

### 1.2 Ollama 모델 설치
```bash
# 기본 모델 다운로드
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# 추가 모델 (선택사항)
ollama pull mistral:latest
ollama pull gemma2:latest

# Ollama 서버 시작
ollama serve
```

### 1.3 프로젝트 디렉토리 생성
```bash
mkdir -p mem0-test-program
cd mem0-test-program

# 디렉토리 구조 생성
mkdir -p backend/app/{api,services,models,core}
mkdir -p backend/tests
mkdir -p frontend/src/{components/{Chat,Memory,Settings,Common},pages,services,stores,types,utils}
mkdir -p frontend/public
mkdir -p data
```

---

## 2. 백엔드 구현

### 2.1 의존성 설치

**backend/requirements.txt**
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
mem0ai==0.1.20
httpx==0.26.0
python-multipart==0.0.6
python-dotenv==1.0.0
qdrant-client==1.7.0
```

```bash
cd backend
pip install -r requirements.txt
```

### 2.2 설정 파일 작성

**backend/.env**
```bash
# Server
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
LOG_LEVEL=INFO

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# Mem0
VECTOR_STORE_PATH=../data/qdrant
HISTORY_DB_PATH=../data/memory_history.db

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**backend/app/config.py**
```python
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
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
```

### 2.3 데이터 모델 정의

**backend/app/models/memory.py**
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class MemoryAddRequest(BaseModel):
    content: str = Field(..., description="저장할 메모리 내용")
    user_id: str = Field(..., description="사용자 ID")
    metadata: Optional[Dict] = Field(default=None, description="추가 메타데이터")

class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="검색 쿼리")
    user_id: str = Field(..., description="사용자 ID")
    limit: int = Field(default=10, ge=1, le=50, description="결과 개수")

class MemoryResponse(BaseModel):
    memory_id: str
    content: str
    score: Optional[float] = None
    metadata: Optional[Dict] = None
    created_at: Optional[str] = None

class MemoryListResponse(BaseModel):
    memories: List[MemoryResponse]
    total: int
```

**backend/app/models/chat.py**
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    user_id: str = Field(..., description="사용자 ID")
    session_id: str = Field(..., description="세션 ID")
    model: str = Field(default="llama3.2:latest", description="사용할 모델")
    use_memory: bool = Field(default=True, description="메모리 사용 여부")
    memory_limit: int = Field(default=5, ge=0, le=20, description="사용할 메모리 개수")

class ChatResponse(BaseModel):
    response: str
    related_memories: List[Dict]
    model_used: str
    timestamp: str

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: str
    related_memories: Optional[List[Dict]] = None
```

**backend/app/models/ollama.py**
```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class OllamaModel(BaseModel):
    name: str
    size: str
    modified_at: str
    details: Optional[Dict] = None

class OllamaModelsResponse(BaseModel):
    models: List[OllamaModel]

class OllamaStatusResponse(BaseModel):
    status: str  # online, offline
    version: Optional[str] = None
```

### 2.4 서비스 레이어 구현

**backend/app/services/memory_service.py**
```python
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.configs.llms.base import LlmConfig
from mem0.configs.embedders.base import EmbedderConfig
from mem0.configs.vector_stores.base import VectorStoreConfig
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MemoryService:
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
```

**backend/app/services/ollama_service.py**
```python
import httpx
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OllamaService:
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
```

**backend/app/services/chat_service.py**
```python
from typing import List, Dict, Optional
from .memory_service import MemoryService
from .ollama_service import OllamaService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ChatService:
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
```

### 2.5 API 엔드포인트 구현

**backend/app/api/memory.py**
```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.memory import (
    MemoryAddRequest,
    MemorySearchRequest,
    MemoryResponse,
    MemoryListResponse
)
from app.services.memory_service import MemoryService
from app.dependencies import get_memory_service
from typing import List

router = APIRouter(prefix="/api/memory", tags=["memory"])

@router.post("/add")
async def add_memory(
    request: MemoryAddRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """메모리 추가"""
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_memories(
    query: str,
    user_id: str,
    limit: int = 10,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """메모리 검색"""
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_memories(
    user_id: str,
    limit: int = 50,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """전체 메모리 조회"""
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
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """메모리 삭제"""
    try:
        result = await memory_service.delete_memory(memory_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**backend/app/api/chat.py**
```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.dependencies import get_chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """대화 생성"""
    try:
        response = await chat_service.generate_response(
            message=request.message,
            user_id=request.user_id,
            model=request.model,
            use_memory=request.use_memory,
            memory_limit=request.memory_limit
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**backend/app/api/ollama.py**
```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.ollama import OllamaModelsResponse, OllamaStatusResponse
from app.services.ollama_service import OllamaService
from app.dependencies import get_ollama_service

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

@router.get("/models", response_model=OllamaModelsResponse)
async def list_models(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """사용 가능한 모델 목록"""
    try:
        models = await ollama_service.list_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=OllamaStatusResponse)
async def check_status(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """Ollama 서버 상태"""
    try:
        status = await ollama_service.check_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2.6 의존성 주입

**backend/app/dependencies.py**
```python
from app.services.memory_service import MemoryService
from app.services.ollama_service import OllamaService
from app.services.chat_service import ChatService
from app.config import settings
from functools import lru_cache

@lru_cache()
def get_memory_service() -> MemoryService:
    return MemoryService(
        ollama_base_url=settings.ollama_base_url,
        ollama_model=settings.ollama_default_model,
        embedding_model=settings.ollama_embedding_model,
        vector_store_path=settings.vector_store_path,
        history_db_path=settings.history_db_path
    )

@lru_cache()
def get_ollama_service() -> OllamaService:
    return OllamaService(base_url=settings.ollama_base_url)

def get_chat_service(
    memory_service: MemoryService = None,
    ollama_service: OllamaService = None
) -> ChatService:
    if memory_service is None:
        memory_service = get_memory_service()
    if ollama_service is None:
        ollama_service = get_ollama_service()
    return ChatService(memory_service, ollama_service)
```

### 2.7 메인 애플리케이션

**backend/app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import memory, chat, ollama
import logging

# 로깅 설정
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Mem0 Test Program API",
    description="Memory-based chat application with Ollama",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(memory.router)
app.include_router(chat.router)
app.include_router(ollama.router)

@app.get("/")
async def root():
    return {
        "message": "Mem0 Test Program API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    from app.dependencies import get_ollama_service

    ollama_service = get_ollama_service()
    ollama_status = await ollama_service.check_status()

    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "ollama": ollama_status["status"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
```

---

## 3. 프론트엔드 구현

### 3.1 프로젝트 초기화

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

### 3.2 의존성 설치

```bash
npm install axios zustand react-router-dom
npm install -D tailwindcss postcss autoprefixer
npm install lucide-react  # 아이콘
npx tailwindcss init -p
```

### 3.3 Tailwind CSS 설정

**frontend/tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**frontend/src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 3.4 TypeScript 타입 정의

**frontend/src/types/memory.ts**
```typescript
export interface Memory {
  id: string;
  memory: string;
  content?: string;
  score?: number;
  metadata?: Record<string, any>;
  created_at?: string;
}

export interface MemoryAddRequest {
  content: string;
  user_id: string;
  metadata?: Record<string, any>;
}

export interface MemorySearchParams {
  query: string;
  user_id: string;
  limit?: number;
}
```

**frontend/src/types/chat.ts**
```typescript
import { Memory } from './memory';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  related_memories?: Memory[];
}

export interface ChatRequest {
  message: string;
  user_id: string;
  session_id: string;
  model: string;
  use_memory: boolean;
  memory_limit: number;
}

export interface ChatResponse {
  response: string;
  related_memories: Memory[];
  model_used: string;
  timestamp: string;
}
```

**frontend/src/types/ollama.ts**
```typescript
export interface OllamaModel {
  name: string;
  size: string;
  modified_at: string;
  details?: Record<string, any>;
}

export interface OllamaStatus {
  status: 'online' | 'offline';
  version?: string;
}
```

### 3.5 API 서비스

**frontend/src/services/api.ts**
```typescript
import axios from 'axios';
import type { MemoryAddRequest, MemorySearchParams, Memory } from '../types/memory';
import type { ChatRequest, ChatResponse } from '../types/chat';
import type { OllamaModel, OllamaStatus } from '../types/ollama';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Memory APIs
export const memoryApi = {
  add: async (data: MemoryAddRequest) => {
    const response = await api.post('/api/memory/add', data);
    return response.data;
  },

  search: async (params: MemorySearchParams) => {
    const response = await api.get('/api/memory/search', { params });
    return response.data;
  },

  list: async (userId: string, limit = 50) => {
    const response = await api.get('/api/memory/list', {
      params: { user_id: userId, limit },
    });
    return response.data;
  },

  delete: async (memoryId: string) => {
    const response = await api.delete(`/api/memory/${memoryId}`);
    return response.data;
  },
};

// Chat APIs
export const chatApi = {
  send: async (data: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/api/chat', data);
    return response.data;
  },
};

// Ollama APIs
export const ollamaApi = {
  listModels: async (): Promise<{ models: OllamaModel[] }> => {
    const response = await api.get('/api/ollama/models');
    return response.data;
  },

  checkStatus: async (): Promise<OllamaStatus> => {
    const response = await api.get('/api/ollama/status');
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },
};

export default api;
```

### 3.6 상태 관리 (Zustand)

**frontend/src/stores/chatStore.ts**
```typescript
import { create } from 'zustand';
import type { ChatMessage } from '../types/chat';

interface ChatStore {
  messages: ChatMessage[];
  sessionId: string;
  isLoading: boolean;
  addMessage: (message: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
  setSessionId: (id: string) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  sessionId: `session_${Date.now()}`,
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  setLoading: (loading) => set({ isLoading: loading }),

  clearMessages: () => set({ messages: [] }),

  setSessionId: (id) => set({ sessionId: id }),
}));
```

**frontend/src/stores/memoryStore.ts**
```typescript
import { create } from 'zustand';
import type { Memory } from '../types/memory';

interface MemoryStore {
  memories: Memory[];
  isLoading: boolean;
  setMemories: (memories: Memory[]) => void;
  addMemory: (memory: Memory) => void;
  removeMemory: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useMemoryStore = create<MemoryStore>((set) => ({
  memories: [],
  isLoading: false,

  setMemories: (memories) => set({ memories }),

  addMemory: (memory) =>
    set((state) => ({ memories: [memory, ...state.memories] })),

  removeMemory: (id) =>
    set((state) => ({
      memories: state.memories.filter((m) => m.id !== id),
    })),

  setLoading: (loading) => set({ isLoading: loading }),
}));
```

**frontend/src/stores/settingsStore.ts**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsStore {
  userId: string;
  selectedModel: string;
  useMemory: boolean;
  memoryLimit: number;
  setUserId: (id: string) => void;
  setSelectedModel: (model: string) => void;
  setUseMemory: (use: boolean) => void;
  setMemoryLimit: (limit: number) => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      userId: 'user123',
      selectedModel: 'llama3.2:latest',
      useMemory: true,
      memoryLimit: 5,

      setUserId: (id) => set({ userId: id }),
      setSelectedModel: (model) => set({ selectedModel: model }),
      setUseMemory: (use) => set({ useMemory: use }),
      setMemoryLimit: (limit) => set({ memoryLimit: limit }),
    }),
    {
      name: 'mem0-settings',
    }
  )
);
```

### 3.7 주요 컴포넌트

프론트엔드 컴포넌트 코드는 분량상 생략하지만, 다음 컴포넌트들을 구현해야 합니다:

1. **Chat 관련**
   - `ChatView.tsx`: 메인 채팅 인터페이스
   - `MessageList.tsx`: 메시지 목록
   - `MessageInput.tsx`: 메시지 입력
   - `MemoryContext.tsx`: 관련 메모리 표시

2. **Memory 관련**
   - `MemoryManager.tsx`: 메모리 관리 페이지
   - `MemoryCard.tsx`: 메모리 카드
   - `AddMemoryForm.tsx`: 메모리 추가 폼
   - `MemorySearch.tsx`: 메모리 검색

3. **Settings 관련**
   - `ModelSelector.tsx`: 모델 선택
   - `SystemSettings.tsx`: 시스템 설정

4. **Common**
   - `Layout.tsx`: 레이아웃
   - `Header.tsx`: 헤더
   - `Sidebar.tsx`: 사이드바

---

## 4. Docker 설정

### 4.1 Backend Dockerfile

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Frontend Dockerfile

**frontend/Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 애플리케이션 복사
COPY . .

# 포트 노출
EXPOSE 5173

# 개발 서버 실행
CMD ["npm", "run", "dev", "--", "--host"]
```

### 4.3 Docker Compose

**docker-compose.yml**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: mem0-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: mem0-backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - PYTHONUNBUFFERED=1
    depends_on:
      - ollama
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: mem0-frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  ollama_data:
```

---

## 5. 테스트 및 실행

### 5.1 로컬 개발 환경

**백엔드 실행**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

**프론트엔드 실행**
```bash
cd frontend
npm install
npm run dev
```

### 5.2 Docker로 실행

```bash
# Ollama 모델 다운로드 (최초 1회)
docker-compose up -d ollama
docker exec -it mem0-ollama ollama pull llama3.2:latest
docker exec -it mem0-ollama ollama pull nomic-embed-text:latest

# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 5.3 테스트

**API 테스트**
```bash
# 헬스체크
curl http://localhost:8000/api/health

# 모델 목록
curl http://localhost:8000/api/ollama/models

# 메모리 추가
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "나는 파이썬 개발자입니다",
    "user_id": "user123"
  }'

# 채팅
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내 직업이 뭐지?",
    "user_id": "user123",
    "session_id": "test",
    "model": "llama3.2:latest",
    "use_memory": true,
    "memory_limit": 5
  }'
```

### 5.4 접속

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

---

## 6. 트러블슈팅

### 6.1 Ollama 연결 실패
```bash
# Ollama 서비스 확인
ollama serve

# 또는 Docker 확인
docker ps | grep ollama
docker logs mem0-ollama
```

### 6.2 메모리 저장 실패
```bash
# Qdrant 데이터 디렉토리 확인
ls -la data/qdrant

# 권한 문제 시
chmod -R 755 data/
```

### 6.3 CORS 에러
```python
# backend/app/config.py에서 CORS origins 확인
cors_origins: List[str] = [
    "http://localhost:5173",  # 프론트엔드 주소 추가
]
```

---

## 다음 단계

이 가이드를 따라 구현하면 기본적인 mem0 테스트 프로그램이 완성됩니다.
추가로 구현할 수 있는 기능들:

1. 스트리밍 응답
2. 대화 세션 저장/불러오기
3. 메모리 태그 시스템
4. Export/Import 기능
5. 통계 대시보드
6. 사용자 인증

각 기능은 모듈화되어 있어 점진적으로 추가할 수 있습니다.
