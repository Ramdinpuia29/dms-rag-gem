# Streaming Response Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. It will decide whether each batch should run in parallel or serial subagent mode and will pass only task-local context to each subagent. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement real-time response streaming for the `ask` endpoint using Server-Sent Events (SSE) and LlamaIndex's streaming capabilities.

**Architecture:** Extend `RAGService` to return a generator from LlamaIndex's `stream_query`. FastAPI's `StreamingResponse` will be used to deliver JSON-wrapped events (`sources`, `token`, `done`, `error`) over SSE.

**Tech Stack:** FastAPI, LlamaIndex, Ollama, SSE.

---

### Task 1: Extend RAGService with streaming

**Files:**
- Modify: `app/services/rag.py`

- [ ] **Step 1: Add `ask_stream` method to `RAGService`**

```python
    def ask_stream(self, query: str):
        """
        Streams an answer using the RAG pipeline.
        Yields: dicts for sources and tokens.
        """
        system_prompt = (
            "Answer ONLY based on the provided context. "
            "If the answer is not in the context, explicitly say: 'Information not available.' "
            "No hallucinations. Provide source citations."
        )
        
        retriever = VectorIndexRetriever(
            index=self.index, 
            similarity_top_k=10,
            vector_store_query_mode="hybrid"
        )
        
        # Build query engine with streaming enabled
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[self.reranker],
            system_prompt=system_prompt,
            streaming=True
        )
        
        streaming_response = query_engine.query(query)
        
        # Yield sources first
        sources = []
        for node in streaming_response.source_nodes:
            sources.append({
                "content": node.node.get_content()[:200] + "...",
                "metadata": node.node.metadata,
                "score": node.score
            })
        yield {"type": "sources", "data": sources}
        
        # Yield tokens
        for token in streaming_response.response_gen:
            yield {"type": "token", "data": token}
            
        yield {"type": "done"}
```

- [ ] **Step 2: Commit**

```bash
git add app/services/rag.py
git commit -m "feat(rag): add streaming support to RAGService"
```

---

### Task 2: Implement Streaming API Endpoint

**Files:**
- Modify: `app/api/v1/ask.py`

- [ ] **Step 1: Add streaming endpoint to `app/api/v1/ask.py`**

```python
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.rag import rag_service

router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/")
async def ask_api(request: AskRequest):
    try:
        response = rag_service.ask(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def ask_stream_api(request: AskRequest):
    def event_generator():
        try:
            for chunk in rag_service.ask_stream(request.query):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

- [ ] **Step 2: Commit**

```bash
git add app/api/v1/ask.py
git commit -m "feat(api): add /stream endpoint for ask"
```

---

### Task 3: Verification

- [ ] **Step 1: Start the application**

Run: `docker-compose up --build` (if running in docker) or `uvicorn app.main:app --host 0.0.0.0 --port 8000`

- [ ] **Step 2: Test streaming with curl**

Run:
```bash
curl -X POST http://localhost:8000/api/v1/ask/stream \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the project about?"}' \
     -N
```

Expected:
- Immediate chunk with `type: sources`.
- Sequential chunks with `type: token`.
- Final chunk with `type: done`.

- [ ] **Step 3: Verify citations**

Check if the `sources` chunk metadata matches expectations.
