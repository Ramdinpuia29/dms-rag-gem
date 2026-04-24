from celery import Celery
from app.core.config import settings

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="ingest_document")
def ingest_document_task(file_path: str, metadata: dict):
    # Logic to be implemented in Task 4
    return {"status": "success"}
