from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import rag_service
from typing import List, Optional

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

@router.post("/")
async def search_api(request: SearchRequest):
    try:
        nodes = rag_service.hybrid_search(request.query, limit=request.limit)
        reranked_nodes = rag_service.rerank(nodes, request.query)
        
        results = []
        for node in reranked_nodes:
            results.append({
                "content": node.node.get_content(),
                "metadata": node.node.metadata,
                "score": node.score
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
