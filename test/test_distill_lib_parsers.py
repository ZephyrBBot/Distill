import time
import unittest
from unittest.mock import patch

from distill_lib.feed_models import Feed
from distill_lib.parsers import parse_feed, parse_opml


class DistillLibParsersTest(unittest.TestCase):
    def test_parse_opml_returns_distill_feed_models(self):
        opml = """
        <opml version="1.0">
          <body>
            <outline type="rss" title="Example" xmlUrl="https://example.com/rss.xml" />
          </body>
        </opml>
        """

        feeds = parse_opml(opml)

        self.assertEqual(len(feeds), 1)
        self.assertEqual(feeds[0].title, "Example")
        self.assertIsInstance(feeds[0], Feed)

    def test_parse_feed_parses_entries(self):
        struct = time.gmtime()

        class _Entry:
            id = "a1"
            title = "Article"
            link = "https://example.com/article"
            summary = "<article><p>Hello world</p></article>"
            published_parsed = struct

        class _Data:
            entries = [_Entry()]

        with patch("distill_lib.parsers.feedparser.parse", return_value=_Data()):
            result = parse_feed([Feed(id=1, title="T", url="https://example.com/rss")])

        self.assertIn("T", result)
        self.assertEqual(len(result["T"]), 1)
        self.assertEqual(result["T"][0].id, "a1")
        self.assertEqual(result["T"][0].summary, "Hello world")


if __name__ == "__main__":
    unittest.main()
