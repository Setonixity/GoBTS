from __future__ import annotations

import pygame

from gobts.client.ui.menubar import MenuBar

class UIRenderer:

    def __init__(self, menubar: MenuBar, font: pygame.font.Font):
        self.menubar = menubar
        self.font = font

    def draw(self, surface: pygame.Surface):
        menubar = self.menubar
        layout = menubar.layout
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)
        hover = layout.title_at(mouse)

        pygame.draw.rect(surface, (0, 0, 0), (0, 0, surface.get_width(), layout.height))

        for i, (menu, rect) in enumerate(zip(menubar.menus, layout.title_rects)):
            if i == menubar.open_index or i == hover:
                pygame.draw.rect(surface, (100, 100, 100), rect)
            self._blit_text(surface, menu.label, (255, 255, 255), center=(rect.centerx, rect.centery - 2))

    def _blit_text(self, surface: pygame.Surface, text, color: pygame.Color, **position):
        image = self.font.render(text, True, color)
        surface.blit(image, image.get_rect(**position))