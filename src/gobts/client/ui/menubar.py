from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

@dataclass
class MenuItem:
    label: str
    action: Callable[[], None]

@dataclass
class Menu:
    label: str
    items: list[MenuItem]

class MenuBar:

    def __init__(self, menus: list[Menu]):
        self.menus = menus
        self.open_index: int|None = None
        self.height = 22
