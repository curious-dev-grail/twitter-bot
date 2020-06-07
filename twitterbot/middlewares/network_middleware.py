from dataclasses import dataclass, field
from typing import ClassVar
from urllib.parse import urlencode
import requests
import atexit
from loguru import logger
import datetime
import os
import json


@dataclass
class NetworkMiddleware:
    __base_url: ClassVar[str] = "https://twitter.com/i/search/timeline?"
    __next_cursor: str = field(default="", init=False, repr=False)
    query: str = ""
    lang: str = None
    __started_at: str = field(default=None, init=False, repr=False)

    def __post_init__(self):
        atexit.register(self.save_data)
        home = os.path.expanduser("~")
        backup_dir = os.path.join(home, ".twitter-bot")
        if os.path.isdir(backup_dir):
            cache_path = os.path.join(backup_dir, "cache.json")
            if os.path.isfile(cache_path):
                with open(cache_path, "r") as f:
                    data = json.load(f)
                    last_cache = data[-1]
                    self.__next_cursor = last_cache["stopped_at"]

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
                if self.__started_at is None:
                    self.__started_at = data["min_position"]
                self.__next_cursor = data["min_position"]
                logger.debug(f"Cursor Begin From: {self.__started_at}")
                logger.debug(f"Current cursor : {self.__next_cursor}")

                return req.status_code, data["items_html"]
        else:
            return req.status_code, None

    def save_data(self):
        home = os.path.expanduser("~")
        backup_dir = os.path.join(home, ".twitter-bot")
        os.makedirs(backup_dir, exist_ok=True)
        with open(os.path.join(backup_dir, "cache.json"), "w+") as f:
            data = f.read()
            if not data:
                data_to_be_saved = [
                    {
                        "last_started_at": self.__started_at,
                        "stopped_at": self.__next_cursor,
                        "date": datetime.datetime.now().timestamp(),
                    }
                ]

            else:
                data_to_be_saved = json.loads(data)
                data_to_be_saved.append(
                    {
                        "last_started_at": self.__started_at,
                        "stopped_at": self.__next_cursor,
                        "date": datetime.datetime.now().timestamp(),
                    }
                )
            json.dump(data_to_be_saved, f)
