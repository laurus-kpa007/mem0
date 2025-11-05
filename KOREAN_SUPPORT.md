# 한글 지원 가이드

## 현재 상황

기본 설정으로는 한글이 부분적으로 지원됩니다:

### ✅ 잘 작동하는 부분
- **임베딩 (nomic-embed-text)**: 한글 벡터 검색 우수
- **메모리 저장**: 한글 텍스트 저장 및 검색 가능
- **UI**: 완전한 한글 지원

### ⚠️ 제한적인 부분
- **LLM (llama3.2)**: 영어 중심 모델로 한글 생성 품질 제한적

---

## 한글 최적화 방법

### 1. 한글 지원이 우수한 LLM 모델 사용

#### Option A: Gemma2 (Google - 추천) ⭐

```bash
# Gemma2 모델 다운로드
ollama pull gemma2:9b      # 9B 파라미터 (권장)
ollama pull gemma2:27b     # 27B 파라미터 (더 높은 품질)

# 또는 작은 모델
ollama pull gemma2:2b      # 2B 파라미터 (빠른 응답)
```

**장점:**
- 한글/영어 모두 우수한 성능
- Google의 다국어 최적화
- 안정적인 한글 생성

#### Option B: Qwen2.5 (Alibaba)

```bash
# Qwen2.5 모델 다운로드
ollama pull qwen2.5:7b
ollama pull qwen2.5:14b
```

**장점:**
- 아시아 언어에 특화
- 한국어, 중국어, 일본어 우수
- 코드 생성도 뛰어남

#### Option C: Llama3.1 (Meta - 대용량)

```bash
# Llama3.1 모델 다운로드
ollama pull llama3.1:8b
ollama pull llama3.1:70b   # 고성능 서버 필요
```

**장점:**
- llama3.2보다 다국어 성능 개선
- 대용량 모델은 한글 품질 향상

### 2. 한글 임베딩 모델 (선택사항)

기본 `nomic-embed-text`도 한글 지원이 우수하지만, 더 나은 옵션:

```bash
# 다국어 임베딩 모델
ollama pull nomic-embed-text:latest   # 현재 사용 중 (권장)
# 또는
ollama pull mxbai-embed-large:latest  # 대안
```

---

## 설정 변경 방법

### 방법 1: 환경 변수로 변경

**backend/.env 파일 수정:**

```bash
# 한글 최적화 설정 (Gemma2 사용)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=gemma2:9b                    # 변경
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest    # 유지
VECTOR_STORE_PATH=../data/qdrant
HISTORY_DB_PATH=../data/memory_history.db
```

### 방법 2: WebUI에서 변경

1. http://localhost:5173 접속
2. **Settings** 탭으로 이동
3. **LLM Model** 섹션에서 `gemma2:9b` 선택
4. 자동 저장됨

### 방법 3: API로 직접 지정

```bash
# 채팅 시 모델 지정
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요, 제 이름은 홍길동입니다.",
    "user_id": "user123",
    "session_id": "session1",
    "model": "gemma2:9b",          # 여기서 변경
    "use_memory": true,
    "memory_limit": 5
  }'
```

---

## 모델 비교

| 모델 | 크기 | 한글 품질 | 속도 | 메모리 | 추천도 |
|------|------|-----------|------|--------|--------|
| llama3.2:latest | 3B | ⭐⭐ | 빠름 | 4GB | - |
| llama3.2:1b | 1B | ⭐ | 매우 빠름 | 2GB | - |
| **gemma2:2b** | 2B | ⭐⭐⭐ | 빠름 | 4GB | ⭐⭐⭐ |
| **gemma2:9b** | 9B | ⭐⭐⭐⭐⭐ | 보통 | 12GB | ⭐⭐⭐⭐⭐ |
| gemma2:27b | 27B | ⭐⭐⭐⭐⭐ | 느림 | 32GB | ⭐⭐⭐⭐ |
| qwen2.5:7b | 7B | ⭐⭐⭐⭐ | 보통 | 10GB | ⭐⭐⭐⭐ |
| llama3.1:8b | 8B | ⭐⭐⭐ | 보통 | 10GB | ⭐⭐⭐ |

**권장 조합:**
- **일반 사용**: `gemma2:2b` (빠른 응답, 적절한 한글 품질)
- **고품질**: `gemma2:9b` (최고의 한글 품질)
- **저사양**: `llama3.2:1b` (한글 제한적이지만 가볍고 빠름)

---

## 테스트 방법

### 1. 모델 다운로드 및 변경

```bash
# Gemma2 다운로드
ollama pull gemma2:9b

# 백엔드 환경변수 변경
cd backend
echo "OLLAMA_DEFAULT_MODEL=gemma2:9b" >> .env

# 백엔드 재시작
python -m app.main
```

### 2. 한글 테스트

```bash
# 한글 메모리 추가
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "나는 서울에 살고 있고, 파이썬 개발자입니다. 주로 FastAPI와 React를 사용합니다.",
    "user_id": "user123"
  }'

# 한글로 질문
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내가 사는 곳은 어디야?",
    "user_id": "user123",
    "session_id": "session1",
    "model": "gemma2:9b",
    "use_memory": true,
    "memory_limit": 5
  }'
```

### 3. 태그 제안 테스트

```bash
# 한글 태그 제안
curl -X POST http://localhost:8000/api/memory/suggest-tags \
  -H "Content-Type: application/json" \
  -d '{
    "content": "오늘 회사에서 중요한 프로젝트 발표가 있었다. 새로운 AI 기능을 추가하는 작업이었는데 팀원들의 반응이 좋았다.",
    "max_tags": 5,
    "language": "ko"
  }'
```

**예상 결과 (gemma2 사용 시):**
```json
{
  "tags": ["회사", "프로젝트", "발표", "AI", "팀워크"],
  "confidence": 0.85
}
```

---

## Docker 환경에서 변경

**docker-compose.yml 환경변수 수정:**

```yaml
services:
  backend:
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OLLAMA_DEFAULT_MODEL=gemma2:9b          # 변경
      - OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

**Docker에서 모델 다운로드:**

```bash
# Ollama 컨테이너에서 모델 다운로드
docker exec -it mem0-ollama ollama pull gemma2:9b

# 서비스 재시작
docker-compose restart backend
```

---

## 성능 고려사항

### 메모리 요구사항

| 모델 | 최소 RAM | 권장 RAM | GPU |
|------|----------|----------|-----|
| gemma2:2b | 4GB | 8GB | 선택 |
| gemma2:9b | 12GB | 16GB | 권장 |
| qwen2.5:7b | 10GB | 16GB | 권장 |

### 속도 최적화

1. **GPU 가속** (NVIDIA GPU 있는 경우):
```bash
# Ollama가 자동으로 GPU 감지 및 사용
# CUDA 드라이버만 설치되어 있으면 됨
```

2. **양자화 모델** (더 빠른 응답):
```bash
# 4-bit 양자화 모델
ollama pull gemma2:9b-q4_0  # 더 작은 메모리, 약간 낮은 품질
```

---

## 문제 해결

### 한글이 깨지는 경우

**UTF-8 인코딩 확인:**
```bash
# 환경 변수 설정
export LANG=ko_KR.UTF-8
export LC_ALL=ko_KR.UTF-8
```

### 모델이 한글을 잘 이해하지 못하는 경우

1. 더 큰 모델 사용 (gemma2:9b → gemma2:27b)
2. 프롬프트에 명시적으로 한글 사용 지시
3. 예시를 포함한 few-shot prompting

### 느린 응답 속도

1. 더 작은 모델 사용 (gemma2:2b)
2. GPU 가속 활성화
3. 양자화 모델 사용

---

## 결론

**최적의 한글 지원을 위한 권장 설정:**

```bash
# 1. 모델 다운로드
ollama pull gemma2:9b
ollama pull nomic-embed-text:latest

# 2. 환경 변수 설정
OLLAMA_DEFAULT_MODEL=gemma2:9b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# 3. 서버 재시작 및 테스트
```

이 설정으로 **한글 메모리 저장, 검색, 대화, 태그 생성** 모두 고품질로 작동합니다! 🇰🇷
