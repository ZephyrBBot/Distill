"""Agent-layer exports for distill_lib."""

from distill_lib.agent.executor import AgentExecutor
from distill_lib.agent.models import *  # noqa: F401,F403
from distill_lib.agent.planner import AgentPlanner
from distill_lib.agent.providers import *  # noqa: F401,F403

__all__ = ["AgentPlanner", "AgentExecutor", "SummarizeAgenticWorkflow"]


def __getattr__(name: str):
    if name == "SummarizeAgenticWorkflow":
        from distill_lib.agent.workflow import SummarizeAgenticWorkflow

        return SummarizeAgenticWorkflow
    raise AttributeError(name)
