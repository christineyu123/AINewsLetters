from abc import ABC, abstractmethod


class Feed(ABC):
    def __init__(self, *args, **kwargs):
        [setattr(self, f'{arg}', arg) for arg in args]
        for key, value in kwargs.items():
            setattr(self, f'{key}', value)

    @abstractmethod
    def get_feed(self, *args, **kwargs):
        """
        Abstract method that must be implemented by all sub classes
        The reason this is not implemented is that it is possible for feeds to require authentication
        and/or obey rate limits. These factors should be handled by the sub classes
        :param args: At minimum should include the feed url
        :param kwargs: May be used to pass in authentication credentials
        :return:
        Value should depend on the sub class. For example, a sub class may return a list of dictionaries
        This should return the parsed feed optionally wrapped in a data structure
        """
        raise NotImplementedError(
            "domain method is not implemented and its intent is to define a contract for sub classes")
