from agent.ps_agent.adapters import fetch_feed_contents
from agent.ps_agent.state import ResearchItem
from distill_lib.agent.tools import fetch_web_contents


async def fetch_contents(
    items: list[ResearchItem],
) -> tuple[dict[str, str], dict[str, str]]:
    urls = [item.get("url", "") for item in items if item.get("source") == "web"]
    web_contents = await fetch_web_contents(urls)
    ids = [item.get("id", "") for item in items if item.get("source") == "feed"]
    feed_contents = await fetch_feed_contents(ids)
    return web_contents, feed_contents
