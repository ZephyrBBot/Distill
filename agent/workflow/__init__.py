"""Compatibility export for workflow orchestration implementation in distill_lib."""

__all__ = ["SummarizeAgenticWorkflow"]


def __getattr__(name: str):
    if name == "SummarizeAgenticWorkflow":
        from distill_lib.workflow import SummarizeAgenticWorkflow

        return SummarizeAgenticWorkflow
    raise AttributeError(name)
