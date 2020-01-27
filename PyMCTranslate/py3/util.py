from typing import Generator
import os
import json
import gzip


def directories(path: str) -> Generator[str, None, None]:
    """
    A generator of only directories in the given directory.
    :param path: str: the path to an existing directory on the current system
    """
    for dir_name in os.listdir(path):
        if os.path.isdir(os.path.join(path, dir_name)):
            yield dir_name


def files(path: str) -> Generator[str, None, None]:
    """
    A generator of only files in the given directory.
    :param path: str: the path to an existing directory on the current system
    """
    for file_name in os.listdir(path):
        if os.path.isfile(os.path.join(path, file_name)):
            yield file_name


def load_json_gz(file_path: str):
    with gzip.open(file_path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'))
