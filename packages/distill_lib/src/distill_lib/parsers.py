from __future__ import annotations

import datetime
import time
import xml.etree.ElementTree as ET
from collections import defaultdict

import feedparser
from bs4 import BeautifulSoup

from distill_lib.feed_models import Feed, FeedArticle

SUMMARY_LENGTH = 500

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/128.0",
    "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


def parse_opml(file_text: str) -> list[Feed]:
    root = ET.fromstring(file_text)
    feeds = []

    for outline in root.findall(".//outline[@type='rss']"):
        feed = Feed(
            id=0,
            title=outline.get("title"),
            url=outline.get("xmlUrl"),
        )
        feeds.append(feed)

    return feeds


def parse_feed(feeds: list[Feed]) -> dict[str, list[FeedArticle]]:
    articles = defaultdict(list)
    for feed in feeds:
        data = feedparser.parse(feed.url, request_headers=HEADERS)
        if not data.entries:
            continue
        for entry in data.entries:
            published_struct = getattr(entry, "published_parsed", None) or getattr(
                entry, "updated_parsed", None
            )
            if not published_struct:
                continue
            pub_date = _convert_to_datetime(published_struct)
            guid = entry.id if hasattr(entry, "id") else entry.link
            content, has_full_content = _extract_text_from_entry(entry)
            summary = content[:SUMMARY_LENGTH] if content else ""
            articles[feed.title].append(
                FeedArticle(
                    id=guid,
                    title=entry.title[:256],
                    url=entry.link,
                    content=content,
                    pub_date=pub_date,
                    summary=summary,
                    has_full_content=has_full_content,
                )
            )
    return articles


def parse_html_content(html_content: str) -> str:
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "lxml")

    potential_containers = [
        soup.find("article"),
        soup.find("main"),
        soup.find(id="main-content"),
        soup.find(id="content"),
        soup.find(class_="post-content"),
        soup.find(class_="entry-content"),
        soup.find(class_="article-body"),
    ]

    content_container = next((container for container in potential_containers if container), None)

    if not content_container:
        content_container = soup.body
        if not content_container:
            return ""

    selectors_to_remove = [
        "nav",
        "header",
        "footer",
        "aside",
        "script",
        "style",
        "noscript",
        '[role="navigation"]',
        '[role="banner"]',
        '[role="contentinfo"]',
        '[id*="comments"]',
        '[class*="comments"]',
        '[id*="sidebar"]',
        '[class*="sidebar"]',
        '[id*="footer"]',
        '[class*="footer"]',
        '[id*="header"]',
        '[class*="header"]',
        '[id*="nav"]',
        '[class*="nav"]',
        '[class*="advert"]',
        '[class*="banner"]',
        '[class*="share"]',
        '[class*="social"]',
        '[class*="related"]',
        '[class*="author-info"]',
    ]

    for selector in selectors_to_remove:
        for element in content_container.select(selector):
            element.decompose()

    main_text = content_container.get_text(separator="\n", strip=True)
    lines = [line for line in main_text.split("\n") if line.strip()]
    return "\n".join(lines)


def _extract_text_from_entry(entry) -> tuple[str, bool]:
    full_content = ""
    if hasattr(entry, "content") and entry.content and isinstance(entry.content, list):
        if entry.content[0].value:
            full_content = parse_html_content(entry.content[0].value)
            return full_content, True

    if hasattr(entry, "summary"):
        full_content = parse_html_content(entry.summary[:SUMMARY_LENGTH])
        return full_content, False

    return "", False


def _convert_to_datetime(ttime: time.struct_time) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(time.mktime(ttime))
