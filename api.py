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
    return "Foo"
    query = TypeMapping.query(TypeMapping.type_id == typeid)
    mapping = query.get()
    if mapping:
        log.debug("Cache hit for typeid %d!", typeid)
        return mapping.name

    # Nothing found, use odylab to translate and store it for future use
    url = "http://odylab-evedb.appspot.com/typeIdToTypeName/%d" % typeid
    res = urlfetch.fetch(url, follow_redirects=False)
    if res.status_code == 200:
        name = res.content
        mapping = TypeMapping(name=name, type_id=typeid)
        mapping.put()

        log.debug("Cached %s from odylab" % mapping)
        print "Cached %s from odylab" % mapping
        return name
    else:
        url = "http://api.eve-central.com/api/quicklook?typeid=%d" % typeid
        res = urlfetch.fetch(url, follow_redirects=False)
        xml = ElementTree.fromstring(res.content)
        name = xml.findtext('.//itemname')
        mapping = TypeMapping(name=name, type_id=typeid)
        mapping.put()

        log.debug("Cached %s from eve-central" % mapping)
        print "Cached %s from eve-central" % mapping
        return name

    log.error("No match found for %d", typeid)
    return "No match found for %d" % typeid


def typeids_to_string(typeids):
    # fetch multiple mappings
    mappings = ndb.get_multi(typeids)
    print mappings
    result = {}

    # build the result cache
    for mapping in mappings:
        result[mapping.typeid] = mapping.name

    for typeid in typeids:
        if result.get(typeid, None):
            print "Cache hit for typeid %d" % typeid
        else:
            result[typeid] =_lookup(typeid)

    return result

def _lookup(typeid):
    # Nothing found, use odylab to translate and store it for future use
    url = "http://odylab-evedb.appspot.com/typeIdToTypeName/%d" % typeid
    res = urlfetch.fetch(url, follow_redirects=False)
    if res.status_code == 200:
        name = res.content
        mapping = TypeMapping(name=name, type_id=typeid)
        mapping.put()

        log.debug("Cached %s from odylab" % mapping)
        print "Cached %s from odylab" % mapping
        return name
    else:
        url = "http://api.eve-central.com/api/quicklook?typeid=%d" % typeid
        res = urlfetch.fetch(url, follow_redirects=False)
        xml = ElementTree.fromstring(res.content)
        name = xml.findtext('.//itemname')
        mapping = TypeMapping(name=name, type_id=typeid)
        mapping.put()

        log.debug("Cached %s from eve-central" % mapping)
        print "Cached %s from eve-central" % mapping
        return name

    log.error("No match found for %d", typeid)
    return "No match found for %d" % typeid
