from collections import namedtuple

Developer = namedtuple("Developer", ("name", "url"))
IAP = namedtuple("IAP", ("name", "price"))
PrivacyCard = namedtuple("PrivacyCard", ("title", "items"))
Rating = namedtuple("Rating", ("value", "count"))
