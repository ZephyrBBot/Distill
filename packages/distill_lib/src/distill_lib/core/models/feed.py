from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Feed:
    id: int
    title: str
    url: str


@dataclass
class FeedArticle:
    id: str
    title: str
    url: str
    content: str | None
    pub_date: datetime
    summary: str
    has_full_content: bool


@dataclass
class FeedGroup:
    id: int
    title: str
    desc: str
    feeds: list[Feed] = field(default_factory=list)
