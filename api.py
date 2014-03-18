# external APIs

import logging as log
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(30)  # default: 5, maximum: 60

from mapping import *
from xml.etree import ElementTree

# TODO: Write own cache module for evelink!!
# https://github.com/ayust/evelink/blob/master/evelink/cache/sqlite.py
# should be pretty straightforward

def typeid_to_string(typeid):
    # Check the cache for typeid mapping
    query = TypeMapping.query(TypeMapping.type_id == typeid)
    mapping = query.get()
    if mapping:
        print "Cache hit"
        log.debug("Cache hit for typeid %d!", typeid)
        return mapping.name
    else:
        print "Cache miss"
        return _lookup(typeid)


def typeids_to_string(typeids):
    # fetch multiple mappings
    result = {}
    qo = ndb.QueryOptions()
    query = TypeMapping.query(TypeMapping.type_id.IN(typeids))
    for mapping in query.fetch(options=qo):
        result[mapping.type_id] = mapping.name

    for typeid in typeids:
        # check if the requested keys have values defined
        if result.get(typeid, None):
            print "Cache hit for typeid %d" % typeid
        else:
            log.debug("Cache miss for %d", typeid)
            result[typeid] =_lookup(typeid)

    return result

def _lookup(typeid):
    url = "http://api.eve-central.com/api/quicklook?typeid=%d" % typeid
    res = urlfetch.fetch(url, follow_redirects=False)
    xml = ElementTree.fromstring(res.content)
    name = xml.findtext('.//itemname')
    if name:
        mapping = TypeMapping(name=name, type_id=typeid)
        mapping.put()

        log.debug("Cached %s from eve-central" % mapping)
        print "Cached %s from eve-central" % mapping
        return name
    else:
        log.error("No match found for %d", typeid)
        return "No match found for %d" % typeid
