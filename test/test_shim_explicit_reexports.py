from __future__ import annotations

import ast
from pathlib import Path
import unittest


TARGETED_SHIMS = (
    "agent/models.py",
    "agent/prompts.py",
    "agent/tools/filter_tool.py",
    "agent/tools/search_tool.py",
    "agent/tools/writing_tool.py",
    "agent/utils.py",
    "agent/workflow/executor.py",
    "agent/workflow/planner.py",
    "agent/workflow/providers.py",
    "core/config/loader.py",
    "core/config/utils.py",
    "core/crawler/crawler.py",
    "core/crawler/search_engine.py",
    "core/llm_client.py",
)


class ShimExplicitReexportStyleTest(unittest.TestCase):
    def test_no_wildcard_imports_in_targeted_shims(self):
        root = Path(__file__).resolve().parent.parent
        for rel in TARGETED_SHIMS:
            text = (root / rel).read_text(encoding="utf-8")
            self.assertNotIn("import *", text, f"{rel} should not use wildcard re-exports")

    def test_targeted_shims_are_implementation_free(self):
        root = Path(__file__).resolve().parent.parent
        for rel in TARGETED_SHIMS:
            tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
            for node in ast.walk(tree):
                self.assertNotIsInstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef), rel)

    def test_targeted_shims_define_all(self):
        root = Path(__file__).resolve().parent.parent
        for rel in TARGETED_SHIMS:
            tree = ast.parse((root / rel).read_text(encoding="utf-8"), filename=rel)
            has_all = any(
                isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets)
                for node in tree.body
            )
            self.assertTrue(has_all, f"{rel} should define __all__ explicitly")


if __name__ == "__main__":
    unittest.main()
