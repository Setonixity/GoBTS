from __future__ import annotations

import pygame

from gobts.client.ui.menubar import MenuBar

PAD_X = 8

class UIRenderer:

    def __init__(self, menubar: MenuBar):
        self.font: pygame.font.Font|None = None
        self.menubar = menubar
        self.open_index = menubar.open_index
        self.menus = menubar.menus
        self.height = 22

    def draw(self, surface: pygame.Surface):
        font = self._get_font()
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, surface.get_width(), self.height))

        x = 0
        for i, menu in enumerate(self.menubar.menus):
            rect = pygame.Rect(x, 0, font.size(menu.label)[0] + 2*PAD_X, self.height)
            x = rect.right

            if i == self.open_index or rect.collidepoint(mouse):
                pygame.draw.rect(surface, (100, 100, 100), rect)
            self._blit_text(surface, menu.label, (255, 255, 255), font, midleft=(rect.x+PAD_X, rect.centery - 2))


    def _get_font(self) -> pygame.font.Font:
        if self.font == None:
            self.font = pygame.font.SysFont("ubuntu,segoeui,dejavusans,arial", 13)
        return self.font

    def _blit_text(self, surface: pygame.Surface, text, color: pygame.Color, font: pygame.font.Font, **position):
        image = font.render(text, True, color)
        surface.blit(image, image.get_rect(**position))