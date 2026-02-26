"""Content storage adapter for PS-agent feed content fetching."""

from core.db.pool import get_async_connection


async def fetch_feed_contents(ids: list[str]) -> dict[str, str]:
    if not ids:
        return {}

    async with get_async_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT feed_item_id, content FROM feed_item_contents WHERE feed_item_id = ANY(%s)",
                (ids,),
            )
            rows = await cur.fetchall()
            return {row[0]: row[1] for row in rows}


__all__ = ["fetch_feed_contents"]
