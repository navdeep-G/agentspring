"""
This module has been deprecated. Embedding functionality is not available with the mock provider.
"""

class EmbeddingsNotAvailableError(NotImplementedError):
    """Raised when embedding functionality is not available with the current provider."""
    pass

def get_embedding(text: str) -> list[float]:
    """Get embedding for text (stub implementation)."""
    raise EmbeddingsNotAvailableError("Embeddings are not available with the mock provider")
