# Mem0 테스트 프로그램 설계 문서

## 1. 프로젝트 개요

Mem0와 Ollama를 통합한 지능형 메모리 기반 대화 시스템입니다. 사용자가 정보를 저장하고, 저장된 컨텍스트를 기반으로 자연스러운 대화를 나눌 수 있는 WebUI 애플리케이션입니다.

### 핵심 기능
- 📝 텍스트 기반 메모리 저장 (mem0)
- 🤖 Ollama 기반 LLM 모델 선택 및 대화
- 💬 저장된 메모리 기반 컨텍스트 응답
- 🌐 직관적인 Web UI (React/Vue)
- ⚡ FastAPI 백엔드 REST API
- 🔍 메모리 검색 및 관리

---

## 2. 시스템 아키텍처

### 2.1 전체 시스템 구조

```mermaid
graph TB
    subgraph Frontend["Frontend (React + TypeScript)"]
        ChatView[Chat View<br/>대화 인터페이스]
        MemoryView[Memory View<br/>메모리 관리]
        SettingsView[Settings View<br/>모델 선택]
    end

    subgraph Backend["Backend (FastAPI)"]
        API[API Endpoints<br/>REST API]

        subgraph Services["Service Layer"]
            MemService[Memory Service<br/>mem0 wrapper]
            ChatService[Chat Service<br/>대화 처리]
            OllamaService[Ollama Service<br/>LLM 통신]
        end
    end

    subgraph External["External Services"]
        subgraph Mem0["Mem0 Library"]
            VectorDB[(Qdrant<br/>Vector DB)]
            HistoryDB[(SQLite<br/>History)]
        end

        Ollama[Ollama Server<br/>llama3.2, mistral, gemma2]
    end

    %% Connections
    Frontend -->|REST API<br/>JSON| API
    API --> Services
    MemService --> Mem0
    ChatService --> MemService
    ChatService --> OllamaService
    OllamaService --> Ollama
    MemService --> Ollama

    style Frontend fill:#e1f5ff
    style Backend fill:#fff4e1
    style External fill:#f0f0f0
    style Mem0 fill:#e8f5e9
```

### 2.2 데이터 흐름

```mermaid
flowchart LR
    User([사용자]) --> UI[Web UI]
    UI -->|HTTP Request| API[FastAPI]
    API --> Service[Service Layer]
    Service -->|저장/검색| Vector[(Qdrant)]
    Service -->|LLM 호출| Ollama[Ollama]
    Service -->|히스토리| SQLite[(SQLite)]

    Vector -->|결과| Service
    Ollama -->|응답| Service
    Service -->|Response| API
    API -->|JSON| UI
    UI -->|화면 표시| User

    style User fill:#4CAF50
    style Vector fill:#2196F3
    style Ollama fill:#FF9800
    style SQLite fill:#9C27B0
```

### 2.3 계층별 구조

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[React Components]
        B[Zustand State]
        C[Axios HTTP Client]
    end

    subgraph "API Layer"
        D[FastAPI Endpoints]
        E[Pydantic Models]
    end

    subgraph "Business Logic Layer"
        F[Memory Service]
        G[Chat Service]
        H[Ollama Service]
    end

    subgraph "Data Layer"
        I[mem0 Library]
        J[Qdrant Vector DB]
        K[SQLite DB]
    end

    subgraph "External Layer"
        L[Ollama LLM Server]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    E --> H
    F --> I
    G --> F
    G --> H
    I --> J
    I --> K
    H --> L

    style A fill:#61dafb
    style D fill:#009688
    style F fill:#3f51b5
    style I fill:#4caf50
    style L fill:#ff9800
```

---

## 3. 기술 스택

### Backend
- **Framework**: FastAPI 0.100+
- **Memory Layer**: mem0 (with Ollama integration)
- **Vector DB**: Qdrant (embedded mode)
- **LLM**: Ollama (local)
- **Database**: SQLite (mem0 history)
- **Python**: 3.10+

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx (optional)
- **CORS**: Enabled for development

---

## 4. 데이터 모델

### 4.0 데이터 모델 관계도

```mermaid
erDiagram
    USER ||--o{ MEMORY : creates
    USER ||--o{ CHAT_SESSION : has
    CHAT_SESSION ||--o{ CHAT_MESSAGE : contains
    CHAT_MESSAGE }o--o{ MEMORY : references
    MEMORY ||--o{ MEMORY_HISTORY : tracks
    USER ||--o{ USER_SETTINGS : has

    USER {
        string user_id PK
        string name
        datetime created_at
    }

    MEMORY {
        string memory_id PK
        string user_id FK
        string content
        float[] embedding
        json metadata
        datetime created_at
    }

    MEMORY_HISTORY {
        string id PK
        string memory_id FK
        string old_memory
        string new_memory
        string event
        string actor_id
        datetime created_at
    }

    CHAT_SESSION {
        string session_id PK
        string user_id FK
        string title
        datetime created_at
        datetime updated_at
    }

    CHAT_MESSAGE {
        string message_id PK
        string session_id FK
        string role
        string content
        json related_memories
        datetime timestamp
    }

    USER_SETTINGS {
        string user_id PK
        string default_model
        int memory_limit
        boolean use_memory
        json preferences
    }
```

### 4.1 Memory Entry
```python
{
    "memory_id": "uuid",
    "content": "사용자가 저장한 텍스트 내용",
    "user_id": "user123",
    "metadata": {
        "tags": ["personal", "work"],
        "timestamp": "2025-11-05T12:00:00Z",
        "source": "manual_input"
    },
    "embedding": [0.123, 0.456, ...],  # 자동 생성
    "created_at": "2025-11-05T12:00:00Z"
}
```

### 4.2 Chat Message
```python
{
    "message_id": "uuid",
    "role": "user" | "assistant",
    "content": "메시지 내용",
    "user_id": "user123",
    "session_id": "session_abc",
    "timestamp": "2025-11-05T12:00:00Z",
    "related_memories": [  # 사용된 메모리 컨텍스트
        {
            "memory_id": "uuid",
            "content": "관련 메모리",
            "relevance_score": 0.89
        }
    ]
}
```

### 4.3 Ollama Model Info
```python
{
    "name": "llama3.2:latest",
    "size": "3.8GB",
    "modified_at": "2025-11-05T12:00:00Z",
    "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "3B"
    }
}
```

---

## 5. API 설계

### 5.0 API 엔드포인트 맵

```mermaid
graph TB
    FastAPI[FastAPI Server<br/>:8000]

    subgraph "Memory APIs"
        M1[POST /api/memory/add<br/>메모리 추가]
        M2[GET /api/memory/search<br/>메모리 검색]
        M3[GET /api/memory/list<br/>전체 메모리]
        M4[DELETE /api/memory/:id<br/>메모리 삭제]
    end

    subgraph "Chat APIs"
        C1[POST /api/chat<br/>대화 생성]
        C2[GET /api/chat/history<br/>대화 이력]
    end

    subgraph "Ollama APIs"
        O1[GET /api/ollama/models<br/>모델 목록]
        O2[POST /api/ollama/pull<br/>모델 다운로드]
        O3[GET /api/ollama/status<br/>서버 상태]
    end

    subgraph "Utility APIs"
        U1[GET /api/health<br/>헬스체크]
        U2[GET /api/stats<br/>통계]
    end

    FastAPI --> M1
    FastAPI --> M2
    FastAPI --> M3
    FastAPI --> M4
    FastAPI --> C1
    FastAPI --> C2
    FastAPI --> O1
    FastAPI --> O2
    FastAPI --> O3
    FastAPI --> U1
    FastAPI --> U2

    M1 -.->|사용| MemService[Memory Service]
    M2 -.->|사용| MemService
    M3 -.->|사용| MemService
    M4 -.->|사용| MemService

    C1 -.->|사용| ChatService[Chat Service]
    C2 -.->|사용| ChatService

    O1 -.->|사용| OllamaService[Ollama Service]
    O2 -.->|사용| OllamaService
    O3 -.->|사용| OllamaService

    style FastAPI fill:#009688
    style M1 fill:#4CAF50
    style M2 fill:#4CAF50
    style M3 fill:#4CAF50
    style M4 fill:#4CAF50
    style C1 fill:#2196F3
    style C2 fill:#2196F3
    style O1 fill:#FF9800
    style O2 fill:#FF9800
    style O3 fill:#FF9800
    style U1 fill:#9C27B0
    style U2 fill:#9C27B0
```

### 5.1 Memory Management APIs

#### POST /api/memory/add
메모리 추가
```json
Request:
{
    "content": "저장할 텍스트 내용",
    "user_id": "user123",
    "metadata": {
        "tags": ["work", "important"]
    }
}

Response:
{
    "success": true,
    "memory_id": "uuid",
    "message": "Memory added successfully"
}
```

#### GET /api/memory/search
메모리 검색
```json
Request Query Params:
?query=검색어&user_id=user123&limit=10

Response:
{
    "memories": [
        {
            "memory_id": "uuid",
            "content": "관련 메모리 내용",
            "score": 0.89,
            "metadata": {...}
        }
    ],
    "total": 5
}
```

#### GET /api/memory/list
전체 메모리 조회
```json
Request Query Params:
?user_id=user123&limit=50&offset=0

Response:
{
    "memories": [...],
    "total": 120,
    "limit": 50,
    "offset": 0
}
```

#### DELETE /api/memory/{memory_id}
메모리 삭제
```json
Response:
{
    "success": true,
    "message": "Memory deleted successfully"
}
```

### 5.2 Chat APIs

#### POST /api/chat
대화 생성
```json
Request:
{
    "message": "사용자 질문",
    "user_id": "user123",
    "session_id": "session_abc",
    "model": "llama3.2:latest",
    "use_memory": true,  // 메모리 컨텍스트 사용 여부
    "memory_limit": 5    // 사용할 메모리 개수
}

Response:
{
    "response": "AI 응답",
    "related_memories": [
        {
            "memory_id": "uuid",
            "content": "사용된 메모리",
            "score": 0.89
        }
    ],
    "model_used": "llama3.2:latest",
    "timestamp": "2025-11-05T12:00:00Z"
}
```

#### GET /api/chat/history
대화 이력 조회
```json
Request Query Params:
?user_id=user123&session_id=session_abc&limit=50

Response:
{
    "messages": [
        {
            "role": "user",
            "content": "질문",
            "timestamp": "..."
        },
        {
            "role": "assistant",
            "content": "응답",
            "related_memories": [...],
            "timestamp": "..."
        }
    ]
}
```

### 5.3 Ollama Integration APIs

#### GET /api/ollama/models
사용 가능한 모델 목록
```json
Response:
{
    "models": [
        {
            "name": "llama3.2:latest",
            "size": "3.8GB",
            "modified_at": "2025-11-05T12:00:00Z",
            "details": {...}
        }
    ]
}
```

#### POST /api/ollama/pull
새 모델 다운로드
```json
Request:
{
    "model_name": "mistral:latest"
}

Response (Streaming):
{
    "status": "downloading",
    "progress": 45.5,
    "message": "Downloading model..."
}
```

#### GET /api/ollama/status
Ollama 서버 상태 확인
```json
Response:
{
    "status": "online",
    "version": "0.1.20",
    "models_count": 3
}
```

### 5.4 Utility APIs

#### GET /api/health
헬스체크
```json
Response:
{
    "status": "healthy",
    "services": {
        "ollama": "online",
        "vector_db": "online",
        "memory": "online"
    }
}
```

#### GET /api/stats
통계 정보
```json
Response:
{
    "total_memories": 1250,
    "total_conversations": 89,
    "active_users": 5,
    "most_used_model": "llama3.2:latest"
}
```

---

## 6. Frontend 설계

### 6.1 페이지 구조

```mermaid
graph TB
    App[App.tsx<br/>메인 앱]

    subgraph "Pages"
        ChatPage[ChatPage<br/>'/chat']
        MemoriesPage[MemoriesPage<br/>'/memories']
        SettingsPage[SettingsPage<br/>'/settings']
        StatsPage[StatsPage<br/>'/stats']
    end

    subgraph "Chat Components"
        ChatView[ChatView<br/>채팅 인터페이스]
        MessageList[MessageList<br/>메시지 목록]
        MessageInput[MessageInput<br/>입력창]
        MemoryContext[MemoryContext<br/>메모리 표시]
    end

    subgraph "Memory Components"
        MemoryManager[MemoryManager<br/>메모리 관리]
        MemoryCard[MemoryCard<br/>메모리 카드]
        AddMemoryForm[AddMemoryForm<br/>추가 폼]
        MemorySearch[MemorySearch<br/>검색]
    end

    subgraph "Settings Components"
        ModelSelector[ModelSelector<br/>모델 선택]
        SystemSettings[SystemSettings<br/>시스템 설정]
    end

    subgraph "Common Components"
        Layout[Layout<br/>레이아웃]
        Header[Header<br/>헤더]
        Sidebar[Sidebar<br/>사이드바]
    end

    subgraph "State Management (Zustand)"
        ChatStore[chatStore<br/>대화 상태]
        MemoryStore[memoryStore<br/>메모리 상태]
        SettingsStore[settingsStore<br/>설정]
    end

    subgraph "Services"
        API[API Service<br/>Axios HTTP Client]
    end

    App --> Layout
    Layout --> Header
    Layout --> Sidebar
    Layout --> ChatPage
    Layout --> MemoriesPage
    Layout --> SettingsPage
    Layout --> StatsPage

    ChatPage --> ChatView
    ChatView --> MessageList
    ChatView --> MessageInput
    ChatView --> MemoryContext

    MemoriesPage --> MemoryManager
    MemoryManager --> MemoryCard
    MemoryManager --> AddMemoryForm
    MemoryManager --> MemorySearch

    SettingsPage --> ModelSelector
    SettingsPage --> SystemSettings

    ChatView -.->|useState| ChatStore
    MemoryManager -.->|useState| MemoryStore
    ModelSelector -.->|useState| SettingsStore

    ChatView -.->|API 호출| API
    MemoryManager -.->|API 호출| API
    ModelSelector -.->|API 호출| API

    style App fill:#61dafb
    style ChatStore fill:#764abc
    style MemoryStore fill:#764abc
    style SettingsStore fill:#764abc
    style API fill:#FF6B6B
```

### 6.1.1 라우팅 구조

```mermaid
graph LR
    Root["/"] --> Chat["/chat<br/>채팅 페이지"]
    Root --> Memories["/memories<br/>메모리 관리"]
    Root --> Settings["/settings<br/>설정"]
    Root --> Stats["/stats<br/>통계"]

    Chat --> Session["/chat/:sessionId<br/>특정 세션"]

    Settings --> Models["/settings/models<br/>모델 설정"]
    Settings --> System["/settings/system<br/>시스템 설정"]

    style Root fill:#4CAF50
    style Chat fill:#2196F3
    style Memories fill:#FF9800
    style Settings fill:#9C27B0
    style Stats fill:#F44336
```

### 6.2 주요 컴포넌트

#### ChatView
```typescript
interface ChatViewProps {
    userId: string;
    sessionId: string;
}

// 기능:
- 메시지 입력 및 전송
- 대화 히스토리 표시
- 사용된 메모리 컨텍스트 표시 (접을 수 있음)
- 스트리밍 응답 지원 (선택적)
- 모델 선택 드롭다운
```

#### MemoryManager
```typescript
interface MemoryManagerProps {
    userId: string;
}

// 기능:
- 새 메모리 추가 (텍스트 입력)
- 메모리 목록 표시 (카드 형태)
- 메모리 검색 (실시간 검색)
- 메모리 삭제/수정
- 태그 필터링
- 메모리 상세 보기
```

#### ModelSelector
```typescript
interface ModelSelectorProps {
    onModelSelect: (model: string) => void;
    currentModel: string;
}

// 기능:
- Ollama 모델 목록 표시
- 모델 정보 (크기, 파라미터 등)
- 현재 선택된 모델 하이라이트
- 새 모델 다운로드 기능
```

#### MemoryContext
```typescript
interface MemoryContextProps {
    memories: Memory[];
    expanded: boolean;
}

// 기능:
- 대화에 사용된 메모리 표시
- 관련도 점수 표시
- 확장/축소 토글
- 메모리 상세 보기 링크
```

### 6.3 UI/UX 특징

1. **실시간 피드백**
   - 메모리 추가 시 즉시 확인 메시지
   - 채팅 응답 로딩 인디케이터
   - 에러 처리 토스트 메시지

2. **반응형 디자인**
   - 모바일/태블릿/데스크톱 지원
   - 다크 모드 지원

3. **접근성**
   - 키보드 네비게이션
   - 스크린 리더 지원
   - ARIA 레이블

---

## 7. 프로젝트 구조

```
mem0-test-program/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 앱 진입점
│   │   ├── config.py               # 설정 관리
│   │   ├── dependencies.py         # 의존성 주입
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py           # Memory API endpoints
│   │   │   ├── chat.py             # Chat API endpoints
│   │   │   ├── ollama.py           # Ollama API endpoints
│   │   │   └── utils.py            # Utility endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── memory_service.py   # mem0 wrapper
│   │   │   ├── ollama_service.py   # Ollama integration
│   │   │   └── chat_service.py     # Chat orchestration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── memory.py           # Pydantic models for memory
│   │   │   ├── chat.py             # Pydantic models for chat
│   │   │   └── ollama.py           # Pydantic models for Ollama
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── exceptions.py       # Custom exceptions
│   │       └── logging.py          # Logging setup
│   ├── tests/
│   │   ├── test_memory.py
│   │   ├── test_chat.py
│   │   └── test_ollama.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatView.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── MemoryContext.tsx
│   │   │   ├── Memory/
│   │   │   │   ├── MemoryManager.tsx
│   │   │   │   ├── MemoryCard.tsx
│   │   │   │   ├── MemorySearch.tsx
│   │   │   │   └── AddMemoryForm.tsx
│   │   │   ├── Settings/
│   │   │   │   ├── ModelSelector.tsx
│   │   │   │   └── SystemSettings.tsx
│   │   │   └── Common/
│   │   │       ├── Layout.tsx
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx
│   │   │   ├── MemoriesPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   └── StatsPage.tsx
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   ├── stores/
│   │   │   ├── chatStore.ts
│   │   │   ├── memoryStore.ts
│   │   │   └── settingsStore.ts
│   │   ├── types/
│   │   │   ├── memory.ts
│   │   │   ├── chat.ts
│   │   │   └── ollama.ts
│   │   ├── utils/
│   │   │   └── helpers.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── README.md
└── DESIGN.md (this file)
```

---

## 8. 핵심 로직 설계

### 8.1 메모리 저장 플로우

#### 시퀀스 다이어그램: 메모리 저장

```mermaid
sequenceDiagram
    actor User as 사용자
    participant UI as Web UI
    participant API as FastAPI<br/>API Endpoint
    participant MemService as Memory<br/>Service
    participant Mem0 as mem0<br/>Library
    participant Ollama as Ollama<br/>LLM
    participant Vector as Qdrant<br/>Vector DB
    participant SQLite as SQLite<br/>History DB

    User->>UI: 텍스트 입력<br/>"나는 파이썬 개발자입니다"
    UI->>API: POST /api/memory/add<br/>{content, user_id}

    API->>MemService: add_memory()
    MemService->>Mem0: memory.add(messages, user_id)

    Note over Mem0: Step 1: Fact Extraction
    Mem0->>Ollama: LLM 호출 (FACT_RETRIEVAL_PROMPT)<br/>"Extract facts from text"
    Ollama-->>Mem0: Facts 반환<br/>["User is a Python developer"]

    Note over Mem0: Step 2: 중복 확인
    Mem0->>Vector: 기존 메모리 검색
    Vector-->>Mem0: 검색 결과

    Note over Mem0: Step 3: 임베딩 생성
    Mem0->>Ollama: 임베딩 생성 요청<br/>(nomic-embed-text)
    Ollama-->>Mem0: 임베딩 벡터<br/>[0.123, 0.456, ...]

    Note over Mem0: Step 4: Vector DB 저장
    Mem0->>Vector: 저장(memory, embedding, metadata)
    Vector-->>Mem0: memory_id

    Note over Mem0: Step 5: 히스토리 기록
    Mem0->>SQLite: 이벤트 기록<br/>(created, memory_id, content)
    SQLite-->>Mem0: 완료

    Mem0-->>MemService: 저장 결과<br/>{id, memory, event: "created"}
    MemService-->>API: 성공 응답
    API-->>UI: {success: true, results}
    UI-->>User: "메모리가 저장되었습니다"
```

#### 코드 구현

```python
# backend/app/services/memory_service.py

class MemoryService:
    def __init__(self):
        self.memory = Memory(
            config=MemoryConfig(
                llm=LlmConfig(
                    provider="ollama",
                    config={
                        "model": "llama3.2:latest",
                        "base_url": "http://ollama:11434"
                    }
                ),
                embedder=EmbedderConfig(
                    provider="ollama",
                    config={
                        "model": "nomic-embed-text:latest"
                    }
                ),
                vector_store=VectorStoreConfig(
                    provider="qdrant",
                    config={
                        "path": "./qdrant_data",
                        "collection_name": "mem0_memories"
                    }
                ),
                history_db_path="./memory_history.db"
            )
        )

    async def add_memory(
        self,
        content: str,
        user_id: str,
        metadata: dict = None
    ) -> dict:
        """
        메모리 추가
        1. mem0에 텍스트 전달
        2. mem0가 자동으로 fact extraction 수행
        3. 임베딩 생성 및 vector store에 저장
        4. SQLite history에 기록
        """
        result = self.memory.add(
            messages=[{"role": "user", "content": content}],
            user_id=user_id,
            metadata=metadata
        )
        return result

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> list:
        """
        메모리 검색
        1. 쿼리를 임베딩으로 변환
        2. Vector similarity search
        3. 관련도 높은 순으로 정렬
        """
        results = self.memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        return results
```

### 8.2 채팅 플로우 (메모리 통합)

#### 시퀀스 다이어그램: 메모리 기반 질의응답

```mermaid
sequenceDiagram
    actor User as 사용자
    participant UI as Web UI
    participant API as FastAPI<br/>API Endpoint
    participant ChatService as Chat<br/>Service
    participant MemService as Memory<br/>Service
    participant Mem0 as mem0<br/>Library
    participant Vector as Qdrant<br/>Vector DB
    participant Ollama as Ollama<br/>LLM

    User->>UI: 질문 입력<br/>"내 직업이 뭐지?"
    UI->>API: POST /api/chat<br/>{message, user_id, use_memory: true}

    API->>ChatService: generate_response()

    alt 메모리 사용 (use_memory = true)
        Note over ChatService: Step 1: 관련 메모리 검색
        ChatService->>MemService: search_memories(query, user_id, limit=5)
        MemService->>Mem0: memory.search(query)

        Mem0->>Ollama: 쿼리 임베딩 생성<br/>"내 직업이 뭐지?"
        Ollama-->>Mem0: 쿼리 벡터<br/>[0.234, 0.567, ...]

        Mem0->>Vector: 유사도 검색<br/>(vector_similarity)
        Vector-->>Mem0: 관련 메모리 목록<br/>[{memory: "User is a Python developer", score: 0.89}]

        Mem0-->>MemService: 검색 결과
        MemService-->>ChatService: related_memories[]
    end

    Note over ChatService: Step 2: 컨텍스트 메시지 구성
    ChatService->>ChatService: context_messages = [<br/>  {role: "system", content: "관련 정보: ..."},<br/>  {role: "user", content: "내 직업이 뭐지?"}]

    Note over ChatService: Step 3: LLM 응답 생성
    ChatService->>Ollama: POST /api/chat<br/>{model, messages}
    Note over Ollama: LLM 추론<br/>(llama3.2)
    Ollama-->>ChatService: 응답<br/>"당신은 파이썬 개발자입니다."

    Note over ChatService: Step 4: 응답 구성
    ChatService->>ChatService: response = {<br/>  response: "...",<br/>  related_memories: [...],<br/>  model_used: "llama3.2",<br/>  timestamp: "..."}

    ChatService-->>API: 응답 데이터
    API-->>UI: JSON Response
    UI-->>User: AI 응답 표시<br/>(+ 사용된 메모리 표시)

    Note over UI: 메모리 컨텍스트 표시<br/>"이 답변은 다음 메모리를 참고했습니다:<br/>- User is a Python developer (관련도: 89%)"
```

#### 데이터 흐름 비교

```mermaid
graph LR
    subgraph "Without Memory"
        Q1[질문: 내 직업이 뭐지?]
        Q1 --> LLM1[Ollama LLM]
        LLM1 --> A1[답변: 죄송하지만<br/>정보가 없습니다]
    end

    subgraph "With Memory"
        Q2[질문: 내 직업이 뭐지?]
        Q2 --> Search[메모리 검색]
        Search --> Found[발견: User is<br/>Python developer]
        Found --> Context[컨텍스트 추가]
        Context --> LLM2[Ollama LLM]
        LLM2 --> A2[답변: 당신은<br/>파이썬 개발자입니다]
    end

    style Q1 fill:#ffebee
    style A1 fill:#ffcdd2
    style Q2 fill:#e8f5e9
    style Search fill:#c8e6c9
    style Found fill:#a5d6a7
    style A2 fill:#81c784
```

#### 코드 구현

```python
# backend/app/services/chat_service.py

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
    ) -> dict:
        """
        메모리 기반 응답 생성
        1. 사용자 메시지로 관련 메모리 검색
        2. 검색된 메모리를 컨텍스트로 추가
        3. Ollama로 응답 생성
        4. 대화 내용을 메모리에 저장 (선택적)
        """
        related_memories = []

        if use_memory:
            # 관련 메모리 검색
            related_memories = await self.memory_service.search_memories(
                query=message,
                user_id=user_id,
                limit=memory_limit
            )

        # 컨텍스트 구성
        context_messages = []

        if related_memories:
            context = "관련 정보:\n"
            for mem in related_memories:
                context += f"- {mem['content']}\n"

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
        response = await self.ollama_service.chat(
            model=model,
            messages=context_messages
        )

        return {
            "response": response["message"]["content"],
            "related_memories": related_memories,
            "model_used": model
        }
```

### 8.3 Ollama 통합

#### Ollama 서비스 아키텍처

```mermaid
graph TB
    subgraph "FastAPI Backend"
        OllamaService[Ollama Service]
        MemService[Memory Service]
        ChatService[Chat Service]
    end

    subgraph "Ollama Server :11434"
        subgraph "LLM Models"
            Llama[llama3.2<br/>대화 생성]
            Mistral[mistral<br/>대화 생성]
            Gemma[gemma2<br/>대화 생성]
        end

        subgraph "Embedding Models"
            Nomic[nomic-embed-text<br/>임베딩 생성]
        end

        API_Tags["/api/tags<br/>모델 목록"]
        API_Chat["/api/chat<br/>채팅"]
        API_Embed["/api/embeddings<br/>임베딩"]
    end

    OllamaService -->|모델 목록| API_Tags
    OllamaService -->|채팅 요청| API_Chat
    MemService -->|임베딩 요청| API_Embed

    API_Chat --> Llama
    API_Chat --> Mistral
    API_Chat --> Gemma
    API_Embed --> Nomic

    ChatService --> OllamaService
    MemService --> OllamaService

    style OllamaService fill:#4CAF50
    style API_Chat fill:#FF9800
    style API_Embed fill:#2196F3
    style Llama fill:#E91E63
    style Nomic fill:#9C27B0
```

#### Ollama API 호출 시퀀스

```mermaid
sequenceDiagram
    participant Backend as Backend<br/>Service
    participant Ollama as Ollama<br/>Server
    participant Model as LLM<br/>Model

    Note over Backend,Model: 모델 목록 조회
    Backend->>Ollama: GET /api/tags
    Ollama-->>Backend: {models: [llama3.2, mistral, ...]}

    Note over Backend,Model: 채팅 요청
    Backend->>Ollama: POST /api/chat<br/>{model: "llama3.2", messages: [...]}
    Ollama->>Model: 모델 로드 (최초 1회)
    Note over Model: 토큰 생성
    Model-->>Ollama: 생성된 응답
    Ollama-->>Backend: {message: {content: "..."}}

    Note over Backend,Model: 임베딩 생성
    Backend->>Ollama: POST /api/embeddings<br/>{model: "nomic-embed-text", prompt: "..."}
    Ollama->>Model: 임베딩 모델 실행
    Note over Model: 벡터 생성
    Model-->>Ollama: 임베딩 벡터
    Ollama-->>Backend: {embedding: [0.1, 0.2, ...]}
```

#### 코드 구현

```python
# backend/app/services/ollama_service.py

import httpx

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def list_models(self) -> list:
        """사용 가능한 모델 목록 조회"""
        response = await self.client.get(f"{self.base_url}/api/tags")
        return response.json()["models"]

    async def chat(
        self,
        model: str,
        messages: list,
        stream: bool = False
    ) -> dict:
        """채팅 API 호출"""
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": stream
            }
        )
        return response.json()

    async def check_status(self) -> dict:
        """Ollama 서버 상태 확인"""
        try:
            response = await self.client.get(f"{self.base_url}/api/version")
            return {
                "status": "online",
                "version": response.json()["version"]
            }
        except Exception:
            return {"status": "offline"}
```

---

## 9. 추가 기능 제안

### 9.1 대화 세션 관리
- 세션별 대화 이력 저장
- 세션 간 전환
- 세션 삭제/아카이브

### 9.2 메모리 자동 저장
- 중요한 대화 내용을 자동으로 메모리에 저장
- 사용자 승인 옵션

### 9.3 메모리 태그 시스템
- 메모리에 태그 추가/관리
- 태그별 필터링 및 검색

### 9.4 Export/Import 기능
- 메모리를 JSON/CSV로 내보내기
- 외부 데이터 가져오기

### 9.5 멀티 유저 지원
- 유저별 메모리 격리
- 간단한 인증 시스템

### 9.6 메모리 분석 대시보드
- 가장 많이 참조된 메모리
- 메모리 증가 추세
- 모델별 사용 통계

### 9.7 임베딩 모델 선택
- 다양한 임베딩 모델 지원
- 임베딩 품질 비교

### 9.8 스트리밍 응답
- 실시간 응답 스트리밍
- 사용자 경험 개선

---

## 10. 환경 설정

### 10.1 필수 환경 변수

```bash
# .env
# Backend
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest

# Mem0
VECTOR_STORE_PATH=./data/qdrant
HISTORY_DB_PATH=./data/memory_history.db
EMBEDDING_MODEL=nomic-embed-text:latest

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_USER_ID=user123

# Optional
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 10.2 Docker Compose 구성

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - mem0_data:/app/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    restart: unless-stopped

  frontend:
    build: ./frontend
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
  mem0_data:
```

---

## 11. 개발 로드맵

### Phase 1: 기본 기능 구현 (1-2주)
- [ ] FastAPI 백엔드 기본 구조
- [ ] mem0 통합 및 메모리 CRUD
- [ ] Ollama 통합 및 모델 목록
- [ ] 기본 채팅 API
- [ ] React 프론트엔드 기본 구조
- [ ] 채팅 UI 컴포넌트
- [ ] 메모리 관리 UI

### Phase 2: 고급 기능 (1주)
- [ ] 메모리 검색 최적화
- [ ] 컨텍스트 기반 응답 개선
- [ ] 세션 관리
- [ ] 태그 시스템
- [ ] 스트리밍 응답

### Phase 3: UX 개선 및 부가 기능 (1주)
- [ ] 통계 대시보드
- [ ] Export/Import
- [ ] 다크 모드
- [ ] 반응형 디자인 완성
- [ ] 에러 처리 강화

### Phase 4: 테스트 및 문서화 (3-5일)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] API 문서 (Swagger)
- [ ] 사용자 가이드
- [ ] 배포 가이드

---

## 12. 성능 고려사항

1. **벡터 검색 최적화**
   - Qdrant 인덱스 튜닝
   - 적절한 similarity threshold 설정

2. **응답 시간 개선**
   - 메모리 검색과 LLM 호출 병렬 처리
   - 캐싱 전략

3. **확장성**
   - Qdrant를 외부 서비스로 분리 가능
   - 메모리 분산 저장 고려

4. **리소스 관리**
   - Ollama 모델 메모리 사용량 모니터링
   - 불필요한 모델 언로드

---

## 13. 보안 고려사항

1. **API 보안**
   - CORS 적절히 설정
   - Rate limiting 구현
   - 입력 검증 및 sanitization

2. **데이터 보안**
   - 민감 정보 저장 주의
   - 사용자별 데이터 격리
   - 암호화 고려 (선택적)

3. **인증/인가**
   - 간단한 토큰 기반 인증
   - 사용자 세션 관리

---

## 14. 모니터링 및 로깅

1. **로깅 전략**
   - 구조화된 로깅 (JSON)
   - 로그 레벨 적절히 사용
   - 민감 정보 로그 제외

2. **메트릭 수집**
   - API 응답 시간
   - 메모리 사용량
   - 에러 발생률

3. **헬스체크**
   - Ollama 서버 상태
   - Vector DB 상태
   - 디스크 공간

---

## 결론

이 설계는 mem0와 Ollama를 활용한 실용적인 메모리 기반 대화 시스템의 청사진입니다.
모듈화된 구조로 각 컴포넌트를 독립적으로 개발하고 테스트할 수 있으며,
필요에 따라 기능을 확장하거나 수정할 수 있습니다.

핵심은 mem0의 강력한 메모리 관리 기능과 Ollama의 로컬 LLM을 통합하여
사용자에게 개인화되고 컨텍스트를 이해하는 AI 어시스턴트를 제공하는 것입니다.
