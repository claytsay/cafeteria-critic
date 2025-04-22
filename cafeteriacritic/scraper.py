"""Holds scrapers for various websites."""

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from datetime import date
import logging
import re
import requests

from cafeteriacritic.menu import Menu, MenuItem, MenuTag


class Scraper(ABC):
    """Abstract class for all online menu scrapers."""

    @staticmethod
    @abstractmethod
    def get_menu(*kwargs) -> Menu:
        """TODO

        TODO,
        TODO
        """
        pass


class CafeBonAppetitScraper(ABC):
    """TODO"""

    _URL_BASE = "https://amazonlab126.cafebonappetit.com/cafe/{}/{}/"
    _CAFETERIAS = {
        "SJC38": "sjc38",
        "SJC32": "midway-cafe-sjc-32",
        "SJC31": "sjc31-cafe",
        "SJC10": "a-z-bistro",
        "SJC11": "lab-126-cafe",
        "SJC14": "lab-luxe",
    }
    _MEALS = {"breakfast", "lunch"}

    @staticmethod
    def get_menu(building: str, meal: str = "lunch", day: date = None) -> Menu:
        # Validate inputs
        if not day:
            logging.warning("No day provided; using current day")
            day = date.today()
        if building not in CafeBonAppetitScraper._CAFETERIAS.keys():
            raise ValueError(
                (
                    f"Invalid building: {building}; valid options are: "
                    f'{", ".join(CafeBonAppetitScraper._CAFETERIAS.keys())}'
                )
            )
        if meal not in CafeBonAppetitScraper._MEALS:
            raise ValueError(
                (
                    f"Invalid meal {meal}; valid options are: "
                    f'{", ".join(CafeBonAppetitScraper._MEALS)}'
                )
            )

        # Get menu HTML
        page_response = CafeBonAppetitScraper._fetch_menu_html(building, day)

        # Parse menu HTML
        page_soup = BeautifulSoup(page_response.content, "html.parser")
        menu = CafeBonAppetitScraper._menu_soup_to_menu(
            page_soup, building=building, meal=meal
        )
        return menu

    @staticmethod
    def _fetch_menu_html(building: str, day: date) -> requests.Response:
        url = CafeBonAppetitScraper._URL_BASE.format(
            CafeBonAppetitScraper._CAFETERIAS[building], day.strftime("%Y-%m-%d")
        )
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(
                f"Error fetching page; HTTP response code {response.status_code}"
            )
        return response

    @staticmethod
    def _menu_soup_to_menu(page_soup: BeautifulSoup, building: str, meal: str) -> Menu:
        meal_soup = page_soup.find(id=meal)
        items = []
        for item_soup in meal_soup.find_all(class_="site-panel__daypart-item"):
            name = item_soup.find(
                class_="h4 site-panel__daypart-item-title"
            ).text.strip()
            price = float("NaN")
            for price_soup in item_soup.find_all(class_="price-item__amount"):
                price_text = price_soup.text.strip().replace("$", "")
                if re.match(r"^-?\d+(?:\.\d+)$", price_text) is not None:
                    price = float(price_text)
                    break
            desc_soup = item_soup.find(class_="site-panel__daypart-item-description")
            if desc_soup:
                desc = " ".join(desc_soup.text.strip().split())
            else:
                desc = ""
            tags = []
            tags_soup = item_soup.find(class_="site-panel__daypart-item-cor-icons")
            if tags_soup:
                for tag_soup in tags_soup.find_all("img", alt=True):
                    tags.append(MenuTag(tag_soup["alt"].split(":")[0]))
            items.append(
                MenuItem(name=name, price=price, desc=desc, tags=frozenset(tags))
            )
        return Menu(location=building, items=frozenset(items))


if __name__ == "__main__":
    cbas = CafeBonAppetitScraper()
    cbas.get_menu("SJC32", meal="breakfast", day=date(2023, 11, 27))
