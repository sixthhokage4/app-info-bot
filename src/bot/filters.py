from urllib import parse

from praw.models import Submission

from settings import REDDIT_USERNAME
from stores import SUPPORTED_STORES


def is_old(submission: Submission) -> bool:
    return submission.created_utc < 1610150400  # 2019-01-09


def is_self(submission: Submission) -> bool:
    return submission.is_self


def was_analyzed(submission: Submission) -> bool:
    for comment in submission.comments:
        author = comment.author

        if not author:
            continue

        if author.name == REDDIT_USERNAME:
            return True

    return False


def is_unsupported(submission: Submission) -> bool:
    url = parse.urlsplit(submission.url)
    return url.hostname not in SUPPORTED_STORES
