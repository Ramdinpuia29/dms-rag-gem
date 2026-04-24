# Contract: API Contract

Defines the public interfaces for the DMS RAG API.

## Endpoints

### `POST /api/v1/ask/`
Synchronous Q&A.
- **Request:** `{"query": "string"}`
- **Response:** `{"answer": "string", "sources": [{"content": "...", "metadata": {}, "score": 0.0}]}`

### `POST /api/v1/ask/stream`
Streaming Q&A using SSE.
- **Request:** `{"query": "string"}`
- **Response:** `text/event-stream`
- **Events:**
    - `sources`: `{"type": "sources", "data": [...]}`
    - `token`: `{"type": "token", "data": "..."}`
    - `done`: `{"type": "done"}`
    - `error`: `{"type": "error", "data": "..."}`

### `POST /api/v1/search/`
Vector search without LLM generation.
- **Request:** `{"query": "string", "limit": 10}`
- **Response:** `{"results": [...]}`

### `POST /api/v1/documents/ingest`
Upload and vectorize document.
- **Request:** `multipart/form-data`
- **Response:** `{"task_id": "string", "document_id": "string"}`
