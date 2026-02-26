import ast
from pathlib import Path
import unittest


class WorkflowForbiddenImportsTest(unittest.TestCase):
    def test_backend_workflow_db_provider_shim_removed(self):
        shim = (
            Path(__file__).resolve().parent.parent
            / "apps"
            / "backend"
            / "adapters"
            / "workflow_db_provider.py"
        )
        self.assertFalse(
            shim.exists(),
            "Legacy backend workflow_db_provider shim should not exist; use agent.workflow.db_providers directly.",
        )

    def _is_forbidden_module(
        self,
        module_name: str,
        forbidden_roots: set[str],
        allowed_from: set[str],
    ) -> bool:
        if module_name in allowed_from:
            return False
        for root in forbidden_roots:
            if module_name == root or module_name.startswith(f"{root}."):
                return True
        return False

    def _assert_no_forbidden_imports(
        self,
        py_file: Path,
        forbidden_roots: set[str],
        allowed_from: set[str] | None = None,
    ):
        allowed_from = allowed_from or set()
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if self._is_forbidden_module(node.module, forbidden_roots, allowed_from):
                    self.fail(f"Forbidden import {node.module} in {py_file}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_forbidden_module(alias.name, forbidden_roots, allowed_from):
                        self.fail(f"Forbidden import {alias.name} in {py_file}")

    def test_workflow_path_has_no_direct_db_tool_imports(self):
        workflow_dir = Path(__file__).resolve().parent.parent / "agent" / "workflow"
        forbidden = {"agent.tools.db_tool", "agent.tools.memory_tool"}
        for py_file in workflow_dir.glob("*.py"):
            self._assert_no_forbidden_imports(py_file, forbidden)

    def test_distill_lib_agent_layer_uses_canonical_imports(self):
        lib_agent_dir = (
            Path(__file__).resolve().parent.parent
            / "packages"
            / "distill_lib"
            / "src"
            / "distill_lib"
            / "agent"
        )
        forbidden_roots = {"agent", "core"}
        allowlist = {"agent.workflow.db_providers"}
        for py_file in lib_agent_dir.rglob("*.py"):
            self._assert_no_forbidden_imports(
                py_file,
                forbidden_roots,
                allowed_from=allowlist,
            )

    def test_distill_lib_core_layer_uses_canonical_imports(self):
        lib_core_dir = (
            Path(__file__).resolve().parent.parent
            / "packages"
            / "distill_lib"
            / "src"
            / "distill_lib"
            / "core"
        )
        forbidden_roots = {"agent", "core"}
        for py_file in lib_core_dir.rglob("*.py"):
            self._assert_no_forbidden_imports(py_file, forbidden_roots)


if __name__ == "__main__":
    unittest.main()
