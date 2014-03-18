# ndb mappings

from google.appengine.ext import ndb

class TypeMapping(ndb.Model):
    # Always searched by type_id, so no point in indexing other values
    name = ndb.StringProperty(indexed=False)
    type_id = ndb.IntegerProperty(indexed=True)

