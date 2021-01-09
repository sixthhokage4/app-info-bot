import logging
from time import sleep
from urllib import parse

from praw.models import Submission

from reddit import reddit
from settings import REDDIT_SUBREDDITS
from stores import SUPPORTED_STORES
from . import filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_submission(submission: Submission):
    logger.info("Found %s app", submission.url)

    url = parse.urlsplit(submission.url)
    scraper = SUPPORTED_STORES.get(url.hostname)
    info = scraper(url.geturl())

    logger.info("Fetched information for %s from %s", info.title, info.store)

    submission.reply(body=str(info))
    logger.info("Replied to %s", submission.permalink)


def analyze_subreddit(subreddit: str):
    for submission in list(reddit.subreddit(subreddit).new(limit=25)):
        if filters.is_self(submission):
            continue

        if filters.is_unsupported(submission):
            continue

        if filters.is_old(submission):
            continue

        try:
            analyze_submission(submission)
            sleep(1)
        except Exception as exc:
            logging.error(exc, exc_info=True)


def run():
    list(map(analyze_subreddit, REDDIT_SUBREDDITS))
