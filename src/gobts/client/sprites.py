from __future__ import annotations

from pathlib import Path

import pygame

from gobts.client.theme import RGB

SUPERSAMPLE = 8

def supersample_canvas(size: tuple[int, int], blend_rgb: RGB = (0, 0, 0)) -> tuple[pygame.Surface]:
    big = pygame.Surface((size[0]*SUPERSAMPLE, size[1]*SUPERSAMPLE), pygame.SRCALPHA)
    big.fill((*blend_rgb, 0))
    return big
 
def downsample(big: pygame.Surface) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (big.get_width() // SUPERSAMPLE, big.get_height() // SUPERSAMPLE))

def centered_canvas(radius: float, blend_rgb: RGB = (0, 0, 0)) -> tuple[pygame.Surface, tuple[float, float]]:
    size = int(radius*2) + 1
    big = supersample_canvas((size, size), blend_rgb)
    return big, (big.get_width()/2, big.get_height()/2)
 
def make_svg_icon(path: str|Path, size: tuple[int, int], rgb: RGB|None = None) -> pygame.Surface:
    sprite = pygame.image.load_sized_svg(path, size)
    if rgb != None:
        sprite.fill((0,0,0), special_flags=pygame.BLEND_RGB_MULT)
        sprite.fill(rgb, special_flags=pygame.BLEND_RGB_ADD)
    return sprite