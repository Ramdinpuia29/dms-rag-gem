import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.worker.tasks import ingest_document_task, celery_app
from app.services.ingestion import delete_document
from app.core.config import settings
from celery.result import AsyncResult
import aiofiles

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".txt", ".md", ".png", ".jpg", ".jpeg"}
_MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/ingest")
async def ingest_document_api(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    file_id = str(uuid.uuid4())
    # Strip path components from filename to prevent directory traversal
    safe_name = Path(file.filename).name
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{safe_name}")

    try:
        size = 0
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1 MB chunks
                size += len(chunk)
                if size > _MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="File too large (max 50 MB)")
                await buffer.write(chunk)

        task = ingest_document_task.delay(file_path, {"document_id": file_id, "filename": file.filename})
        return {"task_id": task.id, "document_id": file_id}
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }


@router.delete("/{document_id}")
async def delete_document_api(document_id: str):
    try:
        result = delete_document(document_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
