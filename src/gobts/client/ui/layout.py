from __future__ import annotations
from dataclasses import dataclass

import pygame

from gobts.client.ui.menu import Menu

BAR_HEIGHT = 22
PAD_X = 8
MIN_DROPDOWN_WIDTH = 180
ITEM_HEIGHT = 22

@dataclass
class MenuBarLayout:
    height: int
    title_rects: list[pygame.Rect]
    dropdown_rects: list[pygame.Rect]
    item_rects: list[pygame.Rect]

    @classmethod
    def fit(cls, menus: list[Menu], font: pygame.font.Font) -> MenuBarLayout:
        t_rects, d_rects, i_rects = [], [], []
        t_x = 0
        for menu in menus:
            t_width = font.size(menu.label)[0] + 2*PAD_X 
            title = pygame.Rect(t_x , 0, t_width, BAR_HEIGHT)
            t_x += t_width

            i_widths = [font.size(item.label)[0] + 2*PAD_X for item in menu.items]
            d_width = max([MIN_DROPDOWN_WIDTH] + i_widths)
            dropdown = pygame.Rect(title.x, BAR_HEIGHT - 1, d_width, len(menu.items) * ITEM_HEIGHT)

            items = [pygame.Rect(dropdown.x, dropdown.y + i*ITEM_HEIGHT, dropdown.width, ITEM_HEIGHT) for i in range(len(menu.items))]

            t_rects.append(title)
            d_rects.append(dropdown)
            i_rects.append(items)
        return cls(BAR_HEIGHT, t_rects, d_rects, i_rects)

    def title_at(self, pos: tuple[float, float]) -> int|None:
        for i, rect in enumerate(self.title_rects):
            if rect.collidepoint(pos):
                return i
        return None

    def item_at(self, menu_index: int, pos: tuple[float, float]) -> int|None:
        for i, rect in enumerate(self.item_rects[menu_index]):
            if rect.collidepoint(pos):
                return i
        return None