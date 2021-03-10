# -*- coding: utf-8 -*-

import flask
import mwapi  # type: ignore
import os
import random
import string
import toolforge
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
def pagepile_url(id: int) -> str:
    return 'https://pagepile.toolforge.org/api.php' \
        '?action=get_data&id=%d&format=html' % id


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
        return flask.render_template('no-such-pagepile.html',
                                     id=id), 404
    domain, pages = pile
    if domain != 'commons.wikimedia.org':
        return flask.render_template('not-commons-pagepile.html',
                                     id=id,
                                     domain=domain), 400
    return flask.render_template('pagepile.html',
                                 id=id,
                                 domain=domain,
                                 pages=pages)


@app.route('/pagepile/<int:id>/filter', methods=['POST'])
def filter_pagepile(id: int):
    if not submitted_request_valid():
        return 'CSRF error', 400  # TODO nicer error
    session = anonymous_session('meta.wikimedia.org')
    original_pile = load_pagepile(session, id)
    if not original_pile:
        return flask.render_template('no-such-pagepile.html',
                                     id=id), 404
    domain, original_pages = original_pile
    new_pages = flask.request.form.getlist('file')
    if not new_pages or len(new_pages) >= len(original_pages):
        return 'no changes', 200  # TODO better response
    new_id = create_pagepile(session, domain, new_pages)
    return flask.redirect(pagepile_url(new_id))


def full_url(endpoint: str, **kwargs) -> str:
    scheme = flask.request.headers.get('X-Forwarded-Proto', 'http')
    return flask.url_for(endpoint, _external=True, _scheme=scheme, **kwargs)


def submitted_request_valid() -> bool:
    """Check whether a submitted POST request is valid.

    If this method returns False, the request might have been issued
    by an attacker as part of a Cross-Site Request Forgery attack;
    callers MUST NOT process the request in that case.
    """
    real_token = flask.session.get('csrf_token')
    submitted_token = flask.request.form.get('csrf_token')
    if not real_token:
        # we never expected a POST
        return False
    if not submitted_token:
        # token got lost or attacker did not supply it
        return False
    if submitted_token != real_token:
        # incorrect token (could be outdated or incorrectly forged)
        return False
    return True


@app.after_request
def deny_frame(response: flask.Response) -> flask.Response:
    """Disallow embedding the tool’s pages in other websites.

    This mainly protects against clickjacking attacks,
    since it’s very useful to embed this tool anyways.
    """
    response.headers['X-Frame-Options'] = 'deny'
    return response
