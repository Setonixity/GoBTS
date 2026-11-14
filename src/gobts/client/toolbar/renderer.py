from __future__ import annotations
from pathlib import Path

import pygame

from gobts.client.theme import ToolbarTheme
from gobts.client.toolbar.layout import ToolbarLayout
from gobts.client.toolbar.tool import Tool
from gobts.client.sprites import make_svg_icon

SUPERSAMPLE = 8

class ToolbarRenderer:

    def __init__(self, layout: ToolbarLayout, theme: ToolbarTheme):
        self.layout = layout
        self.theme = theme
        icon_size = (theme.icon_size, theme.icon_size)
        self.icons = {
            # Tool.SETUP: self.make_node_icon(),
            Tool.SETUP: make_svg_icon(theme.setup_icon, icon_size),
            Tool.TRIANGLE_CROSS: make_svg_icon(theme.triangle_cross_icon, icon_size, theme.icon_rgb),
            Tool.CIRCLE_SQUARE: make_svg_icon(theme.circle_square_icon, icon_size, theme.icon_rgb),
            Tool.LETTER_NUMBER: make_svg_icon(theme.letter_number_icon, icon_size, theme.icon_rgb)
        }

    def draw(self, surface: pygame.Surface, selected: Tool):
        layout = self.layout
        theme = self.theme
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)

        pygame.draw.rect(surface, theme.background_rgb, layout.rect)
        for tool, rect in layout.button_rects.items():
            if tool == selected:
                pygame.draw.rect(surface, theme.selected_rgb, rect)
            elif rect.collidepoint(mouse):
                pygame.draw.rect(surface, theme.hover_rgb, rect)
            icon = self.icons[tool]
            surface.blit(icon, icon.get_rect(center=rect.center))