from __future__ import annotations
 
import pygame

from gobts.client.comment.layout import CommentLayout
from gobts.client.theme import CommentTheme

NAME_HINT = "Name"
COMMENT_HINT = "Comment"

class CommentRenderer:

    def __init__(self, layout: CommentLayout, font: pygame.font.Font, theme: CommentTheme):
        self.layout = layout
        self.font = font
        self.theme = theme

    def __init__(self, layout: CommentLayout, font: pygame.font.Font, theme: CommentTheme):
        self.layout = layout
        self.font = font
        self.theme = theme
 
    def draw(self, surface: pygame.Surface):
        layout = self.layout
        theme = self.theme
 
        pygame.draw.rect(surface, theme.background_rgb, layout.rect)
        clip = surface.get_clip()
        surface.set_clip(layout.rect)
 
        pygame.draw.rect(surface, theme.field_rgb, layout.name_rect)
        pygame.draw.rect(surface, theme.field_rgb, layout.body_rect)
 
        name_rgb = theme.text_rgb if layout.name else theme.hint_rgb
        self.blit_text(surface, layout.name or NAME_HINT, name_rgb, midleft=(layout.name_rect.x + theme.text_pad, layout.name_rect.centery + theme.text_nudge))
 
        text = layout.text_rect
        if not layout.lines:
            self.blit_text(surface, COMMENT_HINT, theme.hint_rgb, topleft=text.topleft)
        visible = layout.lines[0:0 + layout.visible_lines]
        for i, line in enumerate(visible):
            if line:
                self.blit_text(surface, line, theme.text_rgb, topleft=(text.x, text.y + i*layout.line_height))
 
        surface.set_clip(clip)

    def blit_text(self, surface: pygame.Surface, text: str, rgb: RGB, **position):
        image = self.font.render(text, True, rgb)
        surface.blit(image, image.get_rect(height=self.font.get_height(), **position))