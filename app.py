# -*- coding: utf-8 -*-

import flask
import mwapi  # type: ignore
import mwoauth  # type: ignore
import os
import random
import requests_oauthlib  # type: ignore
import string
import toolforge
from typing import Optional
import werkzeug
import yaml

from pagepile import load_pagepile, create_pagepile


app = flask.Flask(__name__)

user_agent = toolforge.set_user_agent(
    'pagepile-visual-filter',
    email='mail@lucaswerkmeister.de')

__dir__ = os.path.dirname(__file__)
try:
    with open(os.path.join(__dir__, 'config.yaml')) as config_file:
        app.config.update(yaml.safe_load(config_file))
except FileNotFoundError:
    print('config.yaml file not found, assuming local development setup')
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(64))
    app.secret_key = random_string

if 'oauth' in app.config:
    oauth_config = app.config['oauth']
    consumer_token = mwoauth.ConsumerToken(oauth_config['consumer_key'],
                                           oauth_config['consumer_secret'])
    index_php = 'https://commons.wikimedia.org/w/index.php'


@app.template_global()
def csrf_token() -> str:
    if 'csrf_token' not in flask.session:
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(64))
        flask.session['csrf_token'] = random_string
    return flask.session['csrf_token']


@app.template_global()
def form_value(name: str) -> flask.Markup:
    if 'repeat_form' in flask.g and name in flask.request.form:
        return (flask.Markup(r' value="') +
                flask.Markup.escape(flask.request.form[name]) +
                flask.Markup(r'" '))
    else:
        return flask.Markup()


@app.template_global()
def form_attributes(name: str) -> flask.Markup:
    return (flask.Markup(r' id="') +
            flask.Markup.escape(name) +
            flask.Markup(r'" name="') +
            flask.Markup.escape(name) +
            flask.Markup(r'" ') +
            form_value(name))


@app.template_filter()
def user_link(user_name: str) -> flask.Markup:
    user_href = 'https://commons.wikimedia.org/wiki/User:'
    return (flask.Markup(r'<a href="' + user_href) +
            flask.Markup.escape(user_name.replace(' ', '_')) +
            flask.Markup(r'">') +
            flask.Markup(r'<bdi>') +
            flask.Markup.escape(user_name) +
            flask.Markup(r'</bdi>') +
            flask.Markup(r'</a>'))


@app.template_global()
def authentication_area() -> flask.Markup:
    if 'oauth' not in app.config:
        return flask.Markup()

    if 'oauth_access_token' not in flask.session:
        return (flask.Markup(r'<a id="login" class="navbar-text" href="') +
                flask.Markup.escape(flask.url_for('login')) +
                flask.Markup(r'">Log in</a>'))

    access_token = mwoauth.AccessToken(**flask.session['oauth_access_token'])
    identity = mwoauth.identify(index_php,
                                consumer_token,
                                access_token)

    return (flask.Markup(r'<span class="navbar-text">Logged in as ') +
            user_link(identity['username']) +
            flask.Markup(r'</span>'))


def authenticated_session() -> Optional[mwapi.Session]:
    if 'oauth_access_token' not in flask.session:
        return None

    access_token = mwoauth.AccessToken(
        **flask.session['oauth_access_token'])
    auth = requests_oauthlib.OAuth1(client_key=consumer_token.key,
                                    client_secret=consumer_token.secret,
                                    resource_owner_key=access_token.key,
                                    resource_owner_secret=access_token.secret)
    return mwapi.Session(host='https://commons.wikimedia.org',
                         auth=auth,
                         user_agent=user_agent)


def anonymous_session(domain: str = 'meta.wikimedia.org') -> mwapi.Session:
    return mwapi.Session(host='https://'+domain, user_agent=user_agent)


@app.route('/')
def index() -> str:
    return flask.render_template('index.html')


@app.route('/pagepile/')
def pagepile_redirect():
    id = flask.request.args.get('page_pile_id')
    if not id:
        return flask.redirect(flask.url_for('index'))
    return flask.redirect(flask.url_for('pagepile', id=id))


@app.route('/pagepile/<int:id>/')
def pagepile(id: int):
    pile = load_pagepile(anonymous_session('meta.wikimedia.org'), id)
    if not pile:
        return 'no such pile', 404  # TODO nicer error
    domain, pages = pile
    if domain != 'commons.wikimedia.org':
        return 'refusing to work with domain %s' % domain, 400
    return flask.render_template('pagepile.html',
                                 id=id,
                                 domain=domain,
                                 pages=pages)


@app.route('/pagepile/<int:id>/filter', methods=['POST'])
def filter_pagepile(id: int):
    if not submitted_request_valid():
        return 'CSRF error', 400  # TODO nicer error
    session = anonymous_session('meta.wikimedia.org')
    domain, original_pages = load_pagepile(session, id)
    new_pages = flask.request.form.getlist('file')
    if not new_pages or len(new_pages) >= len(original_pages):
        return 'no changes', 200  # TODO better response
    new_id = create_pagepile(session, domain, new_pages)
    url = 'https://tools.wmflabs.org/pagepile/api.php' \
        '?action=get_data&id=%d&format=html' % new_id
    return flask.redirect(url)


@app.route('/login')
def login() -> werkzeug.Response:
    redirect, request_token = mwoauth.initiate(index_php,
                                               consumer_token,
                                               user_agent=user_agent)
    flask.session['oauth_request_token'] = dict(zip(request_token._fields,
                                                    request_token))
    return flask.redirect(redirect)


@app.route('/oauth/callback')
def oauth_callback() -> werkzeug.Response:
    request_token = mwoauth.RequestToken(
        **flask.session.pop('oauth_request_token'))
    access_token = mwoauth.complete(index_php,
                                    consumer_token,
                                    request_token,
                                    flask.request.query_string,
                                    user_agent=user_agent)
    flask.session['oauth_access_token'] = dict(zip(access_token._fields,
                                                   access_token))
    return flask.redirect(flask.url_for('index'))


def full_url(endpoint: str, **kwargs) -> str:
    scheme = flask.request.headers.get('X-Forwarded-Proto', 'http')
    return flask.url_for(endpoint, _external=True, _scheme=scheme, **kwargs)


def submitted_request_valid() -> bool:
    """Check whether a submitted POST request is valid.

    If this method returns False, the request might have been issued
    by an attacker as part of a Cross-Site Request Forgery attack;
    callers MUST NOT process the request in that case.
    """
    real_token = flask.session.pop('csrf_token', None)
    submitted_token = flask.request.form.get('csrf_token', None)
    if not real_token:
        # we never expected a POST
        return False
    if not submitted_token:
        # token got lost or attacker did not supply it
        return False
    if submitted_token != real_token:
        # incorrect token (could be outdated or incorrectly forged)
        return False
    if not (flask.request.referrer or '').startswith(full_url('index')):
        # correct token but not coming from the correct page; for
        # example, JS running on https://tools.wmflabs.org/tool-a is
        # allowed to access https://tools.wmflabs.org/tool-b and
        # extract CSRF tokens from it (since both of these pages are
        # hosted on the https://tools.wmflabs.org domain), so checking
        # the Referer header is our only protection against attackers
        # from other Toolforge tools
        return False
    return True


@app.after_request
def deny_frame(response: flask.Response) -> flask.Response:
    """Disallow embedding the tool’s pages in other websites.

    If other websites can embed this tool’s pages, e. g. in <iframe>s,
    other tools hosted on tools.wmflabs.org can send arbitrary web
    requests from this tool’s context, bypassing the referrer-based
    CSRF protection.
    """
    response.headers['X-Frame-Options'] = 'deny'
    return response
