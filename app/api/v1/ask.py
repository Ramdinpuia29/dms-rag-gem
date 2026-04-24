import asyncio
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from app.services.rag import rag_service
from app.core.config import settings

router = APIRouter()


class AskRequest(BaseModel):
    query: str = Field(..., max_length=2000)


@router.post("/")
async def ask_api(request: AskRequest):
    try:
        response = await asyncio.wait_for(
            run_in_threadpool(rag_service.ask, request.query),
            timeout=settings.LLM_REQUEST_TIMEOUT,
        )
        return response
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail=f"LLM did not respond within {settings.LLM_REQUEST_TIMEOUT}s")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def ask_stream_api(request: AskRequest):
    async def event_generator():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def produce():
            try:
                for chunk in rag_service.ask_stream(request.query):
                    loop.call_soon_threadsafe(queue.put_nowait, ("chunk", chunk))
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, ("error", str(e)))
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, ("done", None))

        loop.run_in_executor(None, produce)

        while True:
            kind, data = await queue.get()
            if kind == "done":
                break
            elif kind == "error":
                yield f"data: {json.dumps({'type': 'error', 'data': data})}\n\n"
                break
            else:
                yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
