import timeit
import numpy as np
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_init_time():
    """
    Records initial time
    :return: float                      Initial time
    """
    start_time = timeit.default_timer()
    return start_time


def truncate(n, decimals=0):
    """
    Truncates time with given decimal points
    :param n: float                     Time
    :param decimals: int                Decimal points
    :return: float                      Truncated time
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def get_time(start_time):
    """
    Prints running time in seconds and minutes
    :param start_time: float            Initial time
    :return: None
    """
    elapsed = timeit.default_timer() - start_time
    print('Running time: ', truncate(elapsed, 1), ' seconds')
    print('Running time: ', truncate(elapsed / float(60), 2), ' minutes')


def read_text(filename):
    return np.genfromtxt(filename, invalid_raise=False)


def read_map(path, filename):
    """
    Structure of "cells"
    cells - id: int                 ID of cell, left to right, top to bottom sequence from 0 to cell_qnt - 1
            connections: List[int]  Possible outgoing paths
    :param path: Path
    :param filename: str            Map name
    :return: json
    """
    if filename.endswith("_tested.png"):
        filename.replace("_tested.png", "")
    filepath = filename + ".json"
    return json.load(open(path / filepath))


def export_json(data, filename="risks.json"):
    with open(filename, "w") as f:
        json.dump(data, f)


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
