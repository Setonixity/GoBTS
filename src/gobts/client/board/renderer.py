from __future__ import annotations
import math
import random

import pygame

from gobts.client.board.layout import BoardLayout, Color, Point, Board
from gobts.client.theme import BoardTheme, RGB
from gobts.core.board import Marker

SUPERSAMPLE = 8

class BoardRenderer:

    def __init__(self, board: Board, layout: BoardLayout, theme: BoardTheme):
        self.board = board
        self.layout = layout
        self.theme = theme
        self._sprite_cache: dict[tuple[Color, float], pygame.Surface] = {}
        self._cached_radius: float|None = None

        self._star_cache: dict[float, pygame.Surface] = {}
        self._cached_star_radius: float|None = None 

        self._marker_cache: dict[tuple[Marker, RGB], pygame.Surface] = {}
        self._cached_marker_radius: float|None = None

        self._label_cache: dict[tuple[str, RGB], pygame.Surface] = {}
        self._cached_label_radius: float|None = None
        self._label_font: pygame.font.Font|None = None

        self._surround_tile = pygame.image.load(theme.surround_texture) if theme.surround_texture != None else None

        self._base: pygame.Surface|None = None
        self._cached_base_key: tuple|None = None
        self._clear_cache: dict[float, pygame.Surface] = {}
        self._cached_clear_radius: float|None = None

        self._shifts: dict[tuple[Point, Color], tuple[float, float]] = {}
        self._slides: dict[Point, tuple[tuple[float, float], int]] = {}

    @property
    def animating(self) -> bool:
        return bool(self._slides)

    def draw(self, surface: pygame.Surface, markers: dict[Point, Marker], labels: dict[Point, str], ghost_preview: tuple[Point, Color]|None = None):
        layout = self.layout
        theme = self.theme
        size = layout.size

        base = self.make_base_sprite(surface.get_size())
        surface.blit(base, (0, 0))
        line_width = layout.line_width

        # grid
        for i in range(size):
            pygame.draw.line(surface, theme.line_rgb, layout.to_pixel(Point(i, 0)), layout.to_pixel(Point(i, size-1)), line_width)
            pygame.draw.line(surface, theme.line_rgb, layout.to_pixel(Point(0, i)), layout.to_pixel(Point(size-1, i)), line_width)
        # star points
        star_radius = max(theme.min_star_radius, round(layout.spacing * theme.star_radius))
        star_sprite = self.make_star_sprite(star_radius)
        for point in star_points(layout.size):
            x, y = self.stone_pixel(point)
            surface.blit(star_sprite, (x - star_radius, y - star_radius))

        radius = layout.stone_radius
        self.update_shifts()
        stones = sorted(self.board.stones, key=lambda stone: stone[0] in self._slides)
        for point, color in stones:
            x, y = self.stone_pixel(point)
            surface.blit(self.make_stone_sprite(color, radius), (x - radius, y - radius))
        for point, marker in markers.items():
            x, y = self.stone_pixel(point)
            stone = self.board.get(point)
            if stone == None:
                self.clear_point(surface, base, (x, y), radius*theme.marker_clear)
            rgb = theme.marker_on_black_rgb if stone == Color.BLACK else theme.marker_rgb
            surface.blit(self.make_marker_sprite(marker, rgb, radius), (x - radius, y - radius))
        for point, text in labels.items():
            x, y = self.stone_pixel(point)
            stone = self.board.get(point)
            if stone == None:
                self.clear_point(surface, base, (x, y), radius*theme.marker_clear)
            rgb = theme.marker_on_black_rgb if stone == Color.BLACK else theme.marker_rgb
            sprite = self.make_label_sprite(text, rgb, radius)
            surface.blit(sprite, sprite.get_rect(center=(x, y)))
        if ghost_preview != None and self.board.is_empty(ghost_preview[0]):
            x, y = layout.to_pixel(ghost_preview[0])
            sprite = self.make_stone_sprite(ghost_preview[1], radius).copy()
            sprite.set_alpha(theme.ghost_alpha)
            surface.blit(sprite, (x - radius, y - radius))

    def update_shifts(self):
        theme = self.theme
        now = pygame.time.get_ticks()
        stones = set(self.board.stones)
        self._shifts = {stone: shift for stone, shift in self._shifts.items() if stone in stones}
        self._slides = {point: slide for point, slide in self._slides.items() if now - slide[1] < theme.slide_ms}

        new = stones - set(self._shifts)
        for point, color in new:
            self._shifts[(point, color)] = (random.uniform(-1, 1), random.uniform(-1, 1))
            moved = self.settle_neighbors(point)
            if len(new) == 1:
                angle = random.uniform(0, 2*math.pi)
                distance = theme.stone_slide*self.layout.spacing
                end_x, end_y = self.shift_offset(self._shifts[(point, color)])
                self._slides[point] = ((end_x + distance*math.cos(angle), end_y + distance*math.sin(angle)), now)
                for neighbor, old in moved.items():
                    self._slides[neighbor] = (self.shift_offset(old), now)

    
    def shift_offset(self, shift: tuple[float, float]) -> tuple[float, float]:
        layout, theme = self.layout, self.theme
        stone_radius = layout.stone_radius*theme.stone_image_fill
        reach = max(0, int(layout.spacing) - 2*stone_radius) * theme.stone_shift
        return (shift[0]*reach, shift[1]*reach)

    def draw_ascii(self):
        CORNERS = ["┌", "┐", "└", "┘"] # TL, TR, BL, BR
        EDGES = ["┬", "┴", "├", "┤"] # T, B, L, R
        CENTER       = "┼"
        STAR_POINT   = "⊕"
        HORIZONTAL   = "─"
        BLACK = "●"
        WHITE = "○"

        board = self.board
        stone_map: dict[Point, Color] = dict(board.stones)
        star_map: list[Point] = star_points(board.size)
        # print(stone_map)

        for row in range(board.size):
            row_chars = []
            for col in range(board.size):
                point = Point(col, row)
                char = ""
                if point in stone_map:
                    char = BLACK if stone_map[point] == Color.BLACK else WHITE
                elif point in star_map:
                    char = STAR_POINT

                elif point == Point(0, 0):
                    char = CORNERS[0]
                elif point == Point(board.size - 1, 0):
                    char = CORNERS[1]
                elif point == Point(0, board.size - 1):
                    char = CORNERS[2]
                elif point == Point(board.size - 1, board.size -1):
                    char = CORNERS[3]

                elif row == 0:
                    char = EDGES[0]
                elif row == board.size - 1:
                    char = EDGES[1]
                elif col == 0:
                    char = EDGES[2]
                elif col == board.size - 1:
                    char = EDGES[3]                    

                else:
                    char = CENTER
                row_chars.append(char)
            print(HORIZONTAL.join(row_chars))

    def make_stone_sprite(self, color: Color, radius: float) -> pygame.Surface:
        if radius != self._cached_radius:
            self._sprite_cache.clear()
            self._cached_radius = radius
 
        theme = self.theme
        edge_color = theme.stone_edge_rgb
        fill_color = theme.black_rgb if color == Color.BLACK else theme.white_rgb
        image = theme.black_stone_image if color == Color.BLACK else theme.white_stone_image
        sprite = self._sprite_cache.get((color, radius))
        if sprite == None and image != None:
            size = radius*2 + 1
            ss_size = size*SUPERSAMPLE
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            stone = pygame.image.load_sized_svg(image, (radius*2*SUPERSAMPLE, radius*2*SUPERSAMPLE))
            big.blit(stone, stone.get_rect(center=(ss_size/2, ss_size/2)))
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._sprite_cache[(color, radius)] = sprite
        elif sprite == None:
            size = radius*2 + 1
            ss_size = size*SUPERSAMPLE
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            center = (ss_size/2, ss_size/2)
            edge = max(1, radius*theme.stone_edge) * SUPERSAMPLE
            pygame.draw.circle(big, edge_color, center, radius*SUPERSAMPLE)
            pygame.draw.circle(big, fill_color, center, radius*SUPERSAMPLE - edge)
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._sprite_cache[(color, radius)] = sprite
        return sprite


    def make_star_sprite(self, radius: float) -> pygame.Surface:
        if radius != self._cached_star_radius:
            self._star_cache.clear()
            self._cached_star_radius = radius

        fill_color = self.theme.star_rgb
        sprite = self._star_cache.get(radius)
        if sprite == None:
            size = radius*2 + 1
            ss_size = size*SUPERSAMPLE
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            center = (ss_size/2, ss_size/2)
            pygame.draw.circle(big, fill_color, center, radius*SUPERSAMPLE)
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._star_cache[radius] = sprite
        return sprite

    def make_marker_sprite(self, marker: Marker, rgb: RGB, radius: float) -> pygame.Surface:
        if radius != self._cached_marker_radius:
            self._marker_cache.clear()
            self._cached_marker_radius = radius

        theme = self.theme
        sprite = self._marker_cache.get((marker, rgb))
        if sprite == None:
            size = radius*2 + 1
            ss_size = size*SUPERSAMPLE
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            big.fill((*rgb, 0))
            center = (ss_size/2, ss_size/2)
            reach = radius*theme.marker_size*SUPERSAMPLE # outer edge 
            width = round(max(1, radius*theme.marker_width) * SUPERSAMPLE)
            if marker == Marker.CIRCLE:
                pygame.draw.circle(big, rgb, center, reach, width)
            elif marker == Marker.SQUARE:
                half = reach*0.85 
                pygame.draw.rect(big, rgb, (center[0] - half, center[1] - half, 2*half, 2*half), width)
            elif marker == Marker.TRIANGLE: 
                pygame.draw.polygon(big, rgb, triangle_points(center, reach*1.2))
                pygame.draw.polygon(big, (*rgb, 0), triangle_points(center, reach*1.2 - 2*width))
            elif marker == Marker.CROSS:
                arm = reach*0.75
                pygame.draw.line(big, rgb, (center[0] - arm, center[1] - arm), (center[0] + arm, center[1] + arm), width)
                pygame.draw.line(big, rgb, (center[0] - arm, center[1] + arm), (center[0] + arm, center[1] - arm), width)
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._marker_cache[(marker, rgb)] = sprite
        return sprite

    def make_label_sprite(self, text: str, rgb: RGB, radius: float) -> pygame.Surface:
        if radius != self._cached_label_radius:
            self._label_cache.clear()
            self._cached_label_radius = radius
            self._label_font = pygame.font.Font(self.theme.label_font, max(1, round(radius*self.theme.label_size)))
 
        sprite = self._label_cache.get((text, rgb))
        if sprite == None:
            image = self._label_font.render(text, True, rgb)
            sprite = image.subsurface(image.get_bounding_rect()).copy()
            self._label_cache[(text, rgb)] = sprite
        return sprite

    def make_base_sprite(self, size: tuple[int, int]) -> pygame.Surface:
        layout, theme = self.layout, self.theme
        key = (size, tuple(layout.rect))
        if key != self._cached_base_key:
            self._base = None
            self._cached_base_key = key
 
        if self._base == None:
            base = pygame.Surface(size)
            if self._surround_tile != None:
                tile = self._surround_tile
                for x in range(0, size[0], tile.get_width()):
                    for y in range(0, size[1], tile.get_height()):
                        base.blit(tile, (x, y))
                pygame.draw.rect(base, theme.background_rgb, layout.rect)
            else:
                base.fill(theme.background_rgb)
            if theme.background_image != None:
                background = pygame.image.load_sized_svg(theme.background_image, layout.rect.size)
                base.blit(background, background.get_rect(center=layout.rect.center))
            self._base = base
        return self._base

    def make_clear_mask(self, radius: float) -> pygame.Surface:
        if radius != self._cached_clear_radius:
            self._clear_cache.clear()
            self._cached_clear_radius = radius
 
        sprite = self._clear_cache.get(radius)
        if sprite == None:
            size = int(radius*2) + 1
            ss_size = size*SUPERSAMPLE
            big = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
            big.fill((255, 255, 255, 0)) 
            pygame.draw.circle(big, (255, 255, 255, 255), (ss_size/2, ss_size/2), radius*SUPERSAMPLE)
            sprite = pygame.transform.smoothscale(big, (size, size))
            self._clear_cache[radius] = sprite
        return sprite

    def clear_point(self, surface: pygame.Surface, base: pygame.Surface, center: tuple[float, float], radius: float):
        mask = self.make_clear_mask(radius)
        area = mask.get_rect(center=center)
        patch = pygame.Surface(area.size, pygame.SRCALPHA)
        patch.blit(base, (0, 0), area)
        patch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(patch, area)

    def settle_neighbors(self, point: Point) -> dict[Point, tuple[float, float]]:
        shift_x, shift_y = self._shifts[(point, self.board.get(point))]
        moved: dict[Point, tuple[float, float]] = {}
        for neighbor in self.board.neighbors(point):
            key = (neighbor, self.board.get(neighbor))
            if key not in self._shifts:
                continue
            old_x, old_y = self._shifts[key]
            dx, dy = neighbor.x - point.x, neighbor.y - point.y
            new_x = shift_x - dx if (shift_x - old_x)*dx > 1 else old_x
            new_y = shift_y - dy if (shift_y - old_y)*dy > 1 else old_y
            if (new_x, new_y) != (old_x, old_y):
                self._shifts[key] = (new_x, new_y)
                moved[neighbor] = (old_x, old_y)
        return moved

    def stone_pixel(self, point: Point) -> tuple[float, float]:
        x, y = self.layout.to_pixel(point)
        shift = self._shifts.get((point, self.board.get(point)))
        if shift == None: 
            return (x, y)
        dx, dy = self.shift_offset(shift)
        slide = self._slides.get(point)
        if slide != None:
            (start_x, start_y), start = slide
            def ease_out(t: float) -> float:
                return 1 - (1 - t)**3
            t = ease_out(min(1, (pygame.time.get_ticks() - start) / max(1, self.theme.slide_ms)))
            dx, dy = start_x + (dx - start_x)*t, start_y + (dy - start_y)*t
        return (x + int(dx), y + int(dy))

def star_points(size: int = 19) -> list[Point]:
    """
    Note: My idea is:
    corners and size only for > 7
    shift corners down to 3-3 from < size 12
    sides only from odd >= size 15
    tengen only for odd sizes except 1

    Might change later, the one in 'Sabaki' has sides at like 13x13 but in my go experience, that's not common and it doesn't look that good
    """
    _star_points = []
    
    if size > 7:
        from_corner = 2 if size < 12 else 3
        far_corner = size - from_corner - 1

        #side
        if size % 2 == 1 and size >= 15:
            mid = size // 2
            for point in [Point(mid, from_corner), Point(from_corner, mid), Point(mid, far_corner), Point(far_corner, mid)]:
                _star_points.append(point)

        #corner
        for point in [Point(from_corner, from_corner), Point(from_corner, far_corner), Point(far_corner, from_corner), Point(far_corner, far_corner)]:
            _star_points.append(point)

    if size % 2 == 1 and size > 1: # tengen
        _star_points.append(Point(size // 2, size // 2))
    return _star_points

def triangle_points(center: tuple[float, float], radius: float) -> list[tuple[float, float]]: 
    x, y = center
    half_base = radius * 3**0.5 / 2
    return [(x, y - radius), (x + half_base, y + radius/2), (x - half_base, y + radius/2)]

# board = Board(19)
# board.set(Point(0,0), Color.BLACK)
# board.set(Point(2,2), Color.WHITE)
# BoardRenderer().draw_ascii(board)
