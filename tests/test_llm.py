"""Unit tests for the LLM logic."""

import unittest

from cafeteriacritic.llm import menu_collection_to_prompt, OllamaLLM, OpenAILLM
from cafeteriacritic.menu import Menu, MenuItem, MenuTag, MenuCollection


class TestLLM(unittest.TestCase):
    def setUp(self):
        # Generated with llama2
        self.menu_item_1 = MenuItem(
            name='Seared Foie Gras with Balsamic Glaze and Fresh Figs',
            desc=('Seared foie gras served on a bed of fresh figs and '
                  'drizzled with a balsamic glaze'),
            price=65.00,
            tags=frozenset({MenuTag.FARM_TO_FORK})
        )
        self.menu_item_2 = MenuItem(
            name='Mustard Squash Gratin',
            desc=('Made with organic mustard squash, garlic butter, Parmesan '
                  'cheese, and a hint of black pepper'),
            price=15.00,
            tags=frozenset({MenuTag.FARM_TO_FORK})
        )
        self.menu_item_3 = MenuItem(
            name='The Culinary Wanderer',
            desc=('Garlic, onion, tomato paste, chicken broth, and a touch '
                  'of cream; spices include cinnamon, cardamom, turmeric, '
                  'and ginger; garnished with coriander'),
            price=20.00,
            tags=frozenset({MenuTag.HUMANE, MenuTag.FARM_TO_FORK})
        )
        self.menu_item_4 = MenuItem(
            name='Eggplant Scallops',
            desc=('Grilled eggplant slices seasoned with garlic powder, '
                  'salt, pepper, and olive oil; served with fresh lemon '
                  'wedges and balsamic reduction sauce'),
            price=12.00,
            tags=frozenset({MenuTag.VEGETARIAN, MenuTag.VEGAN})
        )
        self.menu_1 = Menu(
            items=frozenset({self.menu_item_1, self.menu_item_2}),
            location='The Tabletop Cafe'
        )
        self.menu_2 = Menu(
            items=frozenset({self.menu_item_3, self.menu_item_4}),
            location='Dinner in the Sky'
        )
        self.menu_collection = MenuCollection(
            menus=frozenset({self.menu_1, self.menu_2})
        )

    def test_menu_collection_to_prompt(self):
        # Act
        prompt = menu_collection_to_prompt(self.menu_collection)
        print(prompt)

        # Assert
        self.assertTrue(self.menu_item_1.name in prompt)
        self.assertTrue(self.menu_item_1.desc in prompt)

    def test_ollamallm(self):
        # Arrange
        try:
            ollama_llm = OllamaLLM(model='llama2')
        except ValueError as error:
            print(f'Error instantiating LLM: {error}')
            print('Skipping test')
            return
        prompt = menu_collection_to_prompt(self.menu_collection)

        # Act
        response = ollama_llm.send_prompt(prompt)
        print(response)

        # Assert
        self.assertTrue((self.menu_1.location in response or
                         self.menu_2.location in response))

    def test_openaillm(self):
        # Arrange
        try:
            openai_llm = OpenAILLM()
        except ValueError as error:
            print(f'Error instantiating LLM: {error}')
            print('Skipping test')
            return
        prompt = menu_collection_to_prompt(self.menu_collection)

        # Act
        response = openai_llm.send_prompt(prompt)

        # Assert
        self.assertTrue((self.menu_1.location in response or
                         self.menu_2.location in response))


if __name__ == '__main__':
    unittest.main()
