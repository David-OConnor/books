import requests
import rdflib

# Gutenberg forbids using automated tools to parse their site directly, but provides
# feeds and catalogs.

# ie Don't use this:
# 'http://www.gutenberg.org/ebooks/search/?query='

# Use this instead:
# http://www.gutenberg.org/wiki/Gutenberg:Feeds
