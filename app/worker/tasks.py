from celery import Celery
from app.core.config import settings
from app.services.ingestion import ingest_document

celery_app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="ingest_document")
def ingest_document_task(file_path: str, metadata: dict):
    return ingest_document(file_path, metadata)
