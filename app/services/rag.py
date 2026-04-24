from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.postprocessor.sbert_rerank import SentenceTransformerRerank
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.services.ingestion import get_vector_store
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.vector_store = None
        self.index = None
        self.reranker = None
        self.embed_model = None
        self.llm = None

    def initialize(self):
        """
        Initializes the RAG service components.
        """
        # Explicitly instantiate models
        self.embed_model = HuggingFaceEmbedding(model_name=settings.EMBED_MODEL)
        self.llm = Ollama(model=settings.MODEL_NAME, base_url=settings.OLLAMA_URL, request_timeout=120.0)
        
        self.vector_store = get_vector_store()
        # Pass embed_model explicitly
        self.index = VectorStoreIndex.from_vector_store(
            self.vector_store,
            embed_model=self.embed_model
        )
        
        self.reranker = SentenceTransformerRerank(
            model=settings.RERANK_MODEL, 
            top_n=5
        )

    def hybrid_search(self, query: str, limit: int = 10):
        """
        Performs hybrid search (dense + sparse) using PostgreSQL.
        """
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=limit,
            vector_store_query_mode="hybrid"
        )
        return retriever.retrieve(query)

    def rerank(self, nodes, query: str):
        """
        Reranks the retrieved nodes using a cross-encoder model.
        """
        return self.reranker.postprocess_nodes(nodes, query_str=query)

    def ask(self, query: str):
        """
        Answers a query using the RAG pipeline with strict prompt and citations.
        """
        # Custom Prompt
        system_prompt = (
            "Answer ONLY based on the provided context. "
            "If the answer is not in the context, explicitly say: 'Information not available.' "
            "No hallucinations. Provide source citations."
        )
        
        # Configure the retriever for the query engine
        retriever = VectorIndexRetriever(
            index=self.index, 
            similarity_top_k=10,
            vector_store_query_mode="hybrid"
        )
        
        # Build query engine with reranker and explicit llm
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[self.reranker],
            system_prompt=system_prompt,
            llm=self.llm
        )
        
        response = query_engine.query(query)
        
        # Extract citations
        sources = []
        for node in response.source_nodes:
            sources.append({
                "content": node.node.get_content()[:200] + "...",
                "metadata": node.node.metadata,
                "score": node.score
            })
            
        return {
            "answer": str(response),
            "sources": sources
        }

    def ask_stream(self, query: str):
        """
        Streams an answer using the RAG pipeline.
        Yields: dicts for sources and tokens.
        """
        system_prompt = (
            "Answer ONLY based on the provided context. "
            "If the answer is not in the context, explicitly say: 'Information not available.' "
            "No hallucinations. Provide source citations."
        )
        
        retriever = VectorIndexRetriever(
            index=self.index, 
            similarity_top_k=10,
            vector_store_query_mode="hybrid"
        )
        
        # Build query engine with streaming enabled and explicit llm
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[self.reranker],
            system_prompt=system_prompt,
            streaming=True,
            llm=self.llm
        )
        
        streaming_response = query_engine.query(query)
        
        # Yield sources first
        sources = []
        for node in streaming_response.source_nodes:
            sources.append({
                "content": node.node.get_content()[:200] + "...",
                "metadata": node.node.metadata,
                "score": node.score
            })
        yield {"type": "sources", "data": sources}
        
        # Yield tokens
        for token in streaming_response.response_gen:
            yield {"type": "token", "data": token}
            
        yield {"type": "done"}

rag_service = RAGService()
