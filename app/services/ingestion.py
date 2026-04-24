from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from app.core.config import settings
from app.utils.parsers import parse_file
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Global Settings
Settings.embed_model = HuggingFaceEmbedding(model_name=settings.EMBED_MODEL)
Settings.node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

def get_vector_store():
    client = QdrantClient(url=settings.QDRANT_URL)
    return QdrantVectorStore(
        client=client, 
        collection_name="documents",
        enable_hybrid=True,
        batch_size=20
    )

def ingest_document(file_path: str, metadata: dict):
    """
    Parses a document, chunks it, embeds it, and stores it in Qdrant.
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
