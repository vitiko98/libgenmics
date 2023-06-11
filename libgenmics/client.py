import logging
from typing import List

from bs4 import BeautifulSoup as bso
from pydantic import BaseModel
from pydantic import ValidationError
import requests

logger = logging.getLogger(__name__)


_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://libgen.gs",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="111", "Not(A:Brand";v="8"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
}


class ComicFile(BaseModel):
    badges: List[str] = []
    title: str
    path: str
    author: str
    publisher: str
    year: str
    language: str
    pages: str
    ext: str
    mirrors: str
    size: str
    issue: str

    @property
    def bytes(self):
        try:
            value, mb = [i.strip() for i in self.size.split()]
        except ValueError:
            return 0

        if mb != "MB":
            return 0

        try:
            return int(float(value) * 1024 * 1024)
        except ValueError:
            return 0


class Client:
    def __init__(
        self, base_url="https://libgen.gs", cookies=None, session=None, headers=None
    ):
        self._base_url = base_url
        self._session = session or requests.Session()
        self._session.cookies.update(cookies or {})
        self._session.headers.update(headers or _HEADERS)

    def search(
        self, req: str, page=1, res=100, languages=("English",)
    ) -> List[ComicFile]:
        params = {
            "req": req,
            "columns[]": [
                "t",
                "a",
                "s",
                "y",
                "p",
                "i",
            ],
            "objects[]": [
                "f",
                "e",
                "s",
                "a",
                "p",
                "w",
            ],
            "topics[]": [
                "c",
            ],
            "res": res,
            "showch": "on",
            "filesuns": "all",
            "page": page,
        }

        response = self._session.get(f"{self._base_url}/index.php", params=params)
        response.raise_for_status()

        parsed = _parse_results(response.content, languages)
        return parsed

    def download_file(self, url, output):
        response = self._session.get(url, stream=True, allow_redirects=True)
        file_size = int(response.headers.get("Content-Length", 0))
        logger.debug("File size of %s: %d", url, file_size)

        response.raise_for_status()
        with open(output, "wb") as file:
            file.write(response.content)


_COLUMNS = (
    "first",
    "author",
    "publisher",
    "year",
    "language",
    "pages",
    "size",
    "ext",
    "mirrors",
)


def _parse_results(content, languages):
    soup = bso(content, "html.parser")
    trs = soup.select("#tablelibgen > tbody > tr")
    head = soup.select("#tablelibgen > thead > tr")
    try:
        headers = [h.text.replace("\n", "").replace("\r", "") for h in head][0]
    except IndexError:
        logger.info("Headers not found in page. Returning nothing.")
        return []

    headers = [h.strip() for h in headers.split("↕")]

    files = []

    for tr_ in trs:
        try:
            comic_file = _parse_comic_file(tr_)
        except (ValidationError, AttributeError) as error:
            logger.error(f"Error parsing comic file: {error}")
            continue

        if not comic_file:
            continue

        if comic_file.language not in languages:
            continue

        files.append(comic_file)

    return files


def _parse_comic_file(tr_):
    item = dict()
    for n, td, key in zip(range(0, 9), tr_.select("td"), _COLUMNS):
        if n == 0:
            item.update(_parse_first_td(td))
        elif n == 8:
            item[key] = td.select_one("a").get("href")
        else:
            item[key] = td.text.strip()

    if len(item) < 9:
        return None

    return ComicFile(**item)


def _parse_first_td(td):
    item = dict()
    item["badges"] = [i.text for i in td.select("span")]
    item["issue"] = "Unknown"
    for a_ in td.select("a"):
        issue = a_.find("i")
        if issue is not None:
            text = issue.text.strip()
            if text:
                item["issue"] = text
                break

    series = td.select_one("a")
    item["path"] = series.get("href")
    item["title"] = series.text.strip()
    return item
