from __future__ import annotations
from dataclasses import dataclass

import pygame

from gobts.client.ui.menu import Menu
from gobts.client.theme import MenuTheme

@dataclass
class MenuBarLayout:
    height: int
    title_rects: list[pygame.Rect]
    dropdown_rects: list[pygame.Rect]
    item_rects: list[pygame.Rect]
    label_x: list[int]

    @classmethod
    def fit(cls, menus: list[Menu], font: pygame.font.Font, theme: MenuTheme) -> MenuBarLayout:
        t_rects, d_rects, i_rects, label_xs = [], [], [], []
        t_x = 0
        for menu in menus:
            t_width = font.size(menu.label)[0] + 2*theme.pad_x
            title = pygame.Rect(t_x , 0, t_width, theme.bar_height)
            t_x += t_width

            has_checks = any(item.checked != None for item in menu.items)

            label_x = theme.pad_x + (theme.check_width if has_checks else 0)
            i_widths = [font.size(item.label)[0] + 2*theme.pad_x for item in menu.items]
            d_width = max([theme.min_dropdown_width] + i_widths)
            dropdown = pygame.Rect(title.x, theme.bar_height - 1, d_width, len(menu.items) * theme.item_height + 2*theme.dropdown_pad_y)

            items_y = dropdown.y + theme.dropdown_pad_y
            items = [pygame.Rect(dropdown.x, items_y + i*theme.item_height, dropdown.width, theme.item_height) for i in range(len(menu.items))]

            t_rects.append(title)
            d_rects.append(dropdown)
            i_rects.append(items)
            label_xs.append(label_x)
        return cls(theme.bar_height, t_rects, d_rects, i_rects, label_xs)

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