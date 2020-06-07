from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from twitterbot.datatypes import Tweet
from typing import ClassVar, List, Any


@dataclass
class TweetsParser:
    data: str
    __soup: Any = field(default=None, init=False, repr=False)
    __tweet_html: Any = field(default=None, init=False, repr=False)
    __original_tweet: Any = field(default=None, init=False, repr=False)
    __min_range: ClassVar[int] = 0
    __max_range: ClassVar[int] = 20

    def __post_init__(self):
        self.__soup = BeautifulSoup(self.data, "html.parser")
        self.__tweet_html = self.__soup.select("p[class*='tweet-text']")
        self.__original_tweet = self.__soup.select("div[class*='js-stream-tweet']")

    @property
    def reply_count(self) -> list:
        reply_count = [
            span.attrs.get("data-tweet-stat-count")
            for span in self.__soup.select(
                "span.ProfileTweet-action--reply > span.ProfileTweet-actionCount"
            )
        ]
        assert (
            self.__min_range < len(reply_count) <= self.__max_range
        ), f"Expected at most Reply {self.__max_range} counts, Received: {len(reply_count)}"
        return reply_count

    @property
    def retweets_count(self) -> list:
        retweet_count = [
            span.attrs.get("data-tweet-stat-count")
            for span in self.__soup.select(
                "span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount"
            )
        ]
        assert (
            self.__min_range < len(retweet_count) <= self.__max_range
        ), f"Expected at most {self.__max_range} Re-tweets counts, Received: {len(retweet_count)}"
        return retweet_count

    @property
    def images(self) -> list:
        contents = self.__soup.select(".content")
        external_image = []
        for content in contents:
            temp_img = []
            for tag in content.select(".AdaptiveMedia-photoContainer"):
                temp_img.append(tag.attrs.get("data-image-url"))
            external_image.append(temp_img)
        assert (
            self.__min_range < len(external_image) <= self.__max_range
        ), f"Expected at most {self.__max_range} images counts, Received: {len(external_image)}"
        return external_image

    @property
    def tagged_users(self) -> list:
        paragraph_wise_tagged_person = []
        paragraph_wise_mentioned_in_tweet = [
            paragraph.select("a[class*='twitter-atreply']")
            for paragraph in self.__tweet_html
        ]
        for tags in paragraph_wise_mentioned_in_tweet:
            external_urls = []
            for tag in tags:
                external_urls.append(tag.text)
            paragraph_wise_tagged_person.append(external_urls)
        assert (
            self.__min_range < len(paragraph_wise_tagged_person) <= self.__max_range
        ), f"Expected at most {self.__max_range} tagged users, Received: {len(paragraph_wise_tagged_person)}"
        return paragraph_wise_tagged_person

    @property
    def external_urls(self) -> list:
        paragraph_wise_expanded_url = []
        paragraph_wise_anchor_tags_in_tweet = [
            paragraph.select("a") for paragraph in self.__tweet_html
        ]
        for tags in paragraph_wise_anchor_tags_in_tweet:
            external_urls = []
            for tag in tags:
                external_url = tag.attrs.get("data-expanded-url")
                if external_url:
                    external_urls.append(external_url)
            paragraph_wise_expanded_url.append(external_urls)
        assert (
            self.__min_range < len(paragraph_wise_expanded_url) <= self.__max_range
        ), f"Expected at most {self.__max_range} external-urls, Received: {len(paragraph_wise_expanded_url)}"
        return paragraph_wise_expanded_url

    @property
    def timestamp(self) -> list:
        timestamps = [
            int(span.attrs.get("data-time"))
            for span in self.__soup.select("._timestamp")
            if isinstance(span.attrs.get("data-time"), str)
            and span.attrs.get("data-time")
        ]
        assert (
            self.__min_range < len(timestamps) <= self.__max_range
        ), f"Expected at most {self.__max_range} timestamps, Received: {len(timestamps)}"
        return timestamps

    @property
    def tweets_nonce(self) -> list:
        nonces = [div.attrs.get("data-tweet-nonce") for div in self.__original_tweet]
        assert (
            self.__min_range < len(nonces) <= self.__max_range
        ), f"Expected at most {self.__max_range} tweets nonce, Received: {len(nonces)}"
        return nonces

    @property
    def permalinks(self) -> list:
        permalink = [
            div.attrs.get("data-permalink-path") for div in self.__original_tweet
        ]
        assert (
            self.__min_range < len(permalink) <= self.__max_range
        ), f"Expected at most {self.__max_range} permalinks, Received: {len(permalink)}"
        return permalink

    @property
    def hash_tags(self) -> list:
        paragraph_wise_hash_tags = []
        paragraph_wise_hash_tags_in_tweet = [
            paragraph.select("a[class*='twitter-hashtag']")
            for paragraph in self.__tweet_html
        ]
        for tags in paragraph_wise_hash_tags_in_tweet:
            hash_tags = []
            for tag in tags:
                tag_text = tag.text
                hash_tags.append(tag_text)
            paragraph_wise_hash_tags.append(hash_tags)
        assert (
            self.__min_range < len(paragraph_wise_hash_tags) <= self.__max_range
        ), f"Expected at most {self.__max_range} hash_tags, Received: {len(paragraph_wise_hash_tags)}"
        return paragraph_wise_hash_tags

    @property
    def tweets_text(self) -> list:
        texts = [p.text for p in self.__tweet_html]
        assert (
            self.__min_range < len(texts) <= self.__max_range
        ), f"Expected at most {self.__max_range} tweets text, Received: {len(texts)}"
        return texts

    @property
    def favourites_count(self) -> list:
        favourite_counts = [
            span.attrs.get("data-tweet-stat-count")
            for span in self.__soup.select(
                "span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount"
            )
        ]
        assert (
            self.__min_range < len(favourite_counts) <= self.__max_range
        ), f"Expected at most {self.__max_range} favourites counts, Received: {len(favourite_counts)}"
        return favourite_counts

    @property
    def parsed_tweets(self) -> List[Tweet]:
        tweets = []
        for i in range(len(self.tweets_text)):
            tweet = Tweet(
                text=self.tweets_text[i],
                permalink=self.permalinks[i],
                nonce=self.tweets_nonce[i],
                timestamp=self.timestamp[i],
                external_urls=self.external_urls[i],
                images=self.images[i],
                hash_tags=self.hash_tags[i],
                tagged_persons=self.tagged_users[i],
                favourite_count=self.favourites_count[i],
                reply_count=self.reply_count[i],
                retweet_count=self.retweets_count[i],
            )
            tweets.append(tweet)
        return tweets
