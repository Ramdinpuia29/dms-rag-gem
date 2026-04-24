from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter
from sqlalchemy import make_url
from app.core.config import settings
from app.utils.parsers import parse_file
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_ingestion_settings():
    """
    Initializes global LlamaIndex settings.
    """
    Settings.embed_model = HuggingFaceEmbedding(model_name=settings.EMBED_MODEL)
    Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

def get_vector_store():
    url = make_url(settings.DATABASE_URL)
    embed_model = HuggingFaceEmbedding(model_name=settings.EMBED_MODEL)
    return PGVectorStore.from_params(
        host=url.host,
        port=url.port,
        database=url.database,
        user=url.username,
        password=url.password,
        table_name="documents",
        embed_dim=1024,  # BGE-M3 dimension
        hybrid_search=True,
        text_search_config="english",
        embed_model=embed_model
    )

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
        # VectorStoreIndex.from_documents will insert documents into the vector store
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
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
