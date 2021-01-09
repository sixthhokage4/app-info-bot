from urllib import parse

import requests
from bs4 import BeautifulSoup

from utils import fancy_join
from .helpers import find_by_attr, find_all_by_attr

from stores.classes import (
    Developer,
    IAP,
    PrivacyCard,
    Rating,
)


class AppStoreApplication:
    store = "App Store"

    @staticmethod
    def us_store(url: str) -> str:
        url = parse.urlsplit(url)
        path = url.path

        if not path.startswith("/app"):
            path = url.path.split("/", 2)[-1]

        return f"https://{url.hostname}/{path}"

    def __init__(self, url: str, use_us_store: bool = True):
        if use_us_store:
            url = self.us_store(url)

        response = requests.get(url)
        self.soup = BeautifulSoup(response.content, features="html.parser")

    @property
    def category(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-category")
        return tag.text.strip() if tag else None

    @property
    def compatibility(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-compatibility")
        return tag.text.strip().split(". ")[0] if tag else None

    @property
    def description(self) -> list[str]:
        tag = find_by_attr(self.soup, "div", "data-test-description")
        return [str(p) for p in tag.find("p") if str(p) != "<br/>"]

    @property
    def developer(self) -> Developer:
        tag = find_by_attr(self.soup, "a", "data-test-developer-link")
        return Developer(name=tag.text.strip(), url=tag["href"])

    @property
    def iaps(self) -> list[IAP]:
        tags = find_all_by_attr(self.soup, "li", "data-test-app-info-iap")

        iaps = []

        for li in tags:
            split = li.text.strip().split("\n")

            if len(split) == 2:
                iaps.append(IAP(split[0], split[1]))
            elif len(split) == 1:
                iaps.append(IAP(split[0], ""))

        return iaps

    @property
    def last_update(self) -> str:
        tag = find_by_attr(self.soup, "time", "data-test-we-datetime")
        return tag.text if tag else None

    @property
    def platforms(self) -> list[str]:
        tags = find_all_by_attr(self.soup, "a", "data-test-app-platform-link")
        return [a.text.strip() for a in tags]

    @property
    def price(self) -> str:
        tag = self.soup.find("li", class_="app-header__list__item--price")
        return tag.text.strip()

    @property
    def privacy_cards(self) -> list[PrivacyCard]:
        tags = self.soup.find_all("div", class_="ember-view app-privacy__card")

        cards = []
        for tag in tags:
            spans = tag.find_all(
                "span",
                class_="privacy-type__grid-content privacy-type__data-category-heading",
            )

            cards.append(
                PrivacyCard(
                    title=tag.find("h3", class_="privacy-type__heading").text,
                    items=list(map(lambda span: span.text.strip(), spans)),
                )
            )

        return cards

    @property
    def privacy_policy(self) -> str:
        tag = find_by_attr(self.soup, "a", "data-test-app-info-links-privacy")
        return tag["href"] if tag else None

    @property
    def rating(self) -> Rating:
        tag = find_by_attr(self.soup, "div", "data-test-average-rating")
        score = tag.text if tag else None

        tag = find_by_attr(self.soup, "p", "data-test-rating-count")
        count = tag.text.lower() if tag else None

        if not score or not count:
            return None

        return Rating(score, count)

    @property
    def size(self) -> str:
        tag = find_by_attr(self.soup, "dd", "data-test-app-info-size")
        return tag.text if tag else None

    @property
    def subtitle(self) -> str:
        tag = find_by_attr(self.soup, "h2", "data-test-product-subtitle")
        return tag.text.strip() if tag else None

    @property
    def title(self) -> str:
        tag = find_by_attr(self.soup, "h1", "data-test-product-name")
        return tag.find(text=True).strip()

    @property
    def url(self) -> str:
        return self.soup.find("link", rel="canonical")["href"]

    def __str__(self) -> str:
        lines = []

        lines.append(f"## [**{self.title}**]({self.url})")
        lines.append(f" > by [{self.developer.name}]({self.developer.url})")

        lines.append("\n____\n")

        lines.append("#### ℹ️ **App Info**")

        lines.append(f"**Category**: {self.category}.")
        lines.append(f"**Compatibility**: {self.compatibility}.")
        lines.append(f"**Platforms**: {fancy_join(', ', self.platforms, ' & ')}.")

        rating = self.rating

        if rating:
            lines.append(f"**Rating**: {rating.value} ({rating.count}).")
        else:
            lines.append(f"**Rating**: -.")

        lines.append(f"**Size**: {self.size}.")

        lines.append("#### 💸 **Pricing**")

        lines.append(f"**Price**: {self.price}")

        iaps = self.iaps

        if len(iaps) == 3:
            count = "3+"
        elif len(iaps) == 0:
            count = "None"
        else:
            count = str(len(iaps))

        lines.append(f"**In-App Purchases**: {count}")

        if iaps:
            for iap in iaps:
                if iap.price:
                    lines.append(f" * {iap.name}: {iap.price}")
                else:
                    lines.append(f" * {iap.name}")

        lines.append("#### 🔒️ **Privacy**")

        lines.append(f"**Policy**: {self.privacy_policy}")
        lines.append(f"**Specification**:")
        for card in self.privacy_cards:
            if card.items:
                lines.append(f" * {card.title}: {fancy_join(', ', card.items, ' & ')}.")
            else:
                lines.append(f" * {card.title}.")

        return "  \n".join(lines)
