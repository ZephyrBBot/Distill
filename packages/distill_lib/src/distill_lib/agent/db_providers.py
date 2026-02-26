"""Optional DB-backed workflow provider adapters.

These adapters keep compatibility with legacy runtime wiring that uses
`agent.tools.*` modules. distill_lib itself remains standalone because the
imports are resolved lazily at call time.
"""

from __future__ import annotations

from importlib import import_module
from typing import Sequence

from distill_lib.agent.models import AgentState, RawArticle, SummaryMemory
from distill_lib.core.models.feed import FeedGroup


class DBWorkflowDataProvider:
    """Data provider backed by legacy DB tooling when available."""

    async def get_recent_group_update(
        self,
        hour_gap: int,
        group_ids: list[int] | None,
        focus: str = "",
    ) -> tuple[list[FeedGroup], list[RawArticle]]:
        db_tool = import_module("agent.tools.db_tool")
        return await db_tool.get_recent_group_update(hour_gap, group_ids or [], focus)


class DBWorkflowPersistenceProvider:
    """Persistence provider backed by legacy DB tooling when available."""

    async def save_current_execution_records(self, state: AgentState) -> None:
        memory_tool = import_module("agent.tools.memory_tool")
        await memory_tool.save_current_execution_records(state)


class DBWorkflowMemoryProvider:
    """Memory provider backed by legacy DB tooling when available."""

    async def search_memory(self, queries: Sequence[str]) -> dict[int, SummaryMemory]:
        memory_tool = import_module("agent.tools.memory_tool")
        return await memory_tool.search_memory(queries)


class DBWorkflowArticleContentProvider:
    """Article-content provider backed by legacy DB tooling when available."""

    async def get_article_content(self, article_ids: list[str]) -> dict[str, str]:
        db_tool = import_module("agent.tools.db_tool")
        return await db_tool.get_article_content(article_ids)


__all__ = [
    "DBWorkflowDataProvider",
    "DBWorkflowPersistenceProvider",
    "DBWorkflowMemoryProvider",
    "DBWorkflowArticleContentProvider",
]
