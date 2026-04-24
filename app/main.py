from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1 import documents, search, ask, health
from app.services.rag import rag_service
from app.services.ingestion import init_ingestion_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services
    init_ingestion_settings()
    rag_service.initialize()
    yield

app = FastAPI(title="RAG Microservice", lifespan=lifespan)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(ask.router, prefix="/api/v1/ask", tags=["ask"])
