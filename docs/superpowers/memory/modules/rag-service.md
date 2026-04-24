# Module: RAG Service

**Path:** `app/services/rag.py`
**Responsibility:** Orchestrates the retrieval-augmented generation pipeline.

## Roles
- `RAGService`: Singleton service handling vector search, reranking, and LLM querying.
- `Settings.embed_model`: Global configuration for the embedding model (BGE-M3).
- `Settings.llm`: Global configuration for the LLM (Ollama/Llama3).

## Key Procedures
- `initialize()`: Sets up global `llama_index` settings and vector store connection.
- `ask(query)`: Synchronous query-response with citations.
- `ask_stream(query)`: Streaming response using SSE (Server-Sent Events).

## Dependencies
- `app.services.ingestion.get_vector_store`: Provides the PGVector connection.
- `app.core.config.settings`: Global configuration.
- `llama_index`: Core RAG framework.
- `Ollama`: Local LLM provider.
