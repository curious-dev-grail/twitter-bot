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
    fetch_new: bool = field(default=False)
    __failure: int = field(default=0, init=False, repr=False)

    def get_tweets(self):
        query = QueryMiddleWare(
            username=self.username,
            since=self.since,
            until=self.until,
            query_search=self.query_search,
        ).query
        network = NetworkMiddleware(query=query, lang=self.lang)
        try:
            while True:
                status, tweets = network.new_tweets
                logger.debug(status, f"Tweets: {len(tweets)}")
                if status == 200:
                    if tweets:
                        yield TweetsParser(tweets).parsed_tweets
                    else:
                        logger.info("Tweets Finished")
                        return
                    sleeping_time = random.uniform(5, 15)
                    logger.debug(f"Sleeping For {sleeping_time} seconds")
                    time.sleep(sleeping_time)
                elif status == 204:
                    return
                else:
                    self.__failure += 1
                    self.sleep()
        except exceptions.TwitterBotException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
        finally:
            logger.info("Scraper Stopped")

    def get_all_tweets(self):
        query = QueryMiddleWare(
            username=self.username,
            since=self.since,
            until=self.until,
            query_search=self.query_search,
        ).query
        network = NetworkMiddleware(
            query=query, lang=self.lang, fetch_new=self.fetch_new
        )
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
                        self.__failure += 1
                        self.sleep()
                    logger.info(f"Scrapped Tweets: {len(all_tweets)}")
                    sleeping_time = random.uniform(5, 15)
                    logger.debug(f"Sleeping For: {sleeping_time} seconds")
                    time.sleep(sleeping_time)
                elif status == 204:
                    break
                else:
                    self.__failure += 1
                    self.sleep()
        except exceptions.TwitterBotException as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
        finally:
            logger.info(f"Scrapping Done, scraped {len(all_tweets)} tweets")
            return all_tweets

    def save_all_tweet_to_json(self, filename="", path="", auto_approve: bool = False):
        all_tweets = self.get_all_tweets()
        if path.strip() and not os.path.exists(os.path.abspath(path)):
            base_path = os.path.abspath(path)
        else:
            base_path = os.path.join(
                os.path.expanduser("~"), "Downloads", "twitter-bot"
            )
            os.makedirs(base_path, exist_ok=True)
        file = filename
        if not file or file.strip() == "":
            file = f"{self.username or self.query_search}-{datetime.now()}.json"
        file_exist = os.path.exists(os.path.join(os.path.join(base_path, file)))

        file_path = os.path.join(base_path, file)
        is_override = False
        if not auto_approve and file_exist:
            option = input(
                "File already exist. Do you want to Override(o) or Append(A)? (o/A):"
            )
            is_override = option.strip().lower() == "o"
        if is_override:
            with open(file_path, "w") as f:
                logger.info(f"Writing {len(all_tweets)} to Path: {file_path}")
                json.dump(all_tweets, f, default=lambda x: x.__dict__)
        else:
            mode = "r+"
            file_path = os.path.join(base_path, filename)
            if not os.path.isfile(file_path):
                mode = "w+"
            with open(file_path, mode) as f:
                raw_data = f.read()
                if raw_data:
                    data: list = json.loads(raw_data)
                else:
                    data: list = list()
                logger.info(f"Found {len(data)} Old Tweets")
                if not self.fetch_new:
                    data.extend([tweet.__dict__ for tweet in all_tweets])
                else:
                    data = [tweet.__dict__ for tweet in all_tweets] + data
                temp_data = data[:]
                data = []
                timestamp_included = []
                for tweet in temp_data:
                    if tweet["timestamp"] not in timestamp_included:
                        timestamp_included.append(tweet["timestamp"])
                        data.append(tweet)
                logger.info(f"Writing {len(data)} to Path: {file_path}")
                f.truncate(0)
                f.seek(0)
                json.dump(data, f)

    def sleep(self):
        if self.__failure > 20:
            self.__failure = 0
            logger.error("Maximum Attempts of Failure Shutting down Bot")
            raise exceptions.MaximumRetryException(
                "Too many failure attempts to scrape tweets"
            )
        elif 10 <= self.__failure < 20:
            wait_time = random.uniform(20, 120)
            logger.warning(f"Failure Occur, Waiting for {wait_time}")
        else:
            wait_time = random.uniform(5, 20)
            logger.warning(f"Failure Occur, Waiting for {wait_time}")
        time.sleep(wait_time)
