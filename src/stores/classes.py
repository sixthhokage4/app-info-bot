from collections import namedtuple

PlatformAttr = namedtuple("PlatformAttr", ("platform", "name", "value"))
Developer = namedtuple("Developer", ("name", "url"))
Price = namedtuple("Price", ("name", "price"))
PrivacyCard = namedtuple("PrivacyCard", ("title", "items"))
Rating = namedtuple("Rating", ("value", "count"))
