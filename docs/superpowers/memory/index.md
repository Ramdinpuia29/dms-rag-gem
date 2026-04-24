# Repository Memory: DMS RAG Gem

Canonical memory for the 100% local RAG microservice.

## Modules
- [RAG Service](modules/rag-service.md) - Core retrieval and generation logic.
- [Ingestion Service](modules/ingestion-service.md) - Document parsing and vectorization.

## Contracts
- [API Contract](contracts/api-contract.md) - Endpoint definitions and data formats.

## Decisions
- [pgvector Stack](decisions/pgvector-stack.md) - Use of PostgreSQL and pgvector for local vector storage.
- [Mizo Search Config](decisions/mizo-search-config.md) - Simple text search to support Mizo.
- [Thread-Safe Injection](decisions/thread-safe-injection.md) - Avoiding global LlamaIndex Settings.
