from pathlib import Path
import unittest

from core.config import get_config as core_get_config
from core.config.loader import get_config as core_loader_get_config
from core.config.utils import create_default_config as core_create_default_config
from core.crawler import fetch_all_contents as core_fetch_all_contents
from core.crawler.search_engine import search as core_search
from core.llm_client import APIKeyNotConfiguredError as CoreAPIKeyNotConfiguredError
from distill_lib.core.config.loader import get_config as canonical_get_config
from distill_lib.core.config.utils import create_default_config as canonical_create_default_config
from distill_lib.core.crawler import fetch_all_contents as canonical_fetch_all_contents
from distill_lib.core.crawler.search_engine import search as canonical_search
from distill_lib.core.llm_client import APIKeyNotConfiguredError as CanonicalAPIKeyNotConfiguredError


class CoreShimCanonicalImportTest(unittest.TestCase):
    def test_core_shims_alias_canonical_symbols(self):
        self.assertIs(core_get_config, canonical_get_config)
        self.assertIs(core_loader_get_config, canonical_get_config)
        self.assertIs(core_create_default_config, canonical_create_default_config)
        self.assertIs(core_fetch_all_contents, canonical_fetch_all_contents)
        self.assertIs(core_search, canonical_search)
        self.assertIs(CoreAPIKeyNotConfiguredError, CanonicalAPIKeyNotConfiguredError)

    def test_core_modules_are_thin_shims(self):
        project_root = Path(__file__).resolve().parent.parent
        for rel in (
            "core/config/loader.py",
            "core/config/utils.py",
            "core/crawler/crawler.py",
            "core/crawler/search_engine.py",
            "core/llm_client.py",
        ):
            text = (project_root / rel).read_text(encoding="utf-8")
            self.assertNotIn("class ", text, f"{rel} should be a re-export shim without class definitions")
            self.assertNotIn("def ", text, f"{rel} should be a re-export shim without function definitions")


if __name__ == "__main__":
    unittest.main()
