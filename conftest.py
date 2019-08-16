import mwapi # type: ignore
import pytest # type: ignore


@pytest.fixture
def internet_connection():
    """No-value fixture to skip tests if no internet connection is available."""
    try:
        yield
    except mwapi.errors.ConnectionError:
        pytest.skip('no internet connection')
