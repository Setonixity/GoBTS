from __future__ import annotations
from pathlib import Path

import pygame

from gobts.client.theme import ToolbarTheme
from gobts.client.toolbar.layout import ToolbarLayout
from gobts.client.toolbar.tool import Tool

SUPERSAMPLE = 8

class ToolbarRenderer:

    def __init__(self, layout: ToolbarLayout, theme: ToolbarTheme):
        self.layout = layout
        self.theme = theme
        self.icons = {
            # Tool.SETUP: self.make_node_icon(),
            Tool.SETUP: self.make_svg_icon(theme.setup_icon, override_rgb=False),
            Tool.TRIANGLE_CROSS: self.make_svg_icon(theme.triangle_cross_icon),
            Tool.CIRCLE_SQUARE: self.make_svg_icon(theme.circle_square_icon),
            Tool.LETTER_NUMBER: self.make_svg_icon(theme.letter_number_icon)
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

    def make_svg_icon(self, path: str|Path, override_rgb: bool = True) -> pygame.Surface:
        theme = self.theme
        sprite = pygame.image.load_sized_svg(path, (theme.icon_size, theme.icon_size))
        if override_rgb:
            sprite.fill((0,0,0), special_flags=pygame.BLEND_RGB_MULT)
            sprite.fill(theme.icon_rgb, special_flags=pygame.BLEND_RGB_ADD)
        return sprite