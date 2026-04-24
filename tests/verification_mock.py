import unittest
import sys
from unittest.mock import MagicMock, patch

# Mock heavy dependencies
mock_modules = [
    "sqlalchemy",
    "sqlalchemy.orm",
    "llama_index",
    "llama_index.core",
    "llama_index.core.retrievers",
    "llama_index.core.query_engine",
    "llama_index.core.postprocessor",
    "llama_index.llms.ollama",
    "llama_index.embeddings.huggingface",
    "llama_index.vector_stores.postgres",
    "llama_index.core.node_parser",
    "llama_index.core.storage_context",
    "celery",
    "celery.result",
    "redis"
]

for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Mock initializations and specific service objects
with patch("app.services.ingestion.init_ingestion_settings"), \
     patch("app.services.rag.rag_service.initialize"):
    from app.main import app

from fastapi.testclient import TestClient

class TestRAGAcceptance(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.v1.documents.ingest_document_task.delay")
    def test_ac_001_ingest_document(self, mock_delay):
        """AC-001: Ingest text-based docs"""
        # Mocking celery task delay
        mock_task = MagicMock()
        mock_task.id = "test-task-id"
        mock_delay.return_value = mock_task

        file_content = b"test content"
        response = self.client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.txt", file_content, "text/plain")}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["task_id"], "test-task-id")
        self.assertIn("document_id", response.json())
        mock_delay.assert_called_once()

    @patch("app.api.v1.documents.AsyncResult")
    def test_ac_002_check_status(self, mock_async_result):
        """AC-002: Check ingestion status"""
        # Mocking AsyncResult status
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.result = {"status": "success"}
        mock_async_result.return_value = mock_result

        response = self.client.get("/api/v1/documents/status/test-task-id")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "SUCCESS")
        mock_async_result.assert_called_once()

    @patch("app.api.v1.search.rag_service")
    def test_ac_003_hybrid_search(self, mock_rag_service):
        """AC-003: Hybrid search retrieval"""
        # Mock nodes
        mock_node = MagicMock()
        mock_node.node.get_content.return_value = "relevant content"
        mock_node.node.metadata = {"doc_id": "1"}
        mock_node.score = 0.9
        
        mock_rag_service.hybrid_search.return_value = [mock_node]
        mock_rag_service.rerank.return_value = [mock_node]

        response = self.client.post(
            "/api/v1/search/",
            json={"query": "test query"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()["results"]) > 0)
        self.assertEqual(response.json()["results"][0]["content"], "relevant content")

    @patch("app.api.v1.ask.rag_service")
    def test_ac_004_rag_qa(self, mock_rag_service):
        """AC-004: RAG Question Answering"""
        mock_rag_service.ask.return_value = {
            "answer": "This is the answer.",
            "sources": [{"content": "source text", "metadata": {}}]
        }

        response = self.client.post(
            "/api/v1/ask/",
            json={"query": "what is the answer?"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "This is the answer.")

    @patch("app.api.v1.ask.rag_service")
    def test_ac_005_hallucination_prevention(self, mock_rag_service):
        """AC-005: Hallucination prevention"""
        mock_rag_service.ask.return_value = {
            "answer": "Information not available.",
            "sources": []
        }

        response = self.client.post(
            "/api/v1/ask/",
            json={"query": "something not in doc"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Information not available", response.json()["answer"])

    @patch("app.api.v1.documents.delete_document")
    def test_ac_007_delete_document(self, mock_delete):
        """AC-007: Delete document"""
        mock_delete.return_value = {"status": "success", "document_id": "test-doc-id"}

        response = self.client.delete("/api/v1/documents/test-doc-id")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["document_id"], "test-doc-id")

if __name__ == "__main__":
    unittest.main()
