"""`main` is the top level module for your Flask application."""

# Import the Flask Framework
from flask import Flask
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
import jinja2
import os.path
import logging as log

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

import evelink
from evelink import appengine
from mapping import *
from objects import *
from api import *
from util import *

# Jinja filter assignment
JINJA_ENVIRONMENT.filters['to_roman'] = to_roman

@app.route('/account/<key>/<verification>')
def account(key=None, verification=None):
    api = appengine.AppEngineAPI(api_key=(key, verification))

    a = evelink.account.Account(api)

    characters = []
    for char_id in a.characters().result:
        log.debug("Creating character %d", char_id)
        character = CharacterFactory.create_character(api, char_id)
        characters.append(character)

    template = JINJA_ENVIRONMENT.get_template('character_summary.html')
    return template.render({'characters': characters, 'key':key, 'verification':verification})


@app.route('/character/<key>/<verification>/<char_id>')
def character(key=None, verification=None, char_id=None):
    """Return a friendly HTTP greeting."""
    api = appengine.AppEngineAPI(api_key=(key, verification))

    a = evelink.account.Account(api)

    template = JINJA_ENVIRONMENT.get_template('character.html')

    character = CharacterFactory.create_character(api, char_id)
    return template.render({'character': character})


@app.route('/delete')
def delete():
    return "Disabled"

    from google.appengine.ext import ndb
    from mapping import TypeMapping
    keys = TypeMapping.query().fetch(keys_only=True)
    for key in keys:
        print key.delete()

    return "Delete done"


@app.route('/')
def index():
    """Return a friendly HTTP greeting."""

    template = JINJA_ENVIRONMENT.get_template('index.html')
    return template.render()


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
