# Mem0 with Ollama Configuration Guide

## 현재 설정 (Ollama 사용)

이 프로젝트는 **완전히 Ollama를 사용**하도록 구성되어 있습니다:

### ✅ Ollama가 사용되는 곳

1. **mem0 Fact Extraction** (memory_service.py)
   - Provider: `ollama`
   - 메모리 추가 시 자동으로 사실 추출
   - 모델: `OLLAMA_DEFAULT_MODEL` (기본: llama3.2:latest)

2. **mem0 Embeddings** (memory_service.py)
   - Provider: `ollama`
   - 벡터 임베딩 생성
   - 모델: `OLLAMA_EMBEDDING_MODEL` (기본: nomic-embed-text:latest)

3. **Chat Service** (chat_service.py)
   - Ollama를 통해 대화 생성
   - 관련 메모리를 컨텍스트로 사용

4. **Tag Service** (tag_service.py)
   - Ollama로 태그 자동 생성
   - 모델: `OLLAMA_DEFAULT_MODEL`

### 🚫 OpenAI/Anthropic 불필요

`requirements.txt`에서 `openai`와 `anthropic`은 **선택사항**입니다:
- Ollama를 사용하면 **설치할 필요 없음**
- Cloud LLM을 사용하고 싶을 때만 설치

## 설정 파일

### backend/.env
```bash
# Ollama Configuration - 모든 LLM 기능에 사용됨
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest      # mem0 + 태그 생성에 사용
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest  # 임베딩에 사용

# 이 설정만으로 모든 기능이 Ollama를 사용합니다
```

## 동작 확인

### 1. mem0가 Ollama 사용 중인지 확인

**백엔드 로그 확인**:
```bash
python -m app.main
```

**출력에서 확인**:
```
INFO:     MemoryService initialized successfully
```

**API 테스트**:
```bash
# 메모리 추가 (mem0가 Ollama로 fact extraction)
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "나는 파이썬 개발자입니다",
    "user_id": "test"
  }'
```

### 2. 태그 생성이 Ollama 사용 중인지 확인

```bash
# 태그 제안 (Ollama로 생성)
curl -X POST http://localhost:8000/api/memory/suggest-tags \
  -H "Content-Type: application/json" \
  -d '{
    "content": "오늘 회사에서 프로젝트 회의를 했다",
    "max_tags": 5
  }'
```

**응답**:
```json
{
  "tags": ["회사", "프로젝트", "회의", "업무", "협업"],
  "confidence": 0.85
}
```

### 3. 채팅이 Ollama 사용 중인지 확인

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "내 직업은?",
    "user_id": "test",
    "session_id": "s1",
    "model": "llama3.2:latest"
  }'
```

## 코드 구조

### memory_service.py (mem0 설정)
```python
self.config = MemoryConfig(
    llm=LlmConfig(
        provider="ollama",  # ✅ Ollama 사용
        config={
            "model": ollama_model,  # llama3.2:latest
            "base_url": ollama_base_url,  # http://localhost:11434
            "temperature": 0.1,
            "max_tokens": 2000
        }
    ),
    embedder=EmbedderConfig(
        provider="ollama",  # ✅ Ollama 사용
        config={
            "model": embedding_model,  # nomic-embed-text:latest
            "base_url": ollama_base_url
        }
    ),
    # ... vector store 설정
)
```

### tag_service.py (태그 생성)
```python
# LLM 호출 (설정된 모델 사용)
response = await self.ollama_service.chat(
    model=self.default_model,  # settings.ollama_default_model
    messages=[...]
)
```

## 다른 모델로 변경

### 1. 환경 변수로 변경
```bash
# backend/.env
OLLAMA_DEFAULT_MODEL=gemma2:9b          # LLM 모델 변경
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

### 2. 모델 다운로드
```bash
ollama pull gemma2:9b
```

### 3. 백엔드 재시작
```bash
python -m app.main
```

## Cloud LLM 사용 (선택사항)

만약 Ollama 대신 OpenAI/Anthropic을 사용하고 싶다면:

### 1. 패키지 설치
```bash
pip install openai anthropic
```

### 2. memory_service.py 수정
```python
# OpenAI 사용 예시
llm=LlmConfig(
    provider="openai",
    config={
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "temperature": 0.1
    }
)
```

### 3. 환경 변수 추가
```bash
OPENAI_API_KEY=sk-...
```

## 문제 해결

### Ollama 연결 실패
```bash
# Ollama 상태 확인
curl http://localhost:11434/api/version

# Ollama 재시작
ollama serve
```

### 모델 없음 오류
```bash
# 필수 모델 다운로드
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# 설치된 모델 확인
ollama list
```

### mem0 초기화 실패
```bash
# 로그 확인
python -m app.main

# 데이터 디렉토리 권한 확인
ls -la data/
```

## 요약

✅ **현재 상태**: 모든 LLM 기능이 Ollama 사용
- mem0 fact extraction: Ollama
- 임베딩: Ollama
- 채팅: Ollama
- 태그 생성: Ollama

✅ **필요한 것**: Ollama만 설치하면 됨

❌ **불필요한 것**: OpenAI API 키, Anthropic API 키

🎯 **완전한 로컬 실행**: 인터넷 없이 100% 로컬에서 작동
