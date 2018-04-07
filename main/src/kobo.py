from typing import Optional, Tuple

import requests
from requests_html import HTMLSession

from .auth import KOBO_ID as KEY
from ..models import Work


# API documentation:
# Unofficial. Possibly janky. Returns top 30 results
# https://rakuten-api-documentation.antoniotajuelo.com/rakuten/endpoint/view?rakuten_endpoint_id=31

def scrape(work: Work) -> Optional[Tuple[str, str]]:
    """Return the URL for Kobo's entry."""
    payload = {
        'Query': f"{work.title} {work.author.full_name()}"
    }

    session = HTMLSession()
    r = session.get('https://www.kobo.com/us/en/search', params=payload)

    # todo Parse multiple entries; set up your system in general to show multiple
    # todo vesions; Kobo often has this.
    best_match = r.html.find('.product-field', first=True)

    if not best_match:
        return  # No results
    url = next(iter(best_match.links))

    r_page = session.get(url)
    price_div = r_page.html.find('.active-price', first=True)
    price = price_div.find('.price', first=True).text

    return url, price

def search(work: Work) -> Optional[int]:
    url = 'https://app.rakuten.co.jp/services/api/Kobo/EbookSearch/20140811'

    payload = {
        'applicationId': KEY,
        'title': work.title,
        'author': work.author.last_name,
        'formatVersion': '2'  # format version 2 has reduced nesting compared to the default.
    }

    r = requests.get(url, params=payload)

    data = r.json()
    items = data['Items']
    if not items:
        return

    # todo for now just pick the top entry.
    best = items[0]
    return int(best['itemNumber'])
