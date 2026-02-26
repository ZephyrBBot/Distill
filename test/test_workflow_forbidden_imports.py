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

    def test_workflow_related_modules_use_distill_lib_agent_models(self):
        root = Path(__file__).resolve().parent.parent
        targets = [
            root / "agent" / "tools" / "db_tool.py",
            root / "agent" / "tools" / "memory_tool.py",
            root / "agent" / "workflow" / "db_providers.py",
        ]
        for py_file in targets:
            self._assert_no_forbidden_imports(py_file, {"agent.models"})

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
        for py_file in lib_agent_dir.rglob("*.py"):
            self._assert_no_forbidden_imports(
                py_file,
                forbidden_roots,
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

    def test_ps_agent_and_backend_use_distill_lib_for_workflow_utils_and_tools(self):
        root = Path(__file__).resolve().parent.parent
        targets = [
            root / "agent" / "ps_agent" / "__init__.py",
            root / "agent" / "ps_agent" / "utils" / "content_fetcher.py",
            root / "agent" / "ps_agent" / "tools" / "__init__.py",
            root / "agent" / "ps_agent" / "tools" / "handlers.py",
            root / "agent" / "ps_agent" / "nodes" / "planner" / "bootstrap.py",
            root / "agent" / "ps_agent" / "nodes" / "planner" / "structure.py",
            root / "agent" / "ps_agent" / "nodes" / "evaluator" / "audit_analyzer.py",
            root / "agent" / "ps_agent" / "nodes" / "evaluator" / "batch_audit.py",
            root / "agent" / "ps_agent" / "nodes" / "evaluator" / "plan_reviewer.py",
            root / "agent" / "ps_agent" / "nodes" / "evaluator" / "summary_reviewer.py",
            root / "apps" / "backend" / "services" / "setting_service.py",
        ]

        forbidden_roots = {
            "agent.utils",
            "agent.tools",
            "agent.tools.search_tool",
            "agent.tools.filter_tool",
            "agent.tools.writing_tool",
            "core.llm_client",
        }
        allowed_from = {
            "agent.tools.db_tool",
            "agent.tools.memory_tool",
        }
        for py_file in targets:
            self._assert_no_forbidden_imports(py_file, forbidden_roots, allowed_from)

    def test_ps_agent_has_no_core_llm_client_imports(self):
        ps_agent_dir = Path(__file__).resolve().parent.parent / "agent" / "ps_agent"
        for py_file in ps_agent_dir.rglob("*.py"):
            self._assert_no_forbidden_imports(py_file, {"core.llm_client"})

    def test_ps_agent_intentional_root_db_couplings_are_allowlisted(self):
        root = Path(__file__).resolve().parent.parent
        expected = {
            str(root / "agent" / "ps_agent" / "adapters" / "content_store.py"): {
                "core.db.pool",
            },
            str(root / "agent" / "ps_agent" / "adapters" / "feeds_memory.py"): {
                "agent.tools.db_tool",
                "agent.tools.memory_tool",
            },
            str(root / "agent" / "ps_agent" / "adapters" / "embedding.py"): {
                "core.embedding",
            },
            str(root / "agent" / "ps_agent" / "adapters" / "context_budget.py"): {
                "core.config",
                "core.prompt.context_manager",
            },
            str(root / "apps" / "backend" / "services" / "setting_service.py"): {
                "core.config.loader",
                "core.config.utils",
                "core.models.config",
            },
        }

        for file_path, allowed_modules in expected.items():
            py_file = Path(file_path)
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith(("core.", "agent.tools")):
                        imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith(("core.", "agent.tools")):
                            imports.add(alias.name)

            unexpected = imports - allowed_modules
            self.assertFalse(
                unexpected,
                f"Unexpected root coupling imports in {py_file}: {sorted(unexpected)}",
            )


if __name__ == "__main__":
    unittest.main()
