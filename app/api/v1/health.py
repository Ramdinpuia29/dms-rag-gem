from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
import redis
from sqlalchemy import create_engine, text
import httpx
from app.core.config import settings

router = APIRouter()

# Singletons — avoid rebuilding connections on every health check
_redis_client = redis.from_url(settings.REDIS_URL)
_db_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=2,
    max_overflow=0,
    pool_pre_ping=True,
)


@router.get("/")
async def health_check():
    status = {
        "status": "healthy",
        "services": {
            "redis": "unknown",
            "postgres": "unknown",
            "ollama": "unknown",
        },
    }

    try:
        if _redis_client.ping():
            status["services"]["redis"] = "healthy"
        else:
            status["services"]["redis"] = "unhealthy"
            status["status"] = "degraded"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    try:
        def _db_ping():
            with _db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        await run_in_threadpool(_db_ping)
        status["services"]["postgres"] = "healthy"
    except Exception as e:
        status["services"]["postgres"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                status["services"]["ollama"] = "healthy"
            else:
                status["services"]["ollama"] = f"unhealthy: status {resp.status_code}"
                status["status"] = "degraded"
    except Exception as e:
        status["services"]["ollama"] = f"unhealthy: {str(e)}"
        status["status"] = "degraded"

    return status
