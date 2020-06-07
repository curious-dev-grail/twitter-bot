from dataclasses import dataclass, field
from typing import ClassVar
from urllib.parse import urlencode
import requests
from loguru import logger


@dataclass
class NetworkMiddleware:
    __base_url: ClassVar[str] = "https://twitter.com/i/search/timeline?"
    __next_cursor: str = field(default="", init=False, repr=False)
    query: str = ""
    lang: str = None

    @property
    def new_tweets(self):
        params = {
            "f": "tweets",
            "q": self.query,
            "src": "typd",
            "max_position": self.__next_cursor,
        }
        if self.lang:
            params["lang"] = self.lang
        url = self.__base_url + urlencode(params)
        headers = {
            "Host": "twitter.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64)",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{url}",
            "Connection": "keep-alive",
        }
        req = requests.request("GET", url, headers=headers)
        if req.status_code == 200:
            data = req.json()
            has_more_items = data["has_more_items"]
            if not has_more_items:
                self.__next_cursor = ""
                return req.status_code, None
            else:
                self.__next_cursor = data["min_position"]
                return req.status_code, data["items_html"]
        else:
            return req.status_code, None
