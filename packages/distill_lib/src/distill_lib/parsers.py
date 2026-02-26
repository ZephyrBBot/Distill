"""Compatibility wrapper for parser helpers in distill_lib.core."""

from distill_lib.core import parsers as _core_parsers
from distill_lib.core.parsers import parse_feed, parse_html_content, parse_opml

# Backward-compat for tests/patches that target distill_lib.parsers.feedparser
feedparser = _core_parsers.feedparser

__all__ = ["parse_opml", "parse_feed", "parse_html_content", "feedparser"]
