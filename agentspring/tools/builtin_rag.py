"""
This module has been deprecated. RAG functionality is not available with the mock provider.
"""

class RAGNotAvailableError(NotImplementedError):
    """Raised when RAG functionality is not available with the current provider."""
    pass

def search_documents(query: str, top_k: int = 5) -> list[dict]:
    """Search documents (stub implementation)."""
    raise RAGNotAvailableError("RAG is not available with the mock provider")
