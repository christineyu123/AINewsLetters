import pytest

from domain.rss import Feed


@pytest.mark.xfail(raises=TypeError)
def test_initialization_no_args():
    Feed()


@pytest.mark.xfail(raises=TypeError)
def test_initialization_with_args():
    Feed('arg1', 'arg2')
