from __future__ import annotations

import pygame

from gobts.client.panel.layout import PanelLayout
from gobts.client.theme import PanelTheme

class PanelRenderer:
    def __init__(self, layout: PanelLayout, theme: PanelTheme):
        self.layout = layout
        self.theme = theme

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.theme.background_rgb, self.layout.rect)