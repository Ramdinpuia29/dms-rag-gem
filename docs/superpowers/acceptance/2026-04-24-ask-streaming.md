# Acceptance Criteria: Streaming Response Implementation

**Spec:** `docs/superpowers/specs/2026-04-24-ask-streaming-design.md`
**Date:** 2026-04-24
**Status:** Approved

---

## Criteria

| ID | Description | Test Type | Preconditions | Expected Result |
|----|-------------|-----------|---------------|-----------------|
| AC-001 | API endpoint `POST /api/v1/ask/stream` exists | API | Server running | HTTP 200/OK response when query provided |
| AC-002 | Response has correct SSE content type | API | `POST /api/v1/ask/stream` called | Header `Content-Type: text/event-stream` present |
| AC-003 | Sources are sent as the first data chunk | API | Document exists in vector store, query matches | First line starting with `data: ` contains JSON with `"type": "sources"` |
| AC-004 | Answer is delivered as a stream of tokens | API | LLM starts generating | Multiple lines starting with `data: ` contain JSON with `"type": "token"` and non-empty `"data"` |
| AC-005 | Stream terminates with a done signal | API | LLM finished generating | Final line starting with `data: ` contains JSON with `"type": "done"` |
| AC-006 | Error event sent if retrieval or LLM fails | API | Service error triggered (e.g., Ollama down) | `data: ` line contains JSON with `"type": "error"` and error message |
| AC-007 | Citations in stream match source metadata | Logic | RAGService call | `sources` chunk metadata (filename, etc) matches what's in the DB for that chunk |
