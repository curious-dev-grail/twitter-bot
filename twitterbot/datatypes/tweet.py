from dataclasses import dataclass


@dataclass
class Tweet:
    text: str
    permalink: str
    nonce: str
    timestamp: int
    external_urls: list
    images: list
    hash_tags: list
    tagged_persons: list
    favourite_count: int
    reply_count: int
    retweet_count: int
