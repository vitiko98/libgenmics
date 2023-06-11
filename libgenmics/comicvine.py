from typing import List, Optional

from pydantic import BaseModel
import requests

_BASE_URL = "https://comicvine.gamespot.com/api"


class PersonCredit(BaseModel):
    api_detail_url: str
    id: int
    name: str
    role: str
    site_detail_url: str


class Relationship(BaseModel):
    api_detail_url: str
    id: int
    name: str
    site_detail_url: str


class Publisher(BaseModel):
    api_detail_url: str
    id: int
    name: str


class ComicVolume(BaseModel):
    id: int
    publisher: Optional[Publisher]
    name: str


_CREDIT_KEYS = (
    "writer",
    "penciller",
    "inker",
    "colorist",
    "letterer",
    "coverartist",
    "editor",
    "translator",
)


class ComicIssue(BaseModel):
    aliases: Optional[str] = None
    api_detail_url: str
    character_credits: List[Relationship]
    #    concept_credits: List[str]
    cover_date: Optional[str] = None
    date_added: Optional[str] = None
    description: Optional[str] = None
    id: int
    issue_number: str
    location_credits: List[Relationship]
    name: str = ""
    person_credits: List[PersonCredit]
    site_detail_url: str = ""
    store_date: Optional[str]
    team_credits: List[Relationship]
    volume: Relationship
    volume_fetched: Optional[ComicVolume]

    def to_comic_info_xml_params(self):
        item = dict()
        for credit in self.person_credits:
            for credit_key in credit.role.split(","):
                if credit_key in _CREDIT_KEYS:
                    credit_key = credit_key.strip().title()
                    if credit_key not in item:
                        item[credit_key] = {credit.name}
                    else:
                        item[credit_key].add(credit.name)

        item = {k: ", ".join(v) for k, v in item.items()}

        item.update(
            {
                "Title": self.name,
                "Series": self.volume.name,
                "Number": self.issue_number,
                "Web": self.site_detail_url,
            }
        )
        if (
            self.volume_fetched is not None
            and self.volume_fetched.publisher is not None
        ):
            item.update({"Publisher": self.volume_fetched.publisher.name})

        return item


class Client:
    def __init__(self, api_key) -> None:
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "comicvine.py"})
        self._api_key = api_key

    def issue(self, id_or_url, load_volume=True):
        id = str(id_or_url).rstrip("/").split("-")[-1]
        params = {"api_key": self._api_key, "format": "json"}
        response = self._session.get(f"{_BASE_URL}/issue/4000-{id}/", params=params)
        response.raise_for_status()

        issue = ComicIssue(**response.json()["results"])
        if load_volume:
            issue.volume_fetched = self.volume(issue.volume.id)

        return issue

    def volume(self, id_or_url):
        id = str(id_or_url).rstrip("/").split("-")[-1]
        params = {"api_key": self._api_key, "format": "json"}
        response = self._session.get(f"{_BASE_URL}/volume/4050-{id}/", params=params)
        response.raise_for_status()

        return ComicVolume(**response.json()["results"])
