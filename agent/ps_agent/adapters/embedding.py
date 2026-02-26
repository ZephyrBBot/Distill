"""Embedding adapter for PS-agent.

Intentionally couples to system embedding implementation while keeping
PS-agent callers decoupled from direct `core.embedding` imports.
"""

from core.embedding import EmbeddingError, embed_texts, is_embedding_configured

__all__ = ["EmbeddingError", "embed_texts", "is_embedding_configured"]
