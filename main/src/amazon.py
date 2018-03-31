import requests

from main.models import WorkSource

test_isbn = 9780099469506  # todo temp

BASE_URL = 'http://webservices.amazon.com/onca/xml?'

def search_isbn(isbn: str='9780099469506') -> WorkSource:
    payload = {
        'Service': 'AWSECommerceService',
        'Operation': 'ItemLookup',
        'ResponseGroup': 'Large',
        'SearchIndex': 'All',
        'IdType': 'ISBN',
        'ItemId': isbn,
    }
    return requests.get(BASE_URL, params=payload).text

  # Service=AWSECommerceService
  # &Operation=ItemLookup
  # &ResponseGroup=Large
  # &SearchIndex=All
  # &IdType=ISBN
  # &ItemId=076243631X
  # &AWSAccessKeyId=[Your_AWSAccessKeyID]
  # &AssociateTag=[Your_AssociateTag]
  # &Timestamp=[YYYY-MM-DDThh:mm:ssZ]
  # &Signature=[Request_Signature]