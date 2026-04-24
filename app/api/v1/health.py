from fastapi import APIRouter
import redis
from sqlalchemy import create_engine, text
import httpx
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Checks the health of the microservice and its dependencies.
    """
    status = {
        "status": "healthy",
        "services": {
            "redis": "unknown",
            "postgres": "unknown",
            "ollama": "unknown"
        }
    }
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        if r.ping():
            status["services"]["redis"] = "healthy"
        else:
            status["services"]["redis"] = "unhealthy"
            status["status"] = "degraded"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    # Check Postgres
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["services"]["postgres"] = "healthy"
    except Exception as e:
        status["services"]["postgres"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=2.0)
            if resp.status_code == 200:
                status["services"]["ollama"] = "healthy"
            else:
                status["services"]["ollama"] = f"unhealthy: status {resp.status_code}"
                status["status"] = "degraded"
    except Exception as e:
        status["services"]["ollama"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    return status
