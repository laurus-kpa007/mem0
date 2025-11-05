#!/bin/bash

# Mem0 Test Program - Project Setup Script
# This script creates the complete project structure

set -e

echo "🚀 Setting up Mem0 Test Program..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create main directories
echo -e "${BLUE}📁 Creating directory structure...${NC}"

# Backend structure
mkdir -p backend/app/{api,services,models,core,tests}
mkdir -p backend/data

# Frontend structure
mkdir -p frontend/src/{components/{Chat,Memory,Settings,Common},pages,services,stores,types,utils}
mkdir -p frontend/public

# Data directory
mkdir -p data

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# Create __init__.py files for Python packages
echo -e "${BLUE}📝 Creating Python package files...${NC}"

touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
touch backend/app/models/__init__.py
touch backend/app/core/__init__.py
touch backend/app/tests/__init__.py

echo -e "${GREEN}✓ Python packages initialized${NC}"
echo ""

# Copy environment variables
echo -e "${BLUE}⚙️  Setting up environment variables...${NC}"

if [ -f ".env.example" ]; then
    if [ ! -f "backend/.env" ]; then
        cp .env.example backend/.env
        echo -e "${GREEN}✓ Backend .env created${NC}"
    else
        echo -e "${YELLOW}! Backend .env already exists, skipping${NC}"
    fi

    if [ ! -f "frontend/.env" ]; then
        echo "VITE_API_BASE_URL=http://localhost:8000" > frontend/.env
        echo "VITE_DEFAULT_USER_ID=user123" >> frontend/.env
        echo -e "${GREEN}✓ Frontend .env created${NC}"
    else
        echo -e "${YELLOW}! Frontend .env already exists, skipping${NC}"
    fi
else
    echo -e "${YELLOW}! .env.example not found, skipping environment setup${NC}"
fi

echo ""

# Create docker-compose.yml
echo -e "${BLUE}🐳 Creating Docker Compose configuration...${NC}"

cat > docker-compose.yml << 'EOF'
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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 30s
      timeout: 10s
      retries: 3

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
      ollama:
        condition: service_healthy
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
EOF

echo -e "${GREEN}✓ Docker Compose configuration created${NC}"
echo ""

# Create .gitignore
echo -e "${BLUE}📄 Creating .gitignore...${NC}"

cat > .gitignore << 'EOF'
# Environment variables
.env
*.env
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Data
data/
*.db
*.sqlite
qdrant_data/

# Logs
*.log
logs/

# Docker
docker-compose.override.yml
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"
echo ""

# Create README for backend
echo -e "${BLUE}📚 Creating backend README...${NC}"

cat > backend/README.md << 'EOF'
# Mem0 Test Program - Backend

FastAPI backend for Mem0 test program.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m app.main
```

## API Documentation

http://localhost:8000/docs
EOF

echo -e "${GREEN}✓ Backend README created${NC}"
echo ""

# Create README for frontend
echo -e "${BLUE}📚 Creating frontend README...${NC}"

cat > frontend/README.md << 'EOF'
# Mem0 Test Program - Frontend

React + TypeScript frontend for Mem0 test program.

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Access

http://localhost:5173
EOF

echo -e "${GREEN}✓ Frontend README created${NC}"
echo ""

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Next steps:"
echo ""
echo -e "1. Review the documentation:"
echo -e "   ${BLUE}📖 README.md${NC} - Quick start guide"
echo -e "   ${BLUE}📋 DESIGN.md${NC} - System design"
echo -e "   ${BLUE}🛠️  IMPLEMENTATION_GUIDE.md${NC} - Implementation details"
echo ""
echo -e "2. Configure environment variables:"
echo -e "   ${BLUE}backend/.env${NC}"
echo -e "   ${BLUE}frontend/.env${NC}"
echo ""
echo -e "3. Start development:"
echo -e "   ${YELLOW}Option A - Docker:${NC}"
echo -e "     docker-compose up -d ollama"
echo -e "     docker exec -it mem0-ollama ollama pull llama3.2:latest"
echo -e "     docker exec -it mem0-ollama ollama pull nomic-embed-text:latest"
echo -e "     docker-compose up -d"
echo ""
echo -e "   ${YELLOW}Option B - Local:${NC}"
echo -e "     # Terminal 1: Ollama"
echo -e "     ollama serve"
echo ""
echo -e "     # Terminal 2: Backend"
echo -e "     cd backend"
echo -e "     python -m venv venv && source venv/bin/activate"
echo -e "     pip install -r requirements.txt"
echo -e "     python -m app.main"
echo ""
echo -e "     # Terminal 3: Frontend"
echo -e "     cd frontend"
echo -e "     npm install"
echo -e "     npm run dev"
echo ""
echo -e "4. Access the application:"
echo -e "   ${BLUE}Frontend:${NC} http://localhost:5173"
echo -e "   ${BLUE}Backend API:${NC} http://localhost:8000"
echo -e "   ${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
