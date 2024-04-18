import pytest

from application.ai_feed import get_rss_client, fetch_feed, main


def test_get_rss_client():
    client = get_rss_client('feeds.yaml')
    assert len(client._feed_list) > 0


@pytest.mark.asyncio
async def test_fetch_feed():
    articles = await fetch_feed()
    assert len(articles) > 0


def test_main():
    articles = main()
    assert len(articles) > 0
    assert all(article.metadata is not None for article in articles)
    assert all(article.page_content is not None for article in articles)
