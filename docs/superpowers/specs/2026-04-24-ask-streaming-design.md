# RAG Streaming Response Design

Design for implementing real-time response streaming in the `ask` endpoint using Server-Sent Events (SSE).

## Purpose
Reduce perceived latency by delivering LLM tokens as they are generated, while maintaining RAG transparency by providing source citations before or during the stream.

## Architecture
- **Protocol**: Server-Sent Events (SSE) via FastAPI `StreamingResponse`.
- **Engine**: LlamaIndex `RetrieverQueryEngine` with `streaming=True`.
- **Format**: Newline-delimited JSON messages prefixed with `data: `.

## Components

### RAG Service (`app/services/rag.py`)
- Add `ask_stream(query: str)` method.
- Initialize `RetrieverQueryEngine` with `streaming=True`.
- Use `query_engine.stream_query(query)`.
- Extract `source_nodes` immediately after the query call but before iterating the stream.

### API Layer (`app/api/v1/ask.py`)
- New endpoint `POST /api/v1/ask/stream` (or update existing).
- Generator function to yield SSE formatted chunks:
    1.  `{"type": "sources", "data": [...]}`
    2.  `{"type": "token", "data": "..."}` for each token.
    3.  `{"type": "done"}` signal.

## Data Flow
1. Client sends query.
2. `RAGService` retrieves and reranks documents.
3. `RAGService` starts LLM generation.
4. Server sends `sources` event to client.
5. Server loops through LLM token generator, sending `token` events.
6. Server sends `done` event and closes connection.

## Error Handling
- Catch exceptions during retrieval or generation.
- Send `{"type": "error", "data": "..."}` event before closing if possible.
- Fallback to standard HTTP error codes if the stream hasn't started.

## Verification
- Manual verification via `curl -N`.
- Unit test for generator output format.
