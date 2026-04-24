# 2026-04-24 RAG Microservice Design

## Overview
Local-first RAG microservice. Python/FastAPI. 100% On-premise.

## Tech Stack
- **Framework:** FastAPI (Async)
- **Task Queue:** Celery + Redis
- **Vector DB:** Qdrant (Hybrid Search)
- **RAG Framework:** LlamaIndex
- **Inference:** Ollama (LLM)
- **Embeddings:** SentenceTransformers (`BAAI/bge-m3`)
- **Reranker:** CrossEncoder (`BAAI/bge-reranker-v2-m3`)
- **Parsing:** PyMuPDF + Tesseract OCR

## Components

### 1. Ingestion Pipeline
- **Formats:** .txt, .md, .csv, .xlsx, .docx, .pdf, .jpg, .png
- **Process:**
  - File upload -> Temp storage
  - Celery Task:
    - Load file (PyMuPDF for PDF, Unstructured for others)
    - OCR (Tesseract) if scanned image/PDF
    - Metadata extraction (filename, page, etc.)
    - Chunking (Semantic or Fixed-size)
    - Vectorize & Upsert to Qdrant (Dense + Sparse)

### 2. Search & Retrieval
- **Hybrid Search:** Qdrant native Reciprocal Rank Fusion (RRF).
- **Reranking:** Top-k results from hybrid search passed to CrossEncoder for precision.

### 3. Q&A (LLM)
- **Model:** `llama3` or `mistral` via Ollama.
- **Prompt:** Strict system prompt to avoid hallucinations. "Answer ONLY from context. If not found, say 'Information not available'."
- **Response:** JSON with `answer`, `citations` (doc_id, snippet), and `confidence`.

## API Endpoints
- `POST /api/v1/documents/ingest`: Trigger background ingestion.
- `GET /api/v1/documents/status/{task_id}`: Polling for status.
- `POST /api/v1/search`: Raw retrieval for search-only use cases.
- `POST /api/v1/ask`: Full RAG pipeline.
- `DELETE /api/v1/documents/{document_id}`: Cleanup.

## Infrastructure
- **Docker Compose:**
  - `app`: FastAPI
  - `worker`: Celery
  - `redis`: Task broker
  - `qdrant`: Vector DB
  - `ollama`: LLM server (automatic model pull on start)
