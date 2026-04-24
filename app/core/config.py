from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/dms_rag"
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama3"
    EMBED_MODEL: str = "BAAI/bge-m3"
    RERANK_MODEL: str = "BAAI/bge-reranker-v2-m3"
    UPLOAD_DIR: str = "/app/uploads"
    QUERY_CACHE_TTL: int = 3600
    LLM_REQUEST_TIMEOUT: float = 300.0

settings = Settings()
