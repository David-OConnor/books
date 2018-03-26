from typing import List

import requests

from ..models import Work, Author
from .auth import LIBRARYTHING_KEY as KEY

# API ref: https://www.librarything.com/services/


BASE_URL = 'http://www.librarything.com/services/rest/1.1/'


def query_work(title: str) -> dict:
    params = {
        # 'method_name': 'librarything.ck.getwork',
        'apikey': KEY,
        'name': title
    }
    r = requests.get(BASE_URL + '?method=librarything.ck.getwork', params=params)
    return r
    return r.json()