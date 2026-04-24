# Module: Ingestion Service

**Path:** `app/services/ingestion.py`
**Responsibility:** Document parsing, chunking, and vector indexing.

## Roles
- `embed_model`: Module-level singleton for `HuggingFaceEmbedding` (BGE-M3).
- `node_parser`: Module-level singleton for `SentenceSplitter`.
- `get_vector_store()`: Factory function for `PGVectorStore` connection.

## Key Procedures
- `ingest_document(file_path, metadata)`: The main ingestion pipeline. **Passes models explicitly to `VectorStoreIndex.from_documents` to avoid global settings race conditions.**
- `get_vector_store()`: Configures `PGVectorStore` with `text_search_config="simple"` to properly support Mizo language lexical search.
- `delete_document(document_id)`: Removes documents by metadata filter.

## Dependencies
- `llama_index.vector_stores.postgres`: Vector storage backend.
- `app.utils.parsers`: Custom document parsing logic.
- `app.core.config.settings`: Infrastructure configuration.
