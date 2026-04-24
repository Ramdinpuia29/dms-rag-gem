from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"
    OLLAMA_URL: str = "http://localhost:11434"
    MODEL_NAME: str = "llama3"
    EMBED_MODEL: str = "BAAI/bge-m3"

settings = Settings()
