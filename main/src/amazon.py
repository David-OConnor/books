import requests

from main.models import WorkSource

# Documentation:
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/ProgrammingGuide.html

BASE_URL = 'http://webservices.amazon.com/onca/xml?'


def search_title_author(title: str, author: str):
    payload = {
        'Service': 'AWSECommerceService',
        'Operation': 'ItemLookup',
        'ResponseGroup': 'Large',
        'SearchIndex': 'All',
        'IdType': 'ISBN',
        'ItemId': isbn,
    }
    return requests.get(BASE_URL, params=payload).text




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