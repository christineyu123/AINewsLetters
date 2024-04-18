from typing import Callable, Union

from news_feed.interface.channel import ChannelElements
from news_feed.interface.feed import Feed as NewsFeedItem, FeedElement
from news_feed.domain.rss import Feed


class RssFeed(Feed):

    def __init__(self, feed_list: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._feed_list = feed_list
        self._parser: Callable = kwargs['feed_parser']
        self._channel_parser: Union[str, callable] = kwargs['channel_parser']
        self._entry_parser: str = kwargs['entry_parser']

    async def get_feed(self, *args, **kwargs):
        if args or kwargs:
            raise ValueError("RssFeed does not accept arguments")
        for feed in self._feed_list:
            publisher = feed['name']
            url = feed['url']
            parsed_feed = self._parser(url)
            if callable(self._channel_parser):
                channel = ChannelElements(**self._channel_parser(parsed_feed))
            else:
                channel = ChannelElements(**getattr(parsed_feed, self._channel_parser))
            proceed = yield publisher, channel.published, channel.published_parsed
            if proceed:
                yield NewsFeedItem(publisher, channel,
                                   [FeedElement(**entry) for entry in getattr(parsed_feed, self._entry_parser)])
        return
