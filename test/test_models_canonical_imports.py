from pathlib import Path
import unittest

from distill_lib.core.models.config import GlobalConfig as CanonicalGlobalConfig
from distill_lib.core.models.feed import Feed as CanonicalFeed
from distill_lib.core.models.feed import FeedArticle as CanonicalFeedArticle
from distill_lib.core.models.feed import FeedBrief as CanonicalFeedBrief
from distill_lib.core.models.feed import FeedGroup as CanonicalFeedGroup
from distill_lib.core.models.llm import Message as CanonicalMessage
from distill_lib.core.models.llm import ModelProvider as CanonicalModelProvider
from distill_lib.core.models.search import SearchResult as CanonicalSearchResult

from core.models.config import GlobalConfig
from core.models.feed import Feed, FeedArticle, FeedBrief, FeedGroup
from core.models.llm import Message, ModelProvider
from core.models.search import SearchResult


class CanonicalModelsImportTest(unittest.TestCase):
    def test_core_models_are_aliases_of_distill_lib_models(self):
        self.assertIs(Feed, CanonicalFeed)
        self.assertIs(FeedArticle, CanonicalFeedArticle)
        self.assertIs(FeedBrief, CanonicalFeedBrief)
        self.assertIs(FeedGroup, CanonicalFeedGroup)
        self.assertIs(Message, CanonicalMessage)
        self.assertIs(ModelProvider, CanonicalModelProvider)
        self.assertIs(SearchResult, CanonicalSearchResult)
        self.assertIs(GlobalConfig, CanonicalGlobalConfig)

    def test_root_model_modules_are_thin_shims(self):
        project_root = Path(__file__).resolve().parent.parent
        for rel in (
            "core/models/config.py",
            "core/models/feed.py",
            "core/models/llm.py",
            "core/models/search.py",
        ):
            text = (project_root / rel).read_text(encoding="utf-8")
            self.assertNotIn("class ", text, f"{rel} should be a re-export shim without class definitions")


if __name__ == "__main__":
    unittest.main()
