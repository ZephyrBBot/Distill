"""Explicit adapter layer for PS-agent root couplings.

These adapters isolate intentional dependencies on legacy `core.*` and
`agent.tools.*` modules behind PS-agent-local interfaces.
"""

from .embedding import EmbeddingError, embed_texts, is_embedding_configured
from .feeds_memory import get_all_feeds, get_recent_feed_update, search_memory
from .content_store import fetch_feed_contents
from .context_budget import ContextBlock, ContextBudget, get_runtime_config

__all__ = [
    "ContextBlock",
    "ContextBudget",
    "EmbeddingError",
    "embed_texts",
    "fetch_feed_contents",
    "get_all_feeds",
    "get_recent_feed_update",
    "get_runtime_config",
    "is_embedding_configured",
    "search_memory",
]
