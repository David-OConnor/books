import xml.etree.ElementTree as ET
from typing import Optional, Iterator

import requests

# Documentation: https://www.goodreads.com/api
from ..models import Isbn, Source, WorkSource, Work
from .auth import GOODREADS_KEY as KEY


# API ref: https://www.goodreads.com/api

BASE_URL = 'https://goodreads.com/'

source, _ = Source.objects.get_or_create(
        name='GoodReads',
        defaults={
            'url': 'https://www.goodreads.com/',
            'information': True,
            'free_downloads': True
        }
)


def search(work: Work) -> Optional[int]:
    """Find the unique goodreads ids associated with a work's isbns."""
    # for isbn in Isbn.objects.filter(work=work):
    # todo deal with different editions!
    # todo just title search for now
    payload = {
        # 'q': str(isbn.isbn),
        'q': f'{work.title}',
        'key': KEY,
        # 'search': 'isbn'  # title, author or all. I guess all for isbn??
        'search': 'title'  # title, author or all. I guess all for isbn??
    }

    r = requests.get(BASE_URL + 'search/index.xml', params=payload)

    root = ET.fromstring(r.text)
    works = root.find('search').find('results').findall('work')
    for gr_work in works:
        book = gr_work.find('best_book')
        if book.find('author').find('name').text.lower() == work.author.full_name().lower():
            return int(book.find('id').text)



def url_from_id(internal_id: int) -> str:
    """Find the goodreads URL associated with a book from its id."""
    return f"https://www.goodreads.com/book/show/{internal_id}"


def search_title(title: str) -> WorkSource:
    # todo you could merge this with search_isbn, since they both
    # todo use the same API endpoint.
    pass


#Example query result from searching by isbn:
"""
<?xml version="1.0" encoding="UTF-8"?>
<GoodreadsResponse>
  <Request>
    <authentication>true</authentication>
      <key><![CDATA[uexbJbIA196PF5j5S7ZprQ]]></key>
    <method><![CDATA[search_index]]></method>
  </Request>
  
  <search>
    <query><![CDATA[9780099469506]]></query>
    <results-start>1</results-start>
    <results-end>1</results-end>
    <total-results>1</total-results>
    <source>Goodreads</source>
    <query-time-seconds>0.01</query-time-seconds>
    
    <results>
        <work>
          <id type="integer">2416056</id>
          <books_count type="integer">92</books_count>
          <ratings_count type="integer">101528</ratings_count>
          <text_reviews_count type="integer">2311</text_reviews_count>
          <original_publication_year type="integer">1985</original_publication_year>
          <original_publication_month type="integer">9</original_publication_month>
          <original_publication_day type="integer" nil="true"/>
          <average_rating>4.12</average_rating>
          <best_book type="Book">
            <id type="integer">611439</id>
            <title>Contact</title>
            <author>
              <id type="integer">10538</id>
              <name>Carl Sagan</name>
            </author>
            <image_url>https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png</image_url>
            <small_image_url>https://s.gr-assets.com/assets/nophoto/book/50x75-a91bf249278a81aabab721ef782c4a74.png</small_image_url>
          </best_book>
        </work>

    </results>
  </search>

</GoodreadsResponse>
"""