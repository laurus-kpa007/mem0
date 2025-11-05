#!/bin/bash

# Ollama Setup Script for Mem0 Test Program
# Downloads required models for the application

set -e

echo "🤖 Ollama Model Setup for Mem0 Test Program"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama is not installed${NC}"
    echo ""
    echo "Please install Ollama first:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    echo "Or visit: https://ollama.com"
    exit 1
fi

echo -e "${GREEN}✓ Ollama is installed${NC}"
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama server is not running${NC}"
    echo ""
    echo "Starting Ollama server..."
    echo "Please run in another terminal: ollama serve"
    echo ""
    read -p "Press Enter when Ollama is running..."
fi

echo -e "${GREEN}✓ Ollama server is running${NC}"
echo ""

# Required models
LLM_MODEL="llama3.2:latest"
EMBED_MODEL="nomic-embed-text:latest"

# Optional models
OPTIONAL_MODELS=("mistral:latest" "gemma2:latest")

# Download LLM model
echo -e "${BLUE}📥 Downloading LLM model: ${LLM_MODEL}${NC}"
ollama pull ${LLM_MODEL}
echo -e "${GREEN}✓ ${LLM_MODEL} downloaded${NC}"
echo ""

# Download embedding model
echo -e "${BLUE}📥 Downloading embedding model: ${EMBED_MODEL}${NC}"
ollama pull ${EMBED_MODEL}
echo -e "${GREEN}✓ ${EMBED_MODEL} downloaded${NC}"
echo ""

# Ask about optional models
echo -e "${YELLOW}Optional models:${NC}"
echo "  - mistral:latest (7B parameters, good general performance)"
echo "  - gemma2:latest (Google's model, efficient)"
echo ""
read -p "Do you want to download optional models? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for model in "${OPTIONAL_MODELS[@]}"; do
        echo -e "${BLUE}📥 Downloading: ${model}${NC}"
        ollama pull ${model}
        echo -e "${GREEN}✓ ${model} downloaded${NC}"
        echo ""
    done
fi

# List installed models
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Installed models:"
echo ""
ollama list
echo ""
echo -e "You can now start the Mem0 Test Program:"
echo -e "  ${BLUE}docker-compose up -d${NC}"
echo -e "  or"
echo -e "  ${BLUE}cd backend && python -m app.main${NC}"
echo ""
