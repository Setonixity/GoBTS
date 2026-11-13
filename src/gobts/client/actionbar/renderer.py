from __future__ import annotations
from pathlib import Path

import pygame

from gobts.client.theme import ActionBarTheme
from gobts.client.actionbar.layout import ActionBarLayout
from gobts.client.actionbar.action import Action

SUPERSAMPLE = 8

class ActionBarRenderer:

    def __init__(self, layout: ActionBarLayout, theme: ActionBarTheme):
        self.layout = layout
        self.theme = theme
        self.icons = {
            Action.PASS: self.make_svg_icon(theme.pass_icon),
            Action.SCORE: self.make_svg_icon(theme.score_icon)
        }

    def draw(self, surface: pygame.Surface):
        layout = self.layout
        theme = self.theme
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)

        pygame.draw.rect(surface, theme.background_rgb, layout.rect)
        for action, rect in layout.button_rects.items():
            if rect.collidepoint(mouse):
                pygame.draw.rect(surface, theme.hover_rgb, rect)
            icon = self.icons[action]
            surface.blit(icon, icon.get_rect(center=rect.center))

    def make_svg_icon(self, path: str|Path, override_rgb: bool = True) -> pygame.Surface:
        theme = self.theme
        sprite = pygame.image.load_sized_svg(path, (theme.icon_size, theme.icon_size))
        if override_rgb:
            sprite.fill((0,0,0), special_flags=pygame.BLEND_RGB_MULT)
            sprite.fill(theme.icon_rgb, special_flags=pygame.BLEND_RGB_ADD)
        return sprite