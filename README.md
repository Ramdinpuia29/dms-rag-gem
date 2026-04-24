# Local RAG Microservice

A production-ready, **100% local** Retrieval-Augmented Generation (RAG) microservice. This project provides a robust API for ingesting documents, performing hybrid searches, and generating citation-backed answers using local LLMs and embedding models.

## 🚀 Key Features

- **100% Local & Private:** No external AI APIs (OpenAI, Anthropic, etc.). All data stays on your infrastructure.
- **Multilingual Support:** Uses `BAAI/bge-m3` for high-quality embeddings across English, Hindi, Mizo, and more.
- **Hybrid Search:** Combines dense vector search and sparse keyword search via Qdrant for superior retrieval accuracy.
- **Advanced Reranking:** Integrates `BAAI/bge-reranker-v2-m3` for precise cross-encoder reranking of search results.
- **Multi-Format Ingestion:** Supports PDF, Office docs (.docx, .xlsx), images, and plain text (.md, .txt, .csv).
- **OCR Integration:** Built-in Tesseract OCR for processing scanned PDFs and images.
- **Async Processing:** Scalable background ingestion using Celery and Redis.
- **Strict RAG Logic:** Engineered prompts ensure the LLM answers ONLY from provided context, preventing hallucinations and providing verifiable citations.

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python API)
- **Vector Database:** [Qdrant](https://qdrant.tech/) (Hybrid Search + RRF)
- **LLM Inference:** [Ollama](https://ollama.com/) (Local Model Hosting)
- **RAG Orchestration:** [LlamaIndex](https://www.llamaindex.ai/)
- **Task Queue:** [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
- **Embeddings:** `BAAI/bge-m3`
- **Reranker:** `BAAI/bge-reranker-v2-m3`
- **Parsing & OCR:** PyMuPDF, Unstructured, Tesseract OCR

## 🏗 Architecture

The system consists of five main components:

1.  **FastAPI App:** Serves the RESTful API and manages the RAG pipeline.
2.  **Celery Worker:** Handles heavy ingestion tasks (parsing, OCR, embedding) asynchronously.
3.  **Qdrant:** Stores document embeddings and performs hybrid searches.
4.  **Ollama:** Runs the local LLM (e.g., Llama 3) for text generation.
5.  **Redis:** Acts as the message broker for Celery tasks.

A shared Docker volume (`uploads_data`) is used to pass uploaded files between the API and the Worker safely.

## 🚦 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- At least 8GB of RAM (16GB+ recommended for running LLMs smoothly)

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
    *Note: The default settings are optimized for local Docker execution.*

3.  **Start the services:**
    ```bash
    docker-compose up -d --build
    ```
    *Note: On first start, Ollama will automatically pull the `llama3` model. This may take a few minutes depending on your internet speed.*

4.  **Verify the services:**
    - API: `http://localhost:8000/docs` (Swagger UI)
    - Qdrant: `http://localhost:6333/dashboard`
    - Redis: `redis://localhost:6379`

### Local Development Setup (Manual)

If you prefer to run the FastAPI application and Celery worker directly on your host (e.g., for faster debugging), follow these steps:

#### 1. Install System Dependencies
On macOS (using Homebrew):
```bash
brew install tesseract poppler
```
On Ubuntu/Debian:
```bash
sudo apt-get update && sudo apt-get install -y tesseract-ocr poppler-utils
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Run Supporting Services
You still need Redis and Qdrant. Use Docker for just these:
```bash
docker run -d -p 6379:6379 redis:alpine
docker run -d -p 6333:6333 qdrant/qdrant:latest
```

#### 4. Setup Ollama
Install [Ollama](https://ollama.com/) and pull the model:
```bash
ollama serve
ollama pull llama3
```

#### 5. Run Application & Worker
Set your environment variables in `.env` (point `REDIS_URL`, `QDRANT_URL`, etc., to `localhost` instead of container names) and run:

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
- **Returns:** `task_id` for status polling.

### 2. Check Ingestion Status
- **Endpoint:** `GET /api/v1/documents/status/{task_id}`
- **Returns:** Processing status (`PENDING`, `SUCCESS`, `FAILURE`).

### 3. Ask a Question (RAG)
Get a citation-backed answer from your documents.
- **Endpoint:** `POST /api/v1/ask`
- **Payload:** `{"query": "Your question here"}`
- **Returns:** `{"answer": "...", "sources": [...]}`

### 4. Hybrid Search
Raw retrieval for search-only use cases.
- **Endpoint:** `POST /api/v1/search`
- **Payload:** `{"query": "Search keywords", "limit": 5}`
- **Returns:** List of relevant document snippets.

### 5. Delete Document
Remove a document and its vectors.
- **Endpoint:** `DELETE /api/v1/documents/{document_id}`

## 📂 Project Structure

```text
.
├── app/
│   ├── api/v1/             # API Route handlers
│   ├── core/               # Configuration & Settings
│   ├── services/           # Core logic (RAG, Ingestion)
│   ├── utils/              # Document parsers & helpers
│   ├── worker/             # Celery task definitions
│   └── main.py             # FastAPI entry point
├── docs/                   # Design specs & implementation plans
├── tests/                  # Verification & Mock tests
├── docker-compose.yml      # Infrastructure orchestration
├── Dockerfile              # App & Worker image definition
└── requirements.txt        # Python dependencies
```

## 🔒 Security & Performance

- **Data Privacy:** 100% on-premise. No data ever leaves your network.
- **Performance:** Ingestion is offloaded to background workers to keep the API responsive.
- **Reliability:** Service initialization is handled via FastAPI `lifespan` events to ensure Qdrant and Ollama are ready before the app accepts requests.

## 📄 License

MIT
