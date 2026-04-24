# Decision: Thread-Safe Model Injection

## Context
In a FastAPI environment with concurrent requests, mutating the global `llama_index.core.Settings` object (standard in many LlamaIndex tutorials) creates race conditions where one request might overwrite the embedding model or LLM of another.

## Decision
Avoid global `Settings` mutation. Instantiate models locally or as class properties and pass them explicitly to LlamaIndex components.

## Rationales
- **Thread Safety**: Prevents cross-request state leakage in high-concurrency scenarios.
- **Explicitness**: Makes dependencies clear and easier to test/mock.
- **Predictability**: Ensures that each service instance uses exactly the models it was initialized with.

## Implementation
- `app/services/rag.py`: `RAGService` stores `self.llm` and `self.embed_model`.
- `app/services/ingestion.py`: Models are module-level singletons passed to `VectorStoreIndex.from_documents`.

## Related
- [RAG Service](../modules/rag-service.md)
- [Ingestion Service](../modules/ingestion-service.md)
