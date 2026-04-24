from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag import rag_service

router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/")
async def ask_api(request: AskRequest):
    response = rag_service.ask(request.query)
    return response
