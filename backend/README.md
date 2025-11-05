# Mem0 Test Program - Backend

FastAPI backend for the Mem0 test program with Ollama integration.

## Features

- 📝 **Memory Management**: Add, search, list, and delete memories
- 🏷️ **AI Tag Suggestions**: Automatic tag generation using LLM
- 💬 **Chat with Memory**: Context-aware responses using stored memories
- 🤖 **Ollama Integration**: Support for multiple LLM models
- 🔍 **Semantic Search**: Vector-based memory search with Qdrant
- 📊 **Automatic Fact Extraction**: mem0 extracts discrete facts from text

## Technology Stack

- **FastAPI** - Modern Python web framework
- **mem0ai** - Memory layer for AI applications
- **Ollama** - Local LLM server
- **Qdrant** - Vector database (embedded mode)
- **SQLite** - History tracking
- **httpx** - Async HTTP client
- **Pydantic** - Data validation

## Getting Started

### Prerequisites

- Python 3.11+
- Ollama installed and running (http://localhost:11434)
- Required Ollama models pulled:
  ```bash
  ollama pull llama3.2:latest
  ollama pull nomic-embed-text:latest
  ```

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env if needed
nano .env
```

### Running the Server

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Memory Management

- `POST /api/memory/add` - Add new memory
- `GET /api/memory/list` - List all memories
- `GET /api/memory/search` - Search memories
- `DELETE /api/memory/{memory_id}` - Delete memory

### Tag Features

- `POST /api/memory/suggest-tags` - AI-powered tag suggestions
- `GET /api/memory/tags/autocomplete` - Autocomplete tags
- `GET /api/memory/tags/popular` - Get popular tags

### Chat

- `POST /api/chat` - Send chat message with memory context

### Ollama

- `GET /api/ollama/models` - List available models
- `GET /api/ollama/status` - Check Ollama server status

### Health

- `GET /` - Root endpoint
- `GET /api/health` - Health check

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── dependencies.py      # Dependency injection
│   ├── api/                 # API endpoints
│   │   ├── memory.py
│   │   ├── chat.py
│   │   └── ollama.py
│   ├── models/              # Pydantic models
│   │   └── memory.py
│   ├── services/            # Business logic
│   │   ├── memory_service.py
│   │   ├── chat_service.py
│   │   ├── ollama_service.py
│   │   └── tag_service.py
│   └── core/                # Core utilities
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── Dockerfile              # Docker configuration
└── README.md
```

## Configuration

Environment variables in `.env`:

```env
# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest

# Data Storage
VECTOR_STORE_PATH=../data/qdrant
HISTORY_DB_PATH=../data/memory_history.db
```

## Docker

```bash
# Build and run with docker-compose (from project root)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Testing

```bash
# Health check
curl http://localhost:8000/api/health

# List models
curl http://localhost:8000/api/ollama/models

# Add memory
curl -X POST http://localhost:8000/api/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I love programming in Python",
    "user_id": "user123"
  }'

# Suggest tags
curl -X POST http://localhost:8000/api/memory/suggest-tags \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I love programming in Python",
    "max_tags": 5
  }'

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do I like?",
    "user_id": "user123",
    "session_id": "session1",
    "model": "llama3.2:latest",
    "use_memory": true,
    "memory_limit": 5
  }'
```

## Development

```bash
# Install dev dependencies
pip install pytest pytest-asyncio black flake8

# Format code
black app/

# Lint
flake8 app/

# Run tests (if available)
pytest
```

## How It Works

1. **Memory Storage**: When you add content, mem0 automatically:
   - Extracts discrete facts from the text
   - Generates embeddings using Ollama
   - Stores vectors in Qdrant
   - Tracks history in SQLite

2. **Tag Generation**: The tag service:
   - Sends content to LLM with specific prompt
   - Parses and cleans suggested tags
   - Falls back to keyword extraction if LLM fails
   - Provides confidence scores

3. **Chat**: When you send a message:
   - Searches relevant memories using semantic search
   - Builds context from related memories
   - Calls Ollama with augmented prompt
   - Returns response with memory sources

## Troubleshooting

### Ollama not connecting
- Ensure Ollama is running: `ollama serve`
- Check Ollama status: `curl http://localhost:11434/api/version`
- Verify models are pulled: `ollama list`

### Memory not persisting
- Check DATA_DIR in .env
- Ensure directory is writable
- Check logs for Qdrant/SQLite errors

### Slow responses
- Use smaller models (e.g., llama3.2:1b)
- Reduce memory_limit in chat requests
- Enable GPU acceleration in Ollama

## Documentation

- [Design Document](../DESIGN.md)
- [Implementation Guide](../IMPLEMENTATION_GUIDE.md)
- [Tag Feature Documentation](../TAG_FEATURE.md)
- [mem0 Documentation](https://docs.mem0.ai)
- [Ollama Documentation](https://ollama.ai/docs)

## License

This is a test program for demonstration purposes.
