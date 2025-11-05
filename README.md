# Mem0 Test Program

Mem0와 Ollama를 활용한 메모리 기반 대화 시스템

## 📋 개요

이 프로젝트는 mem0 메모리 솔루션과 Ollama LLM을 통합하여 컨텍스트를 기억하고 활용하는 지능형 대화 시스템입니다.

### 주요 기능

- 📝 **메모리 저장**: 텍스트를 mem0에 저장하고 자동으로 임베딩 생성
- 🏷️ **AI 태그 제안**: LLM을 활용한 자동 태그 생성 및 관리
- 🤖 **Ollama 통합**: 로컬 LLM 모델을 선택하여 사용
- 💬 **컨텍스트 대화**: 저장된 메모리를 기반으로 답변 생성
- 🌐 **WebUI**: React + TypeScript 기반의 직관적인 사용자 인터페이스
- ⚡ **FastAPI**: 고성능 REST API 백엔드

## 🏗️ 시스템 아키텍처

```
Frontend (React) ←→ Backend (FastAPI) ←→ Mem0 Library ←→ Qdrant (Vector DB)
                                      ↓
                                  Ollama (LLM)
```

## 📁 프로젝트 구조

```
mem0-test-program/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── services/       # 비즈니스 로직
│   │   ├── models/         # Pydantic 모델
│   │   └── main.py         # 진입점
│   └── requirements.txt
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/    # UI 컴포넌트
│   │   ├── services/      # API 클라이언트
│   │   └── stores/        # 상태 관리
│   └── package.json
├── data/                   # 데이터 저장소
│   ├── qdrant/            # Vector DB
│   └── memory_history.db  # SQLite 히스토리
├── docker-compose.yml
├── DESIGN.md              # 상세 설계 문서
└── IMPLEMENTATION_GUIDE.md # 구현 가이드
```

## 🚀 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- Python 3.10+ (로컬 개발 시)
- Node.js 18+ (로컬 개발 시)

### Docker로 시작하기 (권장)

```bash
# 1. Ollama 시작 및 모델 다운로드
docker-compose up -d ollama
docker exec -it mem0-ollama ollama pull llama3.2:latest
docker exec -it mem0-ollama ollama pull nomic-embed-text:latest

# 2. 전체 서비스 시작
docker-compose up -d

# 3. 접속
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 로컬 개발 환경

#### 1. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치
curl -fsSL https://ollama.com/install.sh | sh

# 모델 다운로드
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# Ollama 서버 시작
ollama serve
```

#### 2. 백엔드 실행

```bash
cd backend

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 서버 실행
python -m app.main
```

#### 3. 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# 개발 서버 실행
npm run dev
```

## 📖 사용 방법

### 1. 메모리 추가

```bash
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "나는 파이썬 개발자이고, FastAPI를 좋아합니다.",
    "user_id": "user123"
  }'
```

### 2. 메모리 기반 대화

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내가 좋아하는 프레임워크는?",
    "user_id": "user123",
    "session_id": "session1",
    "model": "llama3.2:latest",
    "use_memory": true,
    "memory_limit": 5
  }'
```

응답:
```json
{
  "response": "당신은 FastAPI를 좋아한다고 했습니다.",
  "related_memories": [
    {
      "content": "나는 파이썬 개발자이고, FastAPI를 좋아합니다.",
      "score": 0.89
    }
  ],
  "model_used": "llama3.2:latest"
}
```

### 3. WebUI 사용

1. **http://localhost:5173** 접속
2. **Chat 탭**: AI와 실시간 대화, 관련 메모리 표시
3. **Memory 탭**:
   - 텍스트 입력 및 메모리 추가
   - "Suggest Tags" 버튼으로 AI 태그 제안 받기
   - 제안된 태그를 클릭해서 추가하거나 수동 입력
   - 저장된 메모리 목록 조회 및 삭제
4. **Settings 탭**:
   - Ollama 모델 선택 및 새로고침
   - 사용자 ID 설정
   - 메모리 사용 On/Off
   - 메모리 검색 결과 수 조절

## 🔧 API 엔드포인트

### Memory APIs

- `POST /api/memory/add` - 메모리 추가 (태그 메타데이터 포함)
- `GET /api/memory/search` - 메모리 검색
- `GET /api/memory/list` - 전체 메모리 조회
- `DELETE /api/memory/{id}` - 메모리 삭제

### Tag APIs 🏷️

- `POST /api/memory/suggest-tags` - AI 태그 제안
- `GET /api/memory/tags/autocomplete` - 태그 자동완성
- `GET /api/memory/tags/popular` - 인기 태그 조회

### Chat APIs

- `POST /api/chat` - 메모리 기반 대화 생성

### Ollama APIs

- `GET /api/ollama/models` - 모델 목록
- `GET /api/ollama/status` - 서버 상태

### Utility APIs

- `GET /api/health` - 헬스체크

자세한 API 문서: http://localhost:8000/docs

## 🎯 주요 기술

### Backend
- **FastAPI**: 고성능 웹 프레임워크
- **mem0**: 메모리 관리 라이브러리
- **Qdrant**: 벡터 데이터베이스
- **Ollama**: 로컬 LLM 서버

### Frontend
- **React 18**: UI 라이브러리
- **TypeScript**: 타입 안정성
- **Vite**: 빠른 빌드 도구
- **Zustand**: 경량 상태 관리
- **Tailwind CSS**: 유틸리티 기반 스타일링
- **React Router**: SPA 라우팅
- **Axios**: HTTP 클라이언트
- **Lucide React**: 아이콘 라이브러리

## 📚 문서

- [DESIGN.md](./DESIGN.md) - 상세 시스템 설계 문서 (Mermaid 다이어그램 포함)
- [DESIGN_DIAGRAMS.md](./DESIGN_DIAGRAMS.md) - 추가 Mermaid 다이어그램 및 시각화 (30+ 다이어그램)
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) - 구현 가이드 (백엔드/프론트엔드)
- [TAG_FEATURE.md](./TAG_FEATURE.md) - AI 태그 기능 상세 문서
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - 프로젝트 전체 요약
- [HOW_MEM0_WORKS.md](./HOW_MEM0_WORKS.md) - mem0 동작 원리 상세 설명
- [backend/README.md](./backend/README.md) - 백엔드 문서
- [frontend/README.md](./frontend/README.md) - 프론트엔드 문서

## 🔍 핵심 개념

### Mem0란?

Mem0는 AI 애플리케이션을 위한 메모리 레이어입니다:
- **자동 Fact Extraction**: LLM을 사용하여 대화에서 중요한 정보 추출
- **Vector Search**: 임베딩 기반 의미론적 검색
- **History Tracking**: SQLite로 변경 이력 관리
- **Multi-provider**: 다양한 LLM 및 벡터 DB 지원

### 메모리 저장 플로우

```
사용자 입력
  ↓
mem0 Fact Extraction (LLM)
  ↓
임베딩 생성
  ↓
Vector DB 저장 (Qdrant)
  ↓
History 기록 (SQLite)
```

### 대화 생성 플로우

```
사용자 질문
  ↓
Vector Search (관련 메모리 검색)
  ↓
컨텍스트 구성 (메모리 + 질문)
  ↓
Ollama LLM 호출
  ↓
응답 생성
```

## ⚙️ 환경 변수

### Backend (.env)

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# Mem0
VECTOR_STORE_PATH=../data/qdrant
HISTORY_DB_PATH=../data/memory_history.db

# Server
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
LOG_LEVEL=INFO
```

### Frontend (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🐛 트러블슈팅

### Ollama 연결 실패

```bash
# 상태 확인
curl http://localhost:11434/api/version

# 재시작
ollama serve
```

### Vector DB 오류

```bash
# 데이터 디렉토리 권한 확인
chmod -R 755 data/

# 디렉토리 재생성
rm -rf data/qdrant
mkdir -p data/qdrant
```

### CORS 에러

`backend/.env`에서 CORS 설정 확인:
```bash
CORS_ORIGINS=["http://localhost:5173"]
```

## 📈 성능 최적화

1. **벡터 검색 최적화**
   - Qdrant 인덱스 파라미터 튜닝
   - 적절한 similarity threshold 설정

2. **응답 시간 개선**
   - 메모리 검색 캐싱
   - 병렬 처리

3. **리소스 관리**
   - 불필요한 Ollama 모델 언로드
   - 메모리 제한 설정

## 🛣️ 로드맵

### Phase 1 ✅ (완료)
- [x] 기본 아키텍처 설계
- [x] mem0 통합
- [x] Ollama 통합
- [x] 기본 API 구현
- [x] 상세 설계 문서 작성

### Phase 2 ✅ (완료)
- [x] React + TypeScript WebUI 구현
- [x] 메모리 관리 UI (추가/조회/삭제)
- [x] 채팅 인터페이스 (실시간 대화, 관련 메모리 표시)
- [x] 설정 페이지 (모델 선택, 사용자 설정)
- [x] Tailwind CSS 스타일링

### Phase 3 ✅ (완료)
- [x] AI 태그 시스템 (LLM 기반 자동 제안)
- [x] 태그 자동완성 및 인기 태그
- [x] 하이브리드 태그 입력 (AI + 수동)
- [x] 태그 메타데이터 저장

### Phase 4 (계획)
- [ ] 스트리밍 응답 지원
- [ ] 고급 세션 관리
- [ ] Export/Import 기능
- [ ] 통계 대시보드
- [ ] 사용자 인증
- [ ] 멀티 유저 지원

## 🤝 기여

이슈와 풀 리퀘스트를 환영합니다!

## 📝 라이선스

MIT License

## 🙏 감사

- [mem0](https://github.com/mem0ai/mem0) - 메모리 솔루션
- [Ollama](https://ollama.com/) - 로컬 LLM 서버
- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크
- [React](https://react.dev/) - UI 라이브러리

---

## 📞 문의

질문이나 제안사항이 있으시면 이슈를 생성해주세요.

**Happy Coding! 🚀**
