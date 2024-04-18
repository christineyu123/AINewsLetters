import datetime
import os
import time
from typing import Union

import yaml
from pathlib import Path


def get_absolute_path(to_dir_name: str = None):
    application_dir = os.path.dirname(os.path.abspath(__file__))
    dir_parts = Path(application_dir).parts
    if to_dir_name in dir_parts:
        return Path(*dir_parts[:(dir_parts.index(to_dir_name) + 1)])
    repo_root = Path(*dir_parts[:(dir_parts.index('news_feed') + 1)])
    if to_dir_name:
        return str(repo_root.joinpath(to_dir_name))
    return str(repo_root)


def load_feed_list(config_file_name: str):
    config_dir = get_absolute_path('config')
    with open(f'{config_dir}/{config_file_name}') as f:
        return yaml.safe_load(f)


def filter_date_by_threshold(evaluation_date: Union[datetime.datetime, time.struct_time], threshold: datetime.datetime):
    if evaluation_date is None or threshold is None:
        raise ValueError("date and threshold must not be None")
    if isinstance(evaluation_date, time.struct_time):
        evaluation_date = datetime.datetime(*evaluation_date[:6])
        return evaluation_date >= threshold
    elif isinstance(evaluation_date, datetime.datetime):
        return evaluation_date >= threshold
    else:
        raise ValueError("date must be datetime.datetime or time.struct_time")
