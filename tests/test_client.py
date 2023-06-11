import pytest

from libgenmics.client import Client
from libgenmics.client import ComicFile


@pytest.mark.parametrize("size_str", ["27 MB", "Unknown"])
def test_client_comicfile_size(size_str):
    file_ = ComicFile(
        title="foo",
        path="foo",
        author="foo",
        publisher="foo",
        year="foo",
        language="foo",
        pages="foo",
        ext="foo",
        mirrors="foo",
        size=size_str,
        issue="foo",
    )
    assert file_.bytes is not None


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
