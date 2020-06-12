import argparse
import datetime
from loguru import logger
from twitterbot.twitter_bot import TwitterBot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default=None,
        help="Username whose tweets name to be scrapped",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        default=None,
        help="Query Regarding tweet to be Searched",
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Date since tweet to be scraped. For eg: 2006-03-31",
    )
    parser.add_argument(
        "--until",
        type=str,
        default=None,
        help=f"Date until tweet to be scraped. For eg: {datetime.datetime.now().strftime('%Y-%m-%d')}",
    )
    parser.add_argument("--lang", type=str, default=None, help="Language of the Tweets")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="File Name to which tweets need to be saved in tweet-bot directory of Downloads directory of your home",
    )
    parser.add_argument(
        "--auto-approve",
        default=False,
        help="Auto approve any Inputs.",
        action="store_true"
    )
    parser.add_argument(
        "--fetch-new",
        default=False,
        help="Fetch only New Tweets",
        action="store_true"
    )
    args = parser.parse_args()
    if args.username or args.query:
        bot = TwitterBot(
            username=args.username,
            since=args.since,
            until=args.until,
            query_search=args.query,
            lang=args.lang,
            fetch_new=args.fetch_new
        )
        bot.save_all_tweet_to_json(filename=args.output, auto_approve=args.auto_approve)
    else:
        logger.error("Either of the Option Required --username or --query")


if __name__ == "__main__":
    main()
