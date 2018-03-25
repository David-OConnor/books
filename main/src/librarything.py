import requests

from ..models import Work, Author
from .auth import LIBRARYTHING_KEY as KEY

# API ref: https://www.librarything.com/services/


BASE_URL = 'http://www.librarything.com/services/rest/1.1/'
