"""Runtime config/context-budget adapter for PS-agent."""

from core.config import get_config
from core.prompt.context_manager import ContextBlock, ContextBudget


def get_runtime_config():
    return get_config()


__all__ = ["ContextBlock", "ContextBudget", "get_runtime_config"]
