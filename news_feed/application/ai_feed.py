import datetime
import asyncio
from dataclasses import asdict
from operator import itemgetter

import feedparser
import os
from dotenv import load_dotenv
from langchain.document_loaders import WebBaseLoader

from news_feed.application.utils import load_feed_list, filter_date_by_threshold, get_absolute_path
from news_feed.interface.feed import Feed
from news_feed.interface.rss import RssFeed


def filter_articles_by_date(feed_list: list, threshold_date: datetime.datetime):
    latest_articles = []
    for item in feed_list:
        if not isinstance(item, Feed):
            raise ValueError("Unknown type of Feed")
        articles = item.feed
        latest_articles.extend(
            [article for article in articles if filter_date_by_threshold(article.published_parsed, threshold_date)])
    return latest_articles


def get_channel_by_namespace(parsed_content: dict):
    namespace: dict = parsed_content.get('namespaces')
    feed = parsed_content.get('feed')
    title = {'title': feed.get('title')}
    if 'http://www.w3.org/2005/Atom' in list(namespace.values()):
        return {
            **title,
            'description': feed.get('subtitle'),
            'language': feed.get('language'),
            'published': feed.get('updated'),
            'published_parsed': feed.get('updated_parsed')
        }
    else:
        return {
            **title,
            'description': feed.get('description'),
            'language': feed.get('language'),
            'published': feed.get('published'),
            'published_parsed': feed.get('published_parsed')
        }


def get_rss_client(feed_file_name: str):
    feeds = load_feed_list(feed_file_name)
    rss_client = RssFeed(feeds['feeds'], feed_parser=feedparser.parse, channel_parser=get_channel_by_namespace,
                         entry_parser='entries')
    return rss_client


async def fetch_feed(filter_days: int = 1):
    rss_client = get_rss_client('feeds.yaml')
    today = datetime.date.today()
    delta = datetime.timedelta(days=filter_days)
    published_from = datetime.datetime.combine(today - delta, datetime.time.min)
    feed = rss_client.get_feed()
    publisher, _, last_published_at = await feed.__anext__()
    articles = []
    while True:
        try:
            if filter_date_by_threshold(last_published_at, published_from):
                articles.append(await feed.asend(True))
                publisher, _, last_published_at = await feed.asend(None)
            else:
                publisher, _, last_published_at = await feed.asend(False)
        except StopAsyncIteration:
            break
    return filter_articles_by_date(articles, published_from)


def load_page_content(urls: list):
    loader = WebBaseLoader(urls)
    loader.requests_per_second = 10
    return loader.aload()


def main(look_back_days: int = 1):
    num_days_old = int(os.environ.get("NUM_DAYS_OLD", look_back_days))
    articles = asyncio.run(fetch_feed(num_days_old))
    articles = [asdict(article) for article in articles]
    urls = list(map(itemgetter('link'), articles))
    return load_page_content(urls)
