from __future__ import annotations

import pygame

from gobts.client.ui.layout import MenuBarLayout
from gobts.client.ui.menu import Menu

class MenuBar:

    def __init__(self, menus: list[Menu], font: pygame.font.Font):
        self.menus = menus
        self.open_index: int|None = None
        self.layout = MenuBarLayout.fit(menus, font)

    def handle_event(self, event: pygame.event.Event):
        pass


