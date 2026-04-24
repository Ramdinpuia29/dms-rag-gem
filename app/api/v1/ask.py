from fastapi import APIRouter, HTTPException
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
