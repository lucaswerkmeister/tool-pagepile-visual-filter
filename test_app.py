import pytest

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


def test_load_files():
    session = pagepile_visual_filter.anonymous_session('commons.wikimedia.org')
    titles = [
        'Leonardo da Vinci',  # not a file
        'File:Button small 2.png',  # tiny file
        'File:Crystal Project Password.png',  # small file
        'File:Mona Lisa, by Leonardo da Vinci, from C2RMF retouched.jpg',  # large file
    ]
    files = pagepile_visual_filter.load_files(session, titles)
    assert files == {
        'Leonardo da Vinci': None,
        'File:Button small 2.png': {
            'thumburl': 'https://upload.wikimedia.org/wikipedia/commons/1/17/Button_small_2.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled',
            'thumbwidth': 250,
            'thumbheight': 239,
            'thumbattribs': {
                'src': 'https://upload.wikimedia.org/wikipedia/commons/1/17/Button_small_2.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled',
                'decoding': 'async',
                'loading': 'lazy',
                'width': 250,
                'height': 239,
            },
            'url': 'https://upload.wikimedia.org/wikipedia/commons/1/17/Button_small_2.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Button_small_2.png',
            'descriptionshorturl': 'https://commons.wikimedia.org/w/index.php?curid=1278021'
        },
        'File:Crystal Project Password.png': {
            'thumburl': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/1/13/Crystal_Project_Password.png/250px-Crystal_Project_Password.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
            'thumbwidth': 250,
            'thumbheight': 250,
            'responsiveUrls': {
                '2': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Crystal_Project_Password.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled'
            },
            'thumbattribs': {
                'src': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/1/13/Crystal_Project_Password.png/250px-Crystal_Project_Password.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
                'decoding': 'async',
                'loading': 'lazy',
                'width': 250,
                'height': 250,
                'srcset': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Crystal_Project_Password.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail_unscaled 2x',
            },
            'url': 'https://upload.wikimedia.org/wikipedia/commons/1/13/Crystal_Project_Password.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Crystal_Project_Password.png',
            'descriptionshorturl': 'https://commons.wikimedia.org/w/index.php?curid=18332648'
        },
        'File:Mona Lisa, by Leonardo da Vinci, from C2RMF retouched.jpg': {
            'thumburl': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/250px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
            'thumbwidth': 168,
            'thumbheight': 250,
            'responsiveUrls': {
                '2': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/500px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail'
            },
            'thumbattribs': {
                'src': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/250px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
                'decoding': 'async',
                'loading': 'lazy',
                'width': 168,
                'height': 250,
                'srcset': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/500px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail 2x',
            },
            'url': 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=original',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg',
            'descriptionshorturl': 'https://commons.wikimedia.org/w/index.php?curid=15442524'
        },
    }
