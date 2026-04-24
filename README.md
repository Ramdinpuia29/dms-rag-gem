# Local RAG Microservice

A production-ready, **100% local** Retrieval-Augmented Generation (RAG) microservice. Provides a robust API for ingesting documents, performing hybrid searches, and generating citation-backed answers using local LLMs and embedding models.

## Key Features

- **100% Local & Private:** No external AI APIs. All data stays on your infrastructure.
- **Multilingual Support:** `BAAI/bge-m3` embeddings across English, Hindi, Mizo, and more.
- **Hybrid Vector Search:** PostgreSQL + `pgvector` with dense + sparse retrieval.
- **Cross-Encoder Reranking:** `BAAI/bge-reranker-v2-m3` for high-precision result ordering.
- **Query Result Caching:** Redis cache on `ask` responses — repeated queries skip retrieval + LLM entirely.
- **Multi-Format Ingestion:** PDF, DOCX, XLSX, CSV, TXT, MD, PNG, JPG (max 50 MB).
- **OCR Integration:** Tesseract OCR for scanned PDFs and images.
- **Async Processing:** Celery + Redis with exponential-backoff retries.
- **Non-blocking Streaming:** SSE token streaming via `asyncio.Queue` — does not block the event loop.
- **Strict RAG Logic:** Prompts constrain the LLM to context only, with verifiable citations.

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Vector DB | PostgreSQL + pgvector |
| LLM | Ollama (local) |
| RAG Orchestration | LlamaIndex |
| Task Queue | Celery + Redis |
| Embeddings | `BAAI/bge-m3` (1024-dim) |
| Reranker | `BAAI/bge-reranker-v2-m3` |
| Parsing / OCR | PyMuPDF, Unstructured, Tesseract |

## Architecture

```
Client
  │
  ▼
FastAPI App ──── Redis (Celery broker + query cache)
  │                │
  │            Celery Worker
  │                │
  └──────► PostgreSQL / pgvector
                   ▲
               Ollama (LLM)
```

Five components:

1. **FastAPI App** — REST API, RAG pipeline, cached retriever/query engines
2. **Celery Worker** — async ingestion (parse → chunk → embed → store), retries on failure
3. **PostgreSQL (pgvector)** — stores document chunks + vector embeddings
4. **Ollama** — local LLM inference (Llama 3)
5. **Redis** — Celery broker + query result cache (TTL configurable)

Shared Docker volume (`uploads_data`) passes uploaded files between API and Worker. Model weights cached in persistent volume to avoid re-downloads.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- Hugging Face account with **HF Read Token** (required for `bge-m3` models)
- 16 GB RAM minimum recommended

### Installation

1. **Clone:**
    ```bash
    git clone https://github.com/your-repo/dms-rag-gem.git
    cd dms-rag-gem
    ```

2. **Configure environment:**
    ```bash
    cp .env.example .env
    ```
    Edit `.env` — set at minimum `HF_TOKEN`. See [Environment Variables](#environment-variables) for all options.

3. **Start services:**
    ```bash
    docker-compose up -d --build
    ```
    First start pulls Ollama and Hugging Face models — allow extra time.

4. **Verify:**
    - Swagger UI: `http://localhost:8000/docs`
    - Health check: `http://localhost:8000/health`

### Docker Workflow (Day-to-Day)

Avoid `docker-compose down && up` — it tears down Redis, Postgres, and Ollama needlessly, forcing full re-init including Ollama's healthcheck chain (~50s penalty).

| Scenario | Command |
|---|---|
| Code change (most common) | `docker-compose restart app worker` |
| New Python dependency added | `docker-compose up -d --build --no-deps app worker` |
| Full reset (volume wipe, schema change) | `docker-compose down && docker-compose up -d` |

Code changes are reflected immediately on restart because `.:/app` is a live volume mount — no rebuild needed.

### Local Development (without Docker)

#### 1. System dependencies
```bash
# macOS
brew install tesseract poppler

# Ubuntu
sudo apt-get install -y tesseract-ocr poppler-utils
```

#### 2. Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Supporting services
```bash
docker run -d -p 6379:6379 redis:alpine
docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 ankane/pgvector:latest
```

#### 4. Ollama
```bash
ollama serve
ollama pull llama3
```

#### 5. Run
```bash
# API
uvicorn app.main:app --reload

# Worker (separate terminal)
celery -A app.worker.tasks worker --loglevel=info
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/dms_rag` | PostgreSQL connection |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama base URL |
| `MODEL_NAME` | `llama3` | Ollama model to use |
| `EMBED_MODEL` | `BAAI/bge-m3` | HuggingFace embedding model |
| `RERANK_MODEL` | `BAAI/bge-reranker-v2-m3` | Cross-encoder reranker model |
| `UPLOAD_DIR` | `/app/uploads` | Temporary upload directory |
| `QUERY_CACHE_TTL` | `3600` | Query result cache TTL in seconds |
| `HF_TOKEN` | — | Hugging Face read token |

## API Reference

### Ingest a Document
```
POST /api/v1/documents/ingest
Content-Type: multipart/form-data

file: <binary>
```
Returns `task_id` and `document_id`. Allowed types: `.pdf .docx .xlsx .csv .txt .md .png .jpg .jpeg`. Max 50 MB.

### Check Ingestion Status
```
GET /api/v1/documents/status/{task_id}
```

### Delete a Document
```
DELETE /api/v1/documents/{document_id}
```

### Ask (RAG)
```
POST /api/v1/ask/
{"query": "Your question here"}
```
Returns answer with source citations. Results cached in Redis by query hash.

### Ask with Streaming (SSE)
```
POST /api/v1/ask/stream
{"query": "Your question here"}
```
Server-Sent Events. Event types: `sources`, `token`, `done`, `error`.

### Hybrid Search
```
POST /api/v1/search/
{"query": "keywords", "limit": 10}
```
Returns retrieved + reranked chunks.

### Health Check
```
GET /health
```
Reports status of Redis, PostgreSQL, and Ollama.

## Project Structure

```
.
├── app/
│   ├── api/v1/         # Route handlers (ask, documents, search, health)
│   ├── core/           # Settings (config.py)
│   ├── services/       # RAG pipeline (rag.py), ingestion (ingestion.py)
│   ├── utils/          # File parsers (parsers.py)
│   ├── worker/         # Celery tasks (tasks.py)
│   └── main.py         # FastAPI entry point + lifespan
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Performance Notes

- **Retriever + query engines** built once at startup and reused across all requests (no per-request reconstruction).
- **Query cache** — `ask` responses stored in Redis keyed by MD5 hash of the query. Cache miss triggers full retrieval + rerank + LLM; hit returns instantly.
- **Streaming** uses `asyncio.Queue` + `run_in_executor` so sync generator (retrieval, LLM tokens) runs in a thread pool without blocking the event loop.
- **Vector store** singleton — single `PGVectorStore` connection shared across ingestion and delete operations.
- **Celery tasks** retry up to 3 times with exponential backoff (max 60s) on failure.

## License

MIT
