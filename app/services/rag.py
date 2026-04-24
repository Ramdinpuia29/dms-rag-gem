import asyncio
import hashlib
import json
import logging
import redis as redis_lib
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.services.ingestion import get_vector_store
from app.core.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Answer ONLY based on the provided context. "
    "If the answer is not in the context, explicitly say: 'Information not available.' "
    "No hallucinations. Provide source citations."
)


class RAGService:
    def __init__(self):
        self.vector_store = None
        self.index = None
        self.reranker = None
        self.embed_model = None
        self.llm = None
        self._retriever = None
        self._query_engine = None
        self._streaming_query_engine = None
        self._cache: redis_lib.Redis | None = None

    def initialize(self):
        Settings.embed_model = HuggingFaceEmbedding(
            model_name=settings.EMBED_MODEL,
            embed_batch_size=settings.EMBED_BATCH_SIZE
        )
        Settings.llm = Ollama(
            model=settings.MODEL_NAME,
            base_url=settings.OLLAMA_URL,
            request_timeout=settings.LLM_REQUEST_TIMEOUT,
        )

        self.embed_model = Settings.embed_model
        self.llm = Settings.llm

        self.vector_store = get_vector_store()
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            embed_model=self.embed_model,
        )

        self.reranker = SentenceTransformerRerank(
            model=settings.RERANK_MODEL,
            top_n=5,
        )

        # Build once, reuse across all requests — avoid per-request reconstruction overhead
        self._retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=10,
            vector_store_query_mode="hybrid",
        )
        self._query_engine = RetrieverQueryEngine.from_args(
            retriever=self._retriever,
            node_postprocessors=[self.reranker],
            system_prompt=_SYSTEM_PROMPT,
            llm=self.llm,
        )
        self._streaming_query_engine = RetrieverQueryEngine.from_args(
            retriever=self._retriever,
            node_postprocessors=[self.reranker],
            system_prompt=_SYSTEM_PROMPT,
            streaming=True,
            llm=self.llm,
        )

        try:
            self._cache = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
            self._cache.ping()
            logger.info("Query result cache connected")
        except Exception:
            logger.warning("Redis unavailable — query caching disabled")
            self._cache = None

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _cache_key(self, query: str) -> str:
        return f"rag:ask:{hashlib.md5(query.encode()).hexdigest()}"

    def _cache_get(self, query: str):
        if not self._cache:
            return None
        try:
            raw = self._cache.get(self._cache_key(query))
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def _cache_set(self, query: str, result: dict):
        if not self._cache:
            return
        try:
            self._cache.setex(
                self._cache_key(query),
                settings.QUERY_CACHE_TTL,
                json.dumps(result),
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def hybrid_search(self, query: str, limit: int = 10):
        if limit != 10:
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=limit,
                vector_store_query_mode="hybrid",
            )
            return retriever.retrieve(query)
        return self._retriever.retrieve(query)

    def rerank(self, nodes, query: str):
        return self.reranker.postprocess_nodes(nodes, query_str=query)

    def ask(self, query: str):
        cached = self._cache_get(query)
        if cached:
            return cached

        response = self._query_engine.query(query)

        sources = [
            {
                "content": node.node.get_content()[:200] + "...",
                "metadata": node.node.metadata,
                "score": node.score,
            }
            for node in response.source_nodes
        ]
        result = {"answer": str(response), "sources": sources}
        self._cache_set(query, result)
        return result

    def ask_stream(self, query: str):
        streaming_response = self._streaming_query_engine.query(query)

        sources = [
            {
                "content": node.node.get_content()[:200] + "...",
                "metadata": node.node.metadata,
                "score": node.score,
            }
            for node in streaming_response.source_nodes
        ]
        yield {"type": "sources", "data": sources}

        for token in streaming_response.response_gen:
            yield {"type": "token", "data": token}

        yield {"type": "done"}


rag_service = RAGService()
