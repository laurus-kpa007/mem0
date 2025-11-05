"""
Mem0 Test Program - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.api import memory
from app.api import chat as chat_router
from app.api import ollama as ollama_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mem0 Test Program API",
    description="Backend API for Mem0 memory system with Ollama integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(memory.router, tags=["memory"])
app.include_router(chat_router.router, tags=["chat"])
app.include_router(ollama_router.router, tags=["ollama"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mem0 Test Program API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "mem0-backend",
        "version": "1.0.0",
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Starting Mem0 Test Program Backend...")
    logger.info(f"Data directory: {settings.DATA_DIR}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    logger.info("Backend started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down Mem0 Test Program Backend...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
