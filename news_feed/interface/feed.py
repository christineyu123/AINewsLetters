import datetime
from dataclasses import dataclass
from typing import List

from news_feed.interface.channel import ChannelElements


@dataclass(init=False)
class FeedElement:
    title: str
    link: str
    description: str
    language: str
    published: str
    published_parsed: datetime.datetime

    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.link = kwargs.get('link')
        self.description = kwargs.get('description')
        self.language = kwargs.get('language')
        self.published = kwargs.get('published')
        self.published_parsed = kwargs.get('published_parsed')


@dataclass
class Feed:
    publisher: str
    channel: ChannelElements
    feed: List[FeedElement]
