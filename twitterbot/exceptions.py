from dataclasses import dataclass


@dataclass
class TwitterBotException(BaseException):
    msg: str


class MaximumRetryException(TwitterBotException):
    pass
