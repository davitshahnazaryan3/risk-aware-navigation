from pathlib import Path
import json
import requests
from typing import Tuple
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def read_map(path: Path, filename: str) -> dict:
    """Reads map in json format

    Structure of "cells"
    cells - id: int                 ID of cell, left to right, top to bottom sequence from 0 to cell_qnt - 1
            connections: List[int]  Possible outgoing paths

    Parameters
    ----------
    path : Path
        Path of folder containig *.json files of maps
    filename : str
        Filename of map in *.json

    Returns
    -------
    dict
    """    
    if filename.endswith("_tested.png"):
        filename.replace("_tested.png", "")
    filepath = filename + ".json"
    return json.load(open(path / filepath))


def requests_retry_session(
    retries: int = 3, 
    backoff_factor: float = 0.3, 
    status_forcelist: Tuple[int] = (500, 502, 504), 
    session: requests.Session = None,
):
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
