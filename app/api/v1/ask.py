import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from app.services.rag import rag_service

router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/")
async def ask_api(request: AskRequest):
    try:
        response = await run_in_threadpool(rag_service.ask, request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def ask_stream_api(request: AskRequest):
    async def event_generator():
        try:
            # rag_service.ask_stream is synchronous and heavy (does retrieval and reranking)
            # We run the initialization in a threadpool to get the generator
            generator = await run_in_threadpool(rag_service.ask_stream, request.query)
            for chunk in generator:
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
