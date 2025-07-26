import mwapi  # type: ignore
import pytest


@pytest.fixture
def internet_connection():
    """Fixture to skip tests if no internet connection is available."""
    try:
        yield
    except mwapi.errors.ConnectionError:
        pytest.skip('no internet connection')
