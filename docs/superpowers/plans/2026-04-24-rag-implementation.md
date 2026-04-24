# RAG Microservice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. It will decide whether each batch should run in parallel or serial subagent mode and will pass only task-local context to each subagent. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready, 100% local RAG microservice with FastAPI, Qdrant, Celery, and Ollama.

**Architecture:** Distributed microservice using FastAPI for REST, Celery for async ingestion, Qdrant for hybrid search, and Ollama for local LLM inference.

**Tech Stack:** FastAPI, Celery, Redis, Qdrant, LlamaIndex, Ollama, PyMuPDF, Tesseract.

---

### Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `Dockerfile`
- Create: `.env.example`

- [ ] **Step 1: Create requirements.txt**
```text
fastapi
uvicorn
python-multipart
celery
redis
qdrant-client
llama-index
llama-index-vector-stores-qdrant
llama-index-embeddings-huggingface
llama-index-llms-ollama
llama-index-postprocessor-cohere # Using local reranker instead
sentence-transformers
pymupdf
pytesseract
unstructured[all-docs]
python-dotenv
pydantic-settings
```

- [ ] **Step 2: Create Dockerfile**
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
```

- [ ] **Step 3: Create .env.example**
```env
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3
EMBED_MODEL=BAAI/bge-m3
RERANK_MODEL=BAAI/bge-reranker-v2-m3
```

- [ ] **Step 4: Commit**
```bash
git add requirements.txt Dockerfile .env.example
git commit -m "chore: initial project setup"
```

---

### Task 2: Infrastructure Configuration

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: Create docker-compose.yml**
```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
  
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    entrypoint: /bin/sh -c "ollama serve & sleep 10 && ollama run llama3 && wait"

  app:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_URL=http://ollama:11434
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - qdrant
      - ollama

  worker:
    build: .
    command: celery -A app.worker.tasks worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - redis
      - qdrant

volumes:
  qdrant_data:
  ollama_data:
```

- [ ] **Step 2: Commit**
```bash
git add docker-compose.yml
git commit -m "chore: add docker-compose infra"
```

---

### Task 3: Core App & Worker Setup

**Files:**
- Create: `app/main.py`
- Create: `app/worker/tasks.py`
- Create: `app/core/config.py`

- [ ] **Step 1: Create Config**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama3"
    EMBED_MODEL: str = "BAAI/bge-m3"

settings = Settings()
```

- [ ] **Step 2: Create App shell**
```python
from fastapi import FastAPI
from app.api.v1 import documents, search, ask

app = FastAPI(title="RAG Microservice")

app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(ask.router, prefix="/api/v1/ask", tags=["ask"])
```

- [ ] **Step 3: Setup Celery Worker**
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="ingest_document")
def ingest_document_task(file_path: str, metadata: dict):
    # Logic to be implemented in Task 4
    return {"status": "success"}
```

---

### Task 4: Ingestion Pipeline (AC-001, AC-006)

**Files:**
- Create: `app/services/ingestion.py`
- Create: `app/utils/parsers.py`

- [x] **Step 1: Implement Document Parsers**
Use PyMuPDF for PDF, Unstructured for others. Add Tesseract OCR for images.

- [x] **Step 2: Implement Embedding & Vector Store Logic**
Configure `HuggingFaceEmbedding` with `BAAI/bge-m3`. Configure `QdrantVectorStore`.

- [x] **Step 3: Update Worker Task**
Call ingestion service to process and store document.

---

### Task 5: Search & RAG Pipelines (AC-003, AC-004, AC-005)

**Files:**
- Create: `app/services/rag.py`

- [ ] **Step 1: Implement Hybrid Search**
Use LlamaIndex `VectorIndexRetriever` with Qdrant Hybrid search enabled.

- [ ] **Step 2: Implement Reranking**
Use `SentenceTransformerRerank` with `BAAI/bge-reranker-v2-m3`.

- [ ] **Step 3: Implement Q&A with Ollama**
Configure `Ollama` LLM. Write the strict system prompt.

---

### Task 6: API Endpoints Implementation (AC-002, AC-007)

**Files:**
- Create: `app/api/v1/documents.py`
- Create: `app/api/v1/search.py`
- Create: `app/api/v1/ask.py`

- [ ] **Step 1: Implement Ingest Endpoint**
Accept file, save temp, trigger celery.

- [ ] **Step 2: Implement Search & Ask Endpoints**
Call RAG service.

- [ ] **Step 3: Implement Status & Delete Endpoints**
Check celery result and remove from Qdrant.
