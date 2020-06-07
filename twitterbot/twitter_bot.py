from dataclasses import dataclass, field
from twitterbot.middlewares import NetworkMiddleware, QueryMiddleWare
from twitterbot.parsers import TweetsParser
from typing import List
import random
import time
from datetime import datetime
import os
import json
from twitterbot import exceptions
from twitterbot.datatypes import Tweet
from loguru import logger


@dataclass
class TwitterBot:
    username: str = None
    since: str = None
    until: str = None
    query_search: str = None
    lang: str = None
    __failure: int = field(default=0, init=False, repr=False)

    def get_tweets(self):
        query = QueryMiddleWare(
            username=self.username,
            since=self.since,
            until=self.until,
            query_search=self.query_search,
        ).query
        network = NetworkMiddleware(query=query, lang=self.lang)
        while True:
            status, tweets = network.new_tweets
            logger.debug(status)
            if status == 200:
                if tweets:
                    yield TweetsParser(tweets).parsed_tweets
                else:
                    return
            else:
                self.sleep()

    def get_all_tweets(self):
        query = QueryMiddleWare(
            username=self.username,
            since=self.since,
            until=self.until,
            query_search=self.query_search,
        ).query
        network = NetworkMiddleware(query=query, lang=self.lang)
        all_tweets: List[Tweet] = list()
        try:
            while True:
                status, tweets = network.new_tweets
                if status == 200:
                    self.__failure = 0
                    if tweets:
                        tweet = TweetsParser(tweets)
                        all_tweets.extend(tweet.parsed_tweets)
                    else:
                        break
                    logger.info(f"Scrapped Tweets: {len(all_tweets)}")
                    time.sleep(random.randint(5, 10))
                else:
                    self.sleep()
        except exceptions.TwitterBotException as e:
            logger.error(e)
        finally:
            return all_tweets

    def save_all_tweet_to_json(self, filename="", path=""):
        all_tweets = self.get_all_tweets()
        logger.info(f"Scrapped Tweets:{len(all_tweets)}")
        if path.strip() and not os.path.exists(os.path.abspath(path)):
            base_path = os.path.abspath(path)
        else:
            base_path = os.path.join(
                os.path.expanduser("~"), "Downloads", "twitter-bot"
            )
            os.makedirs(base_path, exist_ok=True)
        if (
            filename
            and filename.strip()
            and os.path.exists(os.path.join(os.path.join(base_path, filename)))
        ):
            choice = input("File Exists, Do You want to override(y/N):")
            if choice.strip() != "y" or choice.strip() != "Y":
                name, ext = filename.split(".")
                name += f"-{datetime.now()}"
                file = ".".join([name, ext])
            else:
                file = filename
        else:
            file = f"{self.username or self.query_search}-{datetime.now()}.json"
        with open(os.path.join(base_path, file), "w") as f:
            json.dump(all_tweets, f, default=lambda x: x.__dict__)

    def sleep(self):
        if self.__failure > 20:
            self.__failure = 0
            logger.error("Maximum Attempts of Failure Shutting down Bot")
            raise exceptions.MaximumRetryException(
                "Too many failure attempts to scrape tweets"
            )
        if 10 <= self.__failure < 20:
            wait_time = random.choice(20, 120)
            self.__failure += 1
            logger.info(f"Failure Occur, Waiting for {wait_time}")
        else:
            wait_time = random.choice(5, 20)
            self.__failure += 1
            logger.info(f"Failure Occur, Waiting for {wait_time}")
        time.sleep(wait_time)
