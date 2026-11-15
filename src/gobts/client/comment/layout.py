from __future__ import annotations

from dataclasses import dataclass

import pygame

from gobts.client.theme import CommentTheme

ELLIPSIS = "…"

@dataclass
class CommentLayout:
    rect: pygame.Rect
    name_rect: pygame.Rect
    body_rect: pygame.Rect
    text_rect: pygame.Rect
    name: str
    lines: list[str]
    line_height: int
    
    @classmethod
    def fit(cls, rect: pygame.Rect, name: str, comment: str, font: pygame.font.Font, theme: CommentTheme) -> CommentLayout:
        pad, text_pad = theme.pad, theme.text_pad
        name_rect = pygame.Rect(rect.x + pad, rect.y + pad, rect.width - 2*pad, theme.name_height)
        body_rect = pygame.Rect(name_rect.x, name_rect.bottom + pad, name_rect.width, max(0, rect.bottom - name_rect.bottom - 2*pad))
        text_rect = body_rect.inflate(-2*text_pad, -2*text_pad)
        return cls(
            rect = rect,
            name_rect = name_rect,
            body_rect = body_rect,
            text_rect = text_rect,
            name = cut_off(name, font, name_rect.width - 2*text_pad),
            lines = wrap(comment, font, text_rect.width),
            line_height = font.get_linesize()
        )

    @property
    def visible_lines(self) -> int:
        return max(1, self.text_rect.height // self.line_height)

def cut_off(text: str, font: pygame.font.Font, width: int) -> str:
    if font.size(text)[0] <= width:
        return text
    while text and font.size(text + ELLIPSIS)[0] > width:
        text = text[:-1]
    return text.rstrip() + ELLIPSIS

def wrap(text: str, font: pygame.font.Font, width: int) -> list[str]:
    if width <= 0: 
        return []
    lines: list[str] = []
    for paragraph in text.strip().splitlines():
        line = ""
        for word in paragraph.split():
            joined = f"{line} {word}" if line else word
            if font.size(joined)[0] <= width:
                line = joined
                continue
            if line:
                lines.append(line)
            while len(word) > 1 and font.size(word)[0] > width: 
                cut = len(word) - 1
                while cut > 1 and font.size(word[:cut])[0] > width:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            line = word
        lines.append(line)
    return lines