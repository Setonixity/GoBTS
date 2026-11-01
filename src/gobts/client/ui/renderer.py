from __future__ import annotations

import pygame

from gobts.client.ui.menubar import MenuBar

class UIRenderer:

    def __init__(self, menubar: MenuBar):
        self.font: pygame.font.Font|None = None
        self.menubar = menubar

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, surface.get_width(), self.menubar.height))

    # def _get_font()
        