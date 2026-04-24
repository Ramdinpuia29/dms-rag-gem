# Acceptance Criteria: RAG Microservice

**Spec:** `docs/superpowers/specs/2026-04-24-rag-design.md`
**Date:** 2026-04-24
**Status:** Approved

---

## Criteria

| ID | Description | Test Type | Preconditions | Expected Result |
|----|-------------|-----------|---------------|-----------------|
| AC-001 | Ingest text-based docs | API | Valid .pdf, .docx, .txt, .md, .csv, .xlsx | HTTP 202, returns `task_id` |
| AC-002 | Check ingestion status | API | Valid `task_id` from AC-001 | HTTP 200, status "completed" |
| AC-003 | Hybrid search retrieval | API | Document ingested (AC-001) | HTTP 200, list of relevant chunks with metadata |
| AC-004 | RAG Question Answering | API | Document ingested (AC-001) | HTTP 200, answer based ONLY on context + citations |
| AC-005 | Hallucination prevention | API | Query about info NOT in doc | HTTP 200, answer contains "Information not available" |
| AC-006 | Ingest images/scanned docs (OCR) | API | Scanned PDF, .jpg, or .png | HTTP 202, task completes, text extracted and searchable |
| AC-007 | Delete document | API | Valid `document_id` exists | HTTP 200, document removed from Qdrant |
