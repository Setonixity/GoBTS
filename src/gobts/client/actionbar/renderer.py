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
        self.font = pygame.font.Font(theme.font, theme.font_size)

    def draw(self, surface: pygame.Surface, score_text: str|None = None):
        layout = self.layout
        theme = self.theme
        mouse = pygame.mouse.get_pos() if pygame.mouse.get_focused() else (-1, -1)

        pygame.draw.rect(surface, theme.background_rgb, layout.rect)
        for action, rect in layout.button_rects.items():
            showing_score = action == Action.SCORE and score_text != None
            if showing_score:
                pygame.draw.rect(surface, theme.selected_rgb, rect)
            elif rect.collidepoint(mouse):
                pygame.draw.rect(surface, theme.hover_rgb, rect)
            sprite = self.font.render(score_text, True, theme.text_rgb) if showing_score else self.icons[action]
            surface.blit(sprite, sprite.get_rect(center=(rect.centerx, rect.centery + theme.text_nudge)))

    def make_svg_icon(self, path: str|Path, override_rgb: bool = True) -> pygame.Surface:
        theme = self.theme
        sprite = pygame.image.load_sized_svg(path, (theme.button_width, theme.button_height))
        if override_rgb:
            sprite.fill((0,0,0), special_flags=pygame.BLEND_RGB_MULT)
            sprite.fill(theme.icon_rgb, special_flags=pygame.BLEND_RGB_ADD)
        return sprite