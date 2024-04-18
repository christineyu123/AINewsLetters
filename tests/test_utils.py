import os

from application import utils


def test_get_absolute_path():
    content_root = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/news_feed'
    assert utils.get_absolute_path() == content_root
    assert utils.get_absolute_path('config') == f'{content_root}/config'
