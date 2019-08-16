import pytest  # type: ignore

import app as pagepile_visual_filter


@pytest.fixture
def client():
    pagepile_visual_filter.app.testing = True
    client = pagepile_visual_filter.app.test_client()

    with client:
        yield client
    # request context stays alive until the fixture is closed


def test_csrf_token_generate():
    with pagepile_visual_filter.app.test_request_context():
        token = pagepile_visual_filter.csrf_token()
        assert token != ''


def test_csrf_token_save():
    with pagepile_visual_filter.app.test_request_context() as context:
        token = pagepile_visual_filter.csrf_token()
        assert token == context.session['csrf_token']


def test_csrf_token_load():
    with pagepile_visual_filter.app.test_request_context() as context:
        context.session['csrf_token'] = 'test token'
        assert pagepile_visual_filter.csrf_token() == 'test token'
