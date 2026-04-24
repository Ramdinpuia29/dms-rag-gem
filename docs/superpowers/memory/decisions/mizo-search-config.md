# Decision: Mizo Search Configuration

## Context
The project supports Mizo language RAG. PostgreSQL's default `english` text search configuration performs aggressive stemming (e.g., removing 's', 'ing', 'ed') which is linguistically incorrect for Mizo and degrades hybrid search (lexical BM25) accuracy.

## Decision
Configure `PGVectorStore` with `text_search_config="simple"`.

## Rationales
- **Linguistic Integrity**: The `simple` configuration performs basic whitespace tokenization and case folding without attempting language-specific stemming.
- **Improved Retrieval**: Prevents false negatives caused by incorrect English stemming of Mizo words.
- **Multilingual Support**: Compatible with the `BGE-M3` multilingual embedding model used for the dense search component.

## Implementation
Set `text_search_config="simple"` in `app/services/ingestion.py:get_vector_store()`.

## Related
- [Ingestion Service](../modules/ingestion-service.md)
