# Mem0 테스트 프로그램 - 프로젝트 요약

## 프로젝트 개요

이 프로젝트는 **mem0 메모리 솔루션**과 **Ollama LLM**을 통합한 메모리 기반 대화 시스템입니다.

### 핵심 가치

1. **컨텍스트 기억**: 사용자와의 대화 내용을 장기 메모리로 저장
2. **로컬 우선**: Ollama를 사용한 완전한 로컬 실행 (프라이버시 보호)
3. **확장 가능**: 모듈화된 구조로 쉬운 기능 추가
4. **사용자 친화적**: 직관적인 WebUI 제공

---

## 아키텍처 요약

```
┌─────────────┐
│   React     │ Frontend (Port 5173)
│   WebUI     │ - Chat Interface
└──────┬──────┘ - Memory Management
       │        - Settings
       │ HTTP/REST API
┌──────▼──────┐
│   FastAPI   │ Backend (Port 8000)
│   Server    │ - Memory CRUD APIs
└──┬────────┬─┘ - Chat APIs
   │        │   - Ollama Integration
   │        │
┌──▼───┐ ┌──▼─────────┐
│ mem0 │ │  Ollama    │
│      │ │  (Port     │
└──┬───┘ │   11434)   │
   │     └────────────┘
   │
┌──▼────────────┐
│   Qdrant      │ Vector Database
│   (embedded)  │ - Semantic Search
└───────────────┘ - Memory Storage
```

---

## 주요 컴포넌트

### 1. Backend (FastAPI)

**위치**: `backend/`

**핵심 모듈**:
- **MemoryService**: mem0 래퍼, 메모리 CRUD 담당
- **OllamaService**: Ollama API 통신
- **ChatService**: 메모리 기반 대화 로직

**API 엔드포인트**:
```
POST   /api/memory/add      # 메모리 추가
GET    /api/memory/search   # 메모리 검색
GET    /api/memory/list     # 전체 메모리
DELETE /api/memory/{id}     # 메모리 삭제

POST   /api/chat            # 대화 생성

GET    /api/ollama/models   # 모델 목록
GET    /api/ollama/status   # 서버 상태

GET    /api/health          # 헬스체크
```

### 2. Frontend (React + TypeScript)

**위치**: `frontend/`

**주요 페이지**:
- **Chat Page**: 메인 대화 인터페이스
- **Memories Page**: 메모리 관리
- **Settings Page**: 모델 선택 및 설정

**상태 관리 (Zustand)**:
- `chatStore`: 대화 메시지 및 세션
- `memoryStore`: 메모리 목록
- `settingsStore`: 사용자 설정 (모델, userId 등)

### 3. Mem0 통합

**기능**:
- 자동 Fact Extraction (LLM 기반)
- Vector Embedding 생성
- Semantic Search (유사도 기반)
- History Tracking (SQLite)

**저장 플로우**:
```
텍스트 입력
  ↓
LLM Fact Extraction
  ↓
Embedding 생성
  ↓
Qdrant 저장
  ↓
SQLite History 기록
```

### 4. Ollama 통합

**지원 모델**:
- llama3.2 (기본)
- mistral
- gemma2
- 기타 Ollama 모델

**임베딩 모델**:
- nomic-embed-text (기본)

---

## 데이터 흐름

### 메모리 저장 플로우

```
사용자가 "나는 파이썬 개발자입니다" 입력
  ↓
POST /api/memory/add
  ↓
MemoryService.add_memory()
  ↓
mem0.add() - LLM이 fact 추출
  ↓
Ollama로 임베딩 생성
  ↓
Qdrant에 vector 저장
  ↓
SQLite에 history 기록
  ↓
성공 응답
```

### 대화 생성 플로우

```
사용자가 "내 직업이 뭐지?" 질문
  ↓
POST /api/chat
  ↓
ChatService.generate_response()
  ↓
1. MemoryService.search_memories("내 직업이 뭐지?")
   - 쿼리를 임베딩으로 변환
   - Qdrant에서 유사 메모리 검색
   - 결과: ["나는 파이썬 개발자입니다" (score: 0.89)]
  ↓
2. 컨텍스트 메시지 구성
   - System: "관련 정보: 나는 파이썬 개발자입니다"
   - User: "내 직업이 뭐지?"
  ↓
3. OllamaService.chat(model, messages)
   - Ollama API 호출
   - 응답 생성: "당신은 파이썬 개발자입니다."
  ↓
4. 응답 반환
   - 응답 텍스트
   - 사용된 메모리 목록
   - 메타데이터 (모델, 타임스탬프)
```

---

## 기술 스택 정리

| 계층 | 기술 | 역할 |
|------|------|------|
| Frontend | React 18 + TypeScript | UI 프레임워크 |
| Frontend | Zustand | 상태 관리 |
| Frontend | Tailwind CSS | 스타일링 |
| Frontend | Axios | HTTP 클라이언트 |
| Backend | FastAPI | REST API 서버 |
| Backend | Pydantic | 데이터 검증 |
| Memory | mem0 | 메모리 관리 |
| Vector DB | Qdrant | 벡터 검색 |
| History DB | SQLite | 변경 이력 |
| LLM | Ollama | 로컬 LLM 서버 |
| Embedding | Ollama (nomic-embed-text) | 텍스트 임베딩 |
| DevOps | Docker Compose | 컨테이너 오케스트레이션 |

---

## 파일 구조

```
mem0-test-program/
├── 📋 README.md                    # Quick Start
├── 📘 DESIGN.md                    # 상세 설계
├── 🛠️  IMPLEMENTATION_GUIDE.md     # 구현 가이드
├── 📊 PROJECT_SUMMARY.md           # 이 문서
├── ⚙️  .env.example                 # 환경 변수 예제
├── 🚀 setup.sh                     # 프로젝트 초기화
├── 🤖 setup-ollama.sh              # Ollama 모델 설치
├── 🐳 docker-compose.yml           # Docker 구성
│
├── backend/                        # FastAPI 백엔드
│   ├── app/
│   │   ├── api/                    # API 엔드포인트
│   │   │   ├── memory.py
│   │   │   ├── chat.py
│   │   │   └── ollama.py
│   │   ├── services/               # 비즈니스 로직
│   │   │   ├── memory_service.py
│   │   │   ├── chat_service.py
│   │   │   └── ollama_service.py
│   │   ├── models/                 # Pydantic 모델
│   │   │   ├── memory.py
│   │   │   ├── chat.py
│   │   │   └── ollama.py
│   │   ├── core/
│   │   │   └── exceptions.py
│   │   ├── config.py               # 설정
│   │   ├── dependencies.py         # DI
│   │   └── main.py                 # 앱 진입점
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/               # 채팅 UI
│   │   │   ├── Memory/             # 메모리 관리 UI
│   │   │   ├── Settings/           # 설정 UI
│   │   │   └── Common/             # 공통 컴포넌트
│   │   ├── pages/                  # 페이지
│   │   ├── services/
│   │   │   └── api.ts              # API 클라이언트
│   │   ├── stores/                 # Zustand 스토어
│   │   │   ├── chatStore.ts
│   │   │   ├── memoryStore.ts
│   │   │   └── settingsStore.ts
│   │   ├── types/                  # TypeScript 타입
│   │   │   ├── memory.ts
│   │   │   ├── chat.ts
│   │   │   └── ollama.ts
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
└── data/                           # 데이터 저장소 (gitignore)
    ├── qdrant/                     # Vector DB
    └── memory_history.db           # SQLite
```

---

## 환경 변수

### Backend (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# Mem0
VECTOR_STORE_PATH=./data/qdrant
HISTORY_DB_PATH=./data/memory_history.db

# Server
BACKEND_PORT=8000
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_USER_ID=user123
```

---

## 실행 방법

### 옵션 1: Docker (권장)

```bash
# 1. Ollama 시작 및 모델 다운로드
docker-compose up -d ollama
docker exec -it mem0-ollama ollama pull llama3.2:latest
docker exec -it mem0-ollama ollama pull nomic-embed-text:latest

# 2. 전체 서비스 시작
docker-compose up -d

# 3. 접속
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
```

### 옵션 2: 로컬 개발

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

---

## API 사용 예제

### 1. 메모리 추가

```bash
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "나는 서울에 살고 있고, 파이썬 개발자로 일하고 있습니다. FastAPI를 즐겨 사용합니다.",
    "user_id": "user123",
    "metadata": {
      "tags": ["personal", "work"]
    }
  }'
```

응답:
```json
{
  "success": true,
  "results": [
    {
      "id": "mem_abc123",
      "memory": "User lives in Seoul",
      ...
    },
    {
      "id": "mem_def456",
      "memory": "User is a Python developer",
      ...
    },
    {
      "id": "mem_ghi789",
      "memory": "User enjoys using FastAPI",
      ...
    }
  ]
}
```

> **참고**: mem0가 입력 텍스트에서 자동으로 3개의 독립적인 fact를 추출했습니다.

### 2. 메모리 검색

```bash
curl "http://localhost:8000/api/memory/search?query=직업&user_id=user123&limit=5"
```

응답:
```json
{
  "memories": [
    {
      "id": "mem_def456",
      "memory": "User is a Python developer",
      "score": 0.89
    },
    {
      "id": "mem_ghi789",
      "memory": "User enjoys using FastAPI",
      "score": 0.76
    }
  ],
  "total": 2
}
```

### 3. 대화 생성 (메모리 사용)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내가 사는 곳은 어디고, 무슨 일을 하지?",
    "user_id": "user123",
    "session_id": "session_001",
    "model": "llama3.2:latest",
    "use_memory": true,
    "memory_limit": 5
  }'
```

응답:
```json
{
  "response": "당신은 서울에 살고 있으며, 파이썬 개발자로 일하고 계십니다. 특히 FastAPI 프레임워크를 즐겨 사용하신다고 하셨네요.",
  "related_memories": [
    {
      "memory_id": "mem_abc123",
      "content": "User lives in Seoul",
      "score": 0.91
    },
    {
      "memory_id": "mem_def456",
      "content": "User is a Python developer",
      "score": 0.88
    },
    {
      "memory_id": "mem_ghi789",
      "content": "User enjoys using FastAPI",
      "score": 0.72
    }
  ],
  "model_used": "llama3.2:latest",
  "timestamp": "2025-11-05T12:34:56.789Z"
}
```

---

## 핵심 기능 상세

### 1. 자동 Fact Extraction

mem0는 입력된 텍스트에서 LLM을 사용하여 자동으로 개별 fact를 추출합니다:

**입력**:
```
"나는 서울에 살고, 파이썬 개발자이며, 고양이를 좋아합니다."
```

**추출된 Facts**:
1. "User lives in Seoul"
2. "User is a Python developer"
3. "User likes cats"

각 fact는 독립적으로 저장되어 더 정확한 검색이 가능합니다.

### 2. Semantic Search

Vector embedding을 사용한 의미론적 검색:

**쿼리**: "내 직업은?"
**매칭**: "User is a Python developer" (score: 0.89)

단순 키워드 매칭이 아닌 의미 기반 검색으로 더 정확한 결과를 제공합니다.

### 3. Context-Aware Responses

관련 메모리를 컨텍스트로 제공하여 LLM이 더 정확한 답변을 생성:

```python
# 내부 처리 과정
context_messages = [
    {
        "role": "system",
        "content": "관련 정보:\n- User lives in Seoul\n- User is a Python developer"
    },
    {
        "role": "user",
        "content": "내가 어디 살지?"
    }
]
# → Ollama가 컨텍스트를 참고하여 "당신은 서울에 살고 있습니다" 응답
```

### 4. History Tracking

모든 메모리 변경 사항을 SQLite에 기록:

```sql
-- memory_history 테이블
id | memory_id | old_memory | new_memory | event | created_at
-------------------------------------------------------------------
1  | mem_abc   | NULL       | "User..."  | created | 2025-11-05...
2  | mem_abc   | "User..."  | "User..."  | updated | 2025-11-05...
```

이를 통해 메모리 변경 이력 추적 및 감사가 가능합니다.

---

## 확장 가능성

### Phase 1 완료 (기본 기능)
- [x] 메모리 CRUD
- [x] Ollama 통합
- [x] 기본 채팅
- [x] API 설계

### Phase 2 개발 예정
- [ ] WebUI 구현
- [ ] 스트리밍 응답
- [ ] 세션 관리
- [ ] 메모리 태그 시스템

### Phase 3 확장 기능
- [ ] 다중 사용자 지원
- [ ] 인증/인가
- [ ] 통계 대시보드
- [ ] Export/Import
- [ ] 멀티모달 지원 (이미지, PDF)

---

## 성능 특징

### 장점
1. **로컬 실행**: 모든 처리가 로컬에서 이루어져 프라이버시 보호
2. **빠른 검색**: Vector DB를 통한 밀리초 단위 검색
3. **확장 가능**: 모듈화된 구조로 쉬운 확장
4. **메모리 효율**: Qdrant embedded mode로 낮은 메모리 사용

### 고려사항
1. **초기 응답 시간**: 첫 요청 시 모델 로딩으로 인한 지연 가능
2. **디스크 공간**: Ollama 모델과 Vector DB가 수 GB 사용
3. **CPU/메모리**: LLM 실행을 위한 적절한 하드웨어 필요

---

## 문제 해결

### 자주 발생하는 문제

1. **Ollama 연결 실패**
   ```bash
   # 해결: Ollama 서버 시작
   ollama serve
   ```

2. **메모리 저장 실패**
   ```bash
   # 해결: 데이터 디렉토리 권한 확인
   chmod -R 755 data/
   ```

3. **CORS 에러**
   ```python
   # backend/.env
   CORS_ORIGINS=["http://localhost:5173"]
   ```

---

## 참고 자료

- **mem0 공식 문서**: https://github.com/mem0ai/mem0
- **Ollama 공식 사이트**: https://ollama.com
- **FastAPI 문서**: https://fastapi.tiangolo.com
- **Qdrant 문서**: https://qdrant.tech

---

## 라이선스

MIT License

---

## 기여

이슈와 PR을 환영합니다!

---

**마지막 업데이트**: 2025-11-05
