import pytest

from libgenmics import comicvine


@pytest.fixture
def client():
    yield comicvine.Client("foo")


@pytest.mark.parametrize(
    "id",
    [
        "4000-136972",
        "https://comicvine.gamespot.com/daredevil-379-flying-blind-part-4/4000-136972/",
        "4000-979622",
        "44193",
    ],
)
@pytest.mark.vcr
def test_comicvine_client_issue(client: comicvine.Client, id):
    result = client.issue(id)
    assert result.to_comic_info_xml_params()


@pytest.mark.vcr
def test_comicvine_client_volume(client: comicvine.Client):
    assert client.volume("4050-146171")
