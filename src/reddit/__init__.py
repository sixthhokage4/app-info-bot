from praw import Reddit

from settings import (
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    REDDIT_CLIENTID,
    REDDIT_CLIENTSECRET,
    REDDIT_USERAGENT,
)

reddit = Reddit(
    client_id=REDDIT_CLIENTID,
    client_secret=REDDIT_CLIENTSECRET,
    user_agent=REDDIT_USERAGENT,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
)

assert reddit.user.me().name == REDDIT_USERNAME
