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
