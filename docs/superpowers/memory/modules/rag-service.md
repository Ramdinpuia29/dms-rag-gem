# Module: RAG Service

**Path:** `app/services/rag.py`
**Responsibility:** Orchestrates the retrieval-augmented generation pipeline.

## Roles
- `RAGService`: Singleton service handling vector search, reranking, and LLM querying.
- `self.embed_model`: Locally managed `HuggingFaceEmbedding` (BGE-M3).
- `self.llm`: Locally managed `Ollama` instance (Llama3).

## Key Procedures
- `initialize()`: Sets up model instances and vector store connection. **Crucially, it avoids global `llama_index.core.Settings` mutation to ensure thread safety.**
- `ask(query)`: Synchronous query-response with citations.
- `ask_stream(query)`: Streaming response using SSE (Server-Sent Events).

## Dependencies
- `app.services.ingestion.get_vector_store`: Provides the PGVector connection.
- `app.core.config.settings`: Global configuration.
- `llama_index`: Core RAG framework.
- `Ollama`: Local LLM provider.
