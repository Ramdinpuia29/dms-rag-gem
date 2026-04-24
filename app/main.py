from fastapi import FastAPI
from app.api.v1 import documents, search, ask

app = FastAPI(title="RAG Microservice")

app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(ask.router, prefix="/api/v1/ask", tags=["ask"])
