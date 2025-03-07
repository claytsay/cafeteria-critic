"""Holds menu-related data classes and such.

The data classes are frozen/immutable, which allows them to be passed around
more easily without fear of mutation. Each class implements a __str__ method
designed to convey the information in the class in a succinct format easily
processable by both humans and LLMs.
"""

from dataclasses import dataclass
from enum import Enum


class MenuTag(Enum):
    """Tags for menu items."""
    VEGETARIAN = 'Vegetarian'
    VEGAN = 'Vegan'
    HALAL = 'Halal'
    SEAFOOD_WATCH = 'Seafood Watch'
    GLUTEN_FREE = 'Made without Gluten-Containing Ingredients'
    HUMANE = 'Humane'
    FARM_TO_FORK = 'Farm to Fork'


@dataclass(frozen=True)
class MenuItem:
    """Represents a menu item/dish."""

    name: str
    """Name of the dish."""
    price: float
    """Price of the dish, in USD."""
    desc: str
    """Description of the dish."""
    tags: frozenset[MenuTag]
    """Tags describing the properties of the dish."""

    def __str__(self) -> str:
        return (f'{self.name}: {self.desc}. '
                f'{"; ".join(map(lambda x: x.value, self.tags))}. Price: ${self.price:.2f}')


@dataclass(frozen=True)
class Menu:
    """Represents the menu for a single establishment."""

    location: str
    """Location in which the menu is presented."""
    items: frozenset[MenuItem]
    """Dishes/items on the menu."""

    def __str__(self) -> str:
        s = f'{self.location}: \n'
        s += '\n'.join(f'- {i.__str__()}' for i in self.items)
        return s


@dataclass(frozen=True)
class MenuCollection:
    """Represents a collection of menus for multiple establishments."""

    menus: frozenset[Menu]
    """Set of menus, each corresponding to an establishment."""

    def __str__(self) -> str:
        return '\n'.join(m.__str__() for m in self.menus)
