import requests

from settings import GITHUB
from stores.classes import (
    Developer,
    PlatformAttr,
    Price,
    PrivacyCard,
    Rating,
)
from utils import fancy_join

URL = "https://amp-api.apps.apple.com/v1/catalog/US/apps/{app_id}"

EXTEND = [
    "description",
    "developerInfo",
    "distributionKind",
    "editorialVideo",
    "fileSizeByDevice",
    "messagesScreenshots",
    "platformAttributes",
    "privacy",
    "privacyPolicyUrl",
    "privacyPolicyText",
    "promotionalText",
    "screenshotsByType",
    "supportURLForLanguage",
    "versionHistory",
    "videoPreviewsByType",
    "websiteUrl",
]
INCLUDE = [
    "genres",
    "developer",
    "reviews",
    "merchandised-in-apps",
    "customers-also-bought-apps",
    "developer-other-apps",
    "app-bundles",
    "top-in-apps",
]
PLATFORMS = ["appletv", "ipad", "iphone", "mac"]


PARAMS = {
    "platform": "web",
    "additionalPlatforms": ",".join(PLATFORMS),
    "extend": ",".join(EXTEND),
    "include": ",".join(INCLUDE),
    "l": "en-us",
    "limit[merchandised-in-apps]": 20,
}

HEADERS = {
    "authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNSRjVITkJHUFEifQ.eyJpc3MiOiI4Q1UyNk1LTFM0IiwiaWF0IjoxNjA4MTYzMDk0LCJleHAiOjE2MTExODcwOTR9.FSD4K4vZZy1ouVlyS-vXLQavXuXVo5kbWQGnYIgoWq8Am5DwP7tJlLjkLxeZ0k3D2XDH0F6fAN4FwfUYCIqXGw",
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0)",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://apps.apple.com",
    "referer": "https://apps.apple.com/",
}


class AppStoreApplication:
    store = "App Store"

    def __init__(self, url: str):
        url = URL.format(app_id=url.split("/")[-1].replace("id", ""))
        response = requests.get(url, headers=HEADERS, params=PARAMS)
        data = response.json()["data"][0]

        self.attributes = data["attributes"]
        self.relationships = data["relationships"]

    @property
    def age(self) -> str:
        return self.attributes["contentRatingsBySystem"]["appsApple"]["name"]

    @property
    def category(self) -> str:
        return self.attributes["genreDisplayName"]

    @property
    def developer(self) -> Developer:
        dev = self.relationships["developer"]["data"][0]["attributes"]
        return Developer(name=dev["name"], url=dev["url"])

    @property
    def description(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform,
                    name="description",
                    value=data["description"]["standard"],
                ),
            )

        return attrs

    @property
    def iaps(self) -> list[Price]:
        iaps = []

        for data in self.relationships["top-in-apps"]["data"]:
            iaps.append(
                Price(
                    name=data["attributes"]["name"],
                    price=data["attributes"]["offers"][0]["priceFormatted"],
                )
            )

        return iaps

    @property
    def platforms(self) -> list[str]:
        return self.attributes["deviceFamilies"]

    @property
    def prices(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            for offer in data["offers"]:
                if offer["type"] != "get":
                    continue

                attrs.append(
                    PlatformAttr(
                        platform=platform,
                        name="price",
                        value=offer["priceFormatted"] if offer["price"] else "Free",
                    ),
                )

        return attrs

    @property
    def privacy_cards(self) -> list[PrivacyCard]:
        cards = []

        for data in self.attributes["privacy"]["privacyTypes"]:
            cards.append(
                PrivacyCard(
                    title=data["privacyType"],
                    items=list(
                        map(
                            lambda category: category["dataCategory"],
                            data["dataCategories"],
                        )
                    ),
                )
            )

        return cards

    @property
    def privacy_policy(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform, name="policy", value=data["privacyPolicyUrl"]
                ),
            )

        return attrs

    @property
    def rating(self) -> Rating:
        user_rating = self.attributes["userRating"]
        return Rating(user_rating["ariaLabelForRatings"], user_rating["ratingCount"])

    @property
    def size(self) -> str:
        values = self.attributes["fileSizeByDevice"].values()
        return f"{(sum(values)/len(values)) // 1024 // 1024} MB"

    @property
    def subtitle(self) -> list[PlatformAttr]:
        attrs = []

        for platform, data in self.attributes["platformAttributes"].items():
            attrs.append(
                PlatformAttr(
                    platform=platform, name="subtitle", value=data["subtitle"]
                ),
            )

        return attrs

    @property
    def title(self) -> str:
        return self.attributes["name"]

    @property
    def url(self) -> str:
        return self.attributes["url"]

    def __str__(self) -> str:
        lines = []

        print(self.subtitle)
        lines.append(f"## [**{self.title}**]({self.url})")
        lines.append(f" > by [{self.developer.name}]({self.developer.url})")

        lines.append("\n____\n")

        lines.append("#### ℹ️ **App Info**")

        lines.append(f"**Age**: {self.age}.")
        lines.append(f"**Category**: {self.category}.")
        lines.append(f"**Platforms**: {fancy_join(', ', self.platforms, ' & ')}.")

        rating = self.rating
        lines.append(f"**Rating**: {rating.value} ({rating.count} ratings).")
        lines.append(f"**Size**: {self.size}.")

        lines.append("#### 💸 **Pricing**")

        lines.append(f"**Prices**:")

        for price in self.prices:
            lines.append(f" * {price.platform}: {price.value}")

        iaps = self.iaps

        if len(iaps) > 5:
            count = "5+"
        elif len(iaps) == 0:
            count = "None"
        else:
            count = str(len(iaps))

        lines.append(f"**In-App Purchases**: {count}")

        for iap in iaps[:5]:
            lines.append(f" * {iap.name}: {iap.price}")

        lines.append("#### 🔒️ **Privacy**")

        lines.append(f"**Policy**: {self.privacy_policy}")
        lines.append(f"**Specification**:")
        for card in self.privacy_cards:
            if card.items:
                lines.append(f" * {card.title}: {fancy_join(', ', card.items, ' & ')}.")
            else:
                lines.append(f" * {card.title}.")

        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append(f"^[github]({GITHUB})")

        return "  \n".join(lines)
