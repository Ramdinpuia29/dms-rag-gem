from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from sqlalchemy import create_engine, make_url
from app.core.config import settings
from app.utils.parsers import parse_file
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global models and engine for reuse
embed_model = HuggingFaceEmbedding(
    model_name=settings.EMBED_MODEL,
    embed_batch_size=settings.EMBED_BATCH_SIZE
)
node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600
)
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = PGVectorStore(
            engine=_engine,
            table_name="documents",
            embed_dim=384,  # bge-small-en-v1.5 dimension
            hybrid_search=True,
            text_search_config="simple",
        )
    return _vector_store

def ingest_document(file_path: str, metadata: dict):
    """
    Parses a document, chunks it, embeds it, and stores it in PostgreSQL.
    """
    try:
        logger.info(f"Starting ingestion for: {file_path}")
        
        # 1. Parse document
        documents = parse_file(file_path)
        
        # 2. Add metadata
        for doc in documents:
            doc.metadata.update(metadata)
            
        # 3. Initialize Vector Store and Storage Context
        vector_store = get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 4. Create Index (and store nodes)
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model,
            transformations=[node_parser],
            show_progress=False
        )
        
        logger.info(f"Successfully ingested: {file_path}")
        return {"status": "success", "file_path": file_path}
        
    except Exception as e:
        logger.error(f"Error ingesting document {file_path}: {str(e)}")
        raise e
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")

def delete_document(document_id: str):
    """
    Deletes a document from PostgreSQL by its document_id metadata.
    """
    try:
        vector_store = get_vector_store()
        filters = MetadataFilters(
            filters=[
                ExactMatchFilter(key="document_id", value=document_id)
            ]
        )
        vector_store.delete_nodes(filters=filters)
        logger.info(f"Successfully deleted document: {document_id}")
        return {"status": "success", "document_id": document_id}
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise e
