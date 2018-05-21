import pytest  # type: ignore


@pytest.mark.usefixtures('mock_aiohttp')
class TestBot(object):
    pass


@pytest.mark.usefixtures('mock_aiohttp')
class TestDblBot(object):
    pass
