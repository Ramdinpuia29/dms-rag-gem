# Memory Update Report: Mizo Search and Concurrency

**Date:** 2026-04-24
**Cycle Goal:** Fix Mizo search accuracy and resolve LlamaIndex race conditions.

## Durable Changes

### Modules
- **RAG Service** (`docs/superpowers/memory/modules/rag-service.md`): Updated to reflect local model management and removal of global state.
- **Ingestion Service** (`docs/superpowers/memory/modules/ingestion-service.md`): Created canonical documentation for the ingestion pipeline, documenting the transition to module-level singleton models and explicit injection.

### Decisions
- **Mizo Search Config** (`docs/superpowers/memory/decisions/mizo-search-config.md`): Documented the move to `text_search_config="simple"` in PostgreSQL to support Mizo language lexical search.
- **Thread-Safe Injection** (`docs/superpowers/memory/decisions/thread-safe-injection.md`): Recorded the architectural decision to avoid global `llama_index.core.Settings` mutation in concurrent environments.

## Commit IDs
- `cf1d22d`: fix(ingestion): use simple text search for Mizo and remove global settings
- `e95c873`: fix(rag): remove global settings and inject models explicitly
- `631d6b6`: fix: cleanup init_ingestion_settings references and optimize ingestion

## Verification
- `tests/verification_mock.py`: 7/7 tests passed.
- Manual verification of FastAPI startup.

## Gaps & Rejected Candidates
- **Mizo Stemmer**: Rejected building a custom Mizo stemmer for now in favor of `simple` configuration to minimize complexity while solving the immediate accuracy issue.
- **Dependency Injection Framework**: Considered adding a formal DI library (like `fastapi-users` or `injector`), but rejected it as overkill for the current two-service architecture. Explicit manual injection is sufficient.

## Next Steps
- Monitor hybrid search precision for Mizo documents.
- Evaluate performance of `BGE-M3` vs `Mizo-4M` corpus fine-tuned embedding model.
