from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/dms_rag"
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "phi3:mini"
    EMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    RERANK_MODEL: str = "BAAI/bge-reranker-base"
    UPLOAD_DIR: str = "/app/uploads"
    EMBED_BATCH_SIZE: int = 32
    QUERY_CACHE_TTL: int = 3600
    LLM_REQUEST_TIMEOUT: float = 300.0

settings = Settings()
