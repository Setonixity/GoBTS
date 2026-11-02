from __future__ import annotations

import pygame

from gobts.client.ui.layout import MenuBarLayout
from gobts.client.ui.menu import Menu

MENU_ACTION = pygame.event.custom_type()

class MenuBar:

    def __init__(self, menus: list[Menu], font: pygame.font.Font):
        self.menus = menus
        self.open_index: int|None = None
        self.layout = MenuBarLayout.fit(menus, font)

    def handle_event(self, event: pygame.event.Event):
        if event.type == MENU_ACTION:
            event.action()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            title = self.layout.title_at(event.pos)
            if title != None:
                self.open_index = title
                return True
            if self.open_index != None:
                return True
            return event.pos[1] < self.layout.height
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.open_index == None:
                return False
            i = self.layout.item_at(self.open_index, event.pos)
            if i == None:
                return False
            item = self.menus[self.open_index].items[i]
            self.open_index = None
            pygame.event.post(pygame.event.Event(MENU_ACTION, action=item.action))
            return True
        return False

