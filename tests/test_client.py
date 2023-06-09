import os

import pytest

from libgenmics.client import Client


@pytest.fixture(scope="module")
def client():
    yield Client()


@pytest.mark.vcr
def test_client_search_absolute_watchmen(client: Client):
    result = client.search("absolute watchmen")
    assert result


@pytest.mark.vcr
def test_client_search_watchmen(client: Client):
    result = client.search("watchmen")
    assert result


@pytest.mark.vcr
def test_client_search_nothing(client: Client):
    result = client.search("asdffgggkjdkjlaslkjadslkjsa")
    assert not result
