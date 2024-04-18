from interface.rss import RssFeed


def test_initialization():
    rss = RssFeed([{'name': 'name', 'url': 'url'}], 'arg1', 'arg2', feed_parser=lambda x: x, channel_parser='kwarg2',
                  entry_parser='kwarg3')
    assert rss.arg1 == 'arg1'
    assert rss.arg2 == 'arg2'
    assert callable(rss.feed_parser)
    assert rss.channel_parser == 'kwarg2'
    assert rss.entry_parser == 'kwarg3'
