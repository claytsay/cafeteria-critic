"""Unit tests for the web scraper/parser logic."""

import unittest
from bs4 import BeautifulSoup

from cafeteriacritic.menu import Menu, MenuItem, MenuTag
from cafeteriacritic.scraper import CafeBonAppetitScraper


class TestScraper(unittest.TestCase):
    def test_cba_scraper(self):
        # Arrange
        menu_expected = Menu(
            location="SJC32",
            items=frozenset(
                [
                    MenuItem(
                        name="Ciabatta Sundried Tomato Breakfast Sandwich",
                        desc="Glaum Egg Ranch scrambled egg, sundried tomato, pepper jack cheese",
                        price=6.00,
                        tags=frozenset([MenuTag.VEGETARIAN, MenuTag.FARM_TO_FORK]),
                    ),
                ]
            ),
        )
        cba_scraper = CafeBonAppetitScraper()
        with open("tests/resources/cafebonappetit_2023-11-27.html", "rb") as f:
            page_soup = BeautifulSoup(f.read(), "html.parser")

        # Act
        menu_actual = cba_scraper._menu_soup_to_menu(
            page_soup, building="SJC32", meal="breakfast"
        )

        # Assert
        self.assertEqual(menu_expected, menu_actual)


if __name__ == "__main__":
    unittest.main()
