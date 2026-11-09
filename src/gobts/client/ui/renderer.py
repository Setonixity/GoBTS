from __future__ import annotations

import pygame

from gobts.client.theme import MenuTheme
from gobts.client.ui.menubar import MenuBar

SUPERSAMPLE = 8

class UIRenderer:

    def __init__(self, menubar: MenuBar, font: pygame.font.Font, theme: MenuTheme):
        self.menubar = menubar
        self.font = font
        self.theme = theme
        self._dropdown_cache: dict[tuple[int, int], pygame.Surface] = {}

    def draw(self, surface: pygame.Surface):
        menubar = self.menubar
        layout = menubar.layout
        theme = self.theme
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)
        hover = layout.title_at(mouse)

        pygame.draw.rect(surface, theme.bar_rgb, (0, 0, surface.get_width(), layout.height))

        for i, (menu, rect) in enumerate(zip(menubar.menus, layout.title_rects)):
            if i == menubar.open_index or i == hover:
                pygame.draw.rect(surface, theme.hover_rgb, rect)
            self.blit_text(surface, menu.label, theme.text_rgb, center=(rect.centerx, rect.centery + theme.text_nudge))

        if menubar.open_index != None:
            open_i = menubar.open_index
            dropdown = layout.dropdown_rects[open_i]
            surface.blit(self.make_dropdown_sprite(dropdown.size), dropdown)
            
            for item, rect in zip(menubar.menus[open_i].items, layout.item_rects[open_i]):
                if rect.collidepoint(mouse):
                    pygame.draw.rect(surface, theme.hover_rgb, rect)
                if item.checked != None and item.checked():
                    self.blit_text(surface, theme.check_mark, theme.text_rgb, midleft=(rect.x + theme.pad_x, rect.centery + theme.check_nudge))
                self.blit_text(surface, item.label, theme.text_rgb, midleft=(rect.x + layout.label_x[open_i], rect.centery + theme.text_nudge))

    def make_dropdown_sprite(self, size: tuple[int, int]) -> pygame.Surface:
        sprite = self._dropdown_cache.get(size)
        if sprite == None:
            theme = self.theme
            width, height = size
            big = pygame.Surface((width*SUPERSAMPLE, height*SUPERSAMPLE), pygame.SRCALPHA)
            big.fill((*theme.dropdown_rgb, 0))
            pygame.draw.rect(big, theme.dropdown_rgb, big.get_rect(), border_radius=theme.dropdown_corner*SUPERSAMPLE)
            sprite = pygame.transform.smoothscale(big, size)
            self._dropdown_cache[size] = sprite
        return sprite

    def blit_text(self, surface: pygame.Surface, text, color: pygame.Color, **position):
        image = self.font.render(text, True, color)
        surface.blit(image, image.get_rect(height=self.font.get_height(), **position))