# Local RAG Microservice

A production-ready, **100% local** Retrieval-Augmented Generation (RAG) microservice. This project provides a robust API for ingesting documents, performing hybrid searches, and generating citation-backed answers using local LLMs and embedding models.

## 🚀 Key Features

- **100% Local & Private:** No external AI APIs (OpenAI, Anthropic, etc.). All data stays on your infrastructure.
- **Multilingual Support:** Uses `BAAI/bge-m3` for high-quality embeddings across English, Hindi, Mizo, and more.
- **Vector Search:** Uses PostgreSQL with `pgvector` for efficient document retrieval and storage.
- **Advanced Reranking:** Integrates `BAAI/bge-reranker-v2-m3` for precise cross-encoder reranking of search results.
- **Multi-Format Ingestion:** Supports PDF, Office docs (.docx, .xlsx), images, and plain text (.md, .txt, .csv).
- **OCR Integration:** Built-in Tesseract OCR for processing scanned PDFs and images (via LlamaIndex readers).
- **Async Processing:** Scalable background ingestion using Celery and Redis.
- **Strict RAG Logic:** Engineered prompts ensure the LLM answers ONLY from provided context, preventing hallucinations and providing verifiable citations.

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python API)
- **Vector Database:** [PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector)
- **LLM Inference:** [Ollama](https://ollama.com/) (Local Model Hosting)
- **RAG Orchestration:** [LlamaIndex](https://www.llamaindex.ai/)
- **Task Queue:** [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
- **Embeddings:** `BAAI/bge-m3` (1024-dim)
- **Reranker:** `BAAI/bge-reranker-v2-m3`
- **Parsing & OCR:** PyMuPDF, Unstructured, Tesseract OCR

## 🏗 Architecture

The system consists of five main components:

1.  **FastAPI App:** Serves the RESTful API and manages the RAG pipeline.
2.  **Celery Worker:** Handles heavy ingestion tasks (parsing, OCR, embedding) asynchronously.
3.  **PostgreSQL (pgvector):** Stores document chunks and their vector embeddings.
4.  **Ollama:** Runs the local LLM (Llama 3) for text generation.
5.  **Redis:** Acts as the message broker for Celery tasks.

A shared Docker volume (`uploads_data`) is used to pass uploaded files between the API and the Worker safely. Model weights are cached in a persistent volume to avoid re-downloads.

## 🚦 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- A Hugging Face account and **HF Read Token** (required for `bge-m3` models)
- At least 16GB of RAM recommended for running LLMs and embedding models simultaneously.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/dms-rag-gem.git
    cd dms-rag-gem
    ```

2.  **Configure environment variables:**
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your `HF_TOKEN`.

3.  **Start the services:**
    ```bash
    docker-compose up -d --build
    ```
    *Note: On first start, services will pull models from Ollama and Hugging Face. This may take significant time depending on your connection.*

4.  **Verify the services:**
    - API & Docs: `http://localhost:8000/docs`
    - Health Check: `http://localhost:8000/health`
    - Postgres: `localhost:5432`

### Local Development Setup (Manual)

If you prefer to run the FastAPI application and Celery worker directly on your host:

#### 1. Install System Dependencies
On macOS: `brew install tesseract poppler`
On Ubuntu: `sudo apt-get install -y tesseract-ocr poppler-utils`

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Run Supporting Services
```bash
docker run -d -p 6379:6379 redis:alpine
docker run -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 ankane/pgvector:latest
```

#### 4. Setup Ollama
Install [Ollama](https://ollama.com/) and pull the model:
```bash
ollama serve
ollama pull llama3
```

#### 5. Run Application & Worker
Ensure `.env` has `DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/postgres`.

**FastAPI App:**
```bash
uvicorn app.main:app --reload
```

**Celery Worker:**
```bash
celery -A app.worker.tasks worker --loglevel=info
```

## 📖 API Documentation

### 1. Ingest a Document
Upload a file for background processing.
- **Endpoint:** `POST /api/v1/documents/ingest`
- **Payload:** `multipart/form-data` (file)
- **Returns:** `task_id` and `document_id`.

### 2. Check Ingestion Status
- **Endpoint:** `GET /api/v1/documents/status/{task_id}`
- **Returns:** Processing status and result info.

### 3. Ask a Question (RAG)
Get a citation-backed answer from your documents.
- **Endpoint:** `POST /api/v1/ask/`
- **Payload:** `{"query": "Your question here"}`

### 4. Search
Raw retrieval with reranking.
- **Endpoint:** `POST /api/v1/search/`
- **Payload:** `{"query": "Search keywords", "limit": 10}`

### 5. Health Check
Verify connectivity to Postgres and other services.
- **Endpoint:** `GET /health`

## 📂 Project Structure

```text
.
├── app/
│   ├── api/v1/             # API Route handlers (ask, documents, search, health)
│   ├── core/               # Configuration (Settings, DB init)
│   ├── services/           # Logic (RAG service, Ingestion pipeline)
│   ├── utils/              # Parsers & Helpers
│   ├── worker/             # Celery tasks
│   └── main.py             # FastAPI entry point
├── docs/                   # Design specs & implementation plans
├── tests/                  # Verification & Mock tests
├── docker-compose.yml      # Infrastructure orchestration
├── Dockerfile              # App & Worker image definition
└── requirements.txt        # Python dependencies
```

## 🔒 Security & Performance

- **Data Privacy:** 100% on-premise. No data ever leaves your network.
- **Performance:** Hybrid search and cross-encoder reranking ensure high precision. Ingestion is asynchronous.
- **Persistence:** All data (Postgres, Models, Uploads) is stored in persistent Docker volumes.

## 📄 License

MIT
