from __future__ import annotations

import importlib
import sys
from pathlib import Path
import unittest


class WorkflowLibSubpackageImportTest(unittest.TestCase):
    def test_subpackage_source_importable_via_local_path(self):
        repo_root = Path(__file__).resolve().parent.parent
        package_src = repo_root / "packages" / "distill_lib" / "src"

        # Simulate skill-side local/path install resolution by importing from package src path.
        sys.path.insert(0, str(package_src))
        try:
            for mod_name in [
                "distill_lib",
                "distill_lib.api",
                "distill_lib.providers",
                "distill_lib.parsers",
                "distill_lib.rate_limiter",
            ]:
                sys.modules.pop(mod_name, None)

            package = importlib.import_module("distill_lib")
            api = importlib.import_module("distill_lib.api")
            parsers = importlib.import_module("distill_lib.parsers")
            rate_limiter = importlib.import_module("distill_lib.rate_limiter")

            self.assertIn("packages/distill_lib/src", package.__file__)
            self.assertIn("packages/distill_lib/src", api.__file__)
            self.assertIn("packages/distill_lib/src", parsers.__file__)
            self.assertIn("packages/distill_lib/src", rate_limiter.__file__)
            self.assertTrue(hasattr(api, "run_workflow_from_articles"))
            self.assertTrue(hasattr(parsers, "parse_opml"))
            self.assertTrue(hasattr(rate_limiter, "RateLimiter"))
        finally:
            if str(package_src) in sys.path:
                sys.path.remove(str(package_src))


if __name__ == "__main__":
    unittest.main()
