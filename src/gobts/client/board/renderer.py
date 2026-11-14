from __future__ import annotations
import math
from pathlib import Path
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
    
        screen_px = max(height for _, height in pygame.display.get_desktop_sizes())
        svg_size = (screen_px, screen_px)
        self.surround_tile = pygame.image.load(theme.surround_texture) if theme.surround_texture != None else None
        self.background_svg = load_svg(theme.background_image, svg_size)
        self._black_svg = load_svg(theme.black_stone_image, svg_size)
        self._white_svg = load_svg(theme.white_stone_image, svg_size)

        self.sprites_radius: int|None = None
        self.stone_sprites: dict[tuple[Color, int], pygame.Surface] = {}
        self.star_sprites: dict[int, pygame.Surface] = {}
        self.marker_sprites: dict[tuple[Marker, RGB, int], pygame.Surface] = {}
        self.label_sprites: dict[tuple[str, RGB, int], pygame.Surface] = {}
        self.label_fonts: dict[int, pygame.font.Font] = {}
        self.clear_masks: dict[int, pygame.Surface] = {}

        self.base_sprite: pygame.Surface|None = None
        self.base_key: tuple|None = None
        self.territory_sprite: pygame.Surface|None = None
        self.territory_key: tuple|None = None

        self._shifts: dict[tuple[Point, Color], tuple[float, float]] = {}
        self._slides: dict[Point, tuple[tuple[float, float], int]] = {}

    @property
    def animating(self) -> bool:
        return bool(self._slides)

    def draw(self, surface: pygame.Surface, markers: dict[Point, Marker], labels: dict[Point, str], ghost_preview: tuple[Point, Color]|None = None, territory: dict[Point, Color]|None = None):
        layout = self.layout
        theme = self.theme
        size = layout.size
        radius = layout.stone_radius
        if radius != self.sprites_radius:
            self.clear_sprites()

        base = self.make_base_sprite(surface.get_size())
        surface.blit(base, (0, 0))

        # grid
        for i in range(size):
            pygame.draw.line(surface, theme.line_rgb, layout.to_pixel(Point(i, 0)), layout.to_pixel(Point(i, size-1)), layout.line_width)
            pygame.draw.line(surface, theme.line_rgb, layout.to_pixel(Point(0, i)), layout.to_pixel(Point(size-1, i)), layout.line_width)
        # star points
        star_radius = max(theme.min_star_radius, round(layout.spacing * theme.star_radius))
        star = self.make_star_sprite(star_radius)
        for point in star_points(size):
            surface.blit(star, star.get_rect(center=self.stone_pixel(point)))
        if territory:
            surface.blit(self.make_territory_sprite(territory), layout.rect)

        self.update_shifts()
        stones = sorted(self.board.stones, key=lambda stone: stone[0] in self._slides)
        for point, color in stones:
            sprite = self.make_stone_sprite(color, radius)
            surface.blit(sprite, sprite.get_rect(center=self.stone_pixel(point)))
        
        annotations = [(point, self.make_marker_sprite(marker, self.annotation_rgb(point), radius)) for point, marker in markers.items()]
        annotations += [(point, self.make_label_sprite(text, self.annotation_rgb(point), radius)) for point, text in labels.items()]
        for point, sprite in annotations:
            center = self.stone_pixel(point)
            if self.board.is_empty(point):
                self.clear_point(surface, base, center, radius*theme.marker_clear)
            surface.blit(sprite, sprite.get_rect(center=center))
            
        if ghost_preview != None:
            point, color = ghost_preview
            if self.board.is_empty(point):
                sprite = self.make_stone_sprite(color, radius).copy()
                sprite.set_alpha(theme.ghost_alpha)
                surface.blit(sprite, sprite.get_rect(center=layout.to_pixel(point)))

    def annotation_rgb(self, point: Point) -> RGB:
        if self.board.get(point) == Color.BLACK:
            return self.theme.marker_on_black_rgb
        return self.theme.marker_rgb

    def clear_sprites(self):
        self.sprites_radius = self.layout.stone_radius
        self.stone_sprites.clear()
        self.star_sprites.clear()
        self.marker_sprites.clear()
        self.label_sprites.clear()
        self.label_fonts.clear()
        self.clear_masks.clear()

    def make_base_sprite(self, size: tuple[int, int]) -> pygame.Surface:
        layout, theme = self.layout, self.theme
        key = (size, tuple(layout.rect))
        if key == self.base_key:
            return self.base_sprite
        
        base = pygame.Surface(size)
        if self.surround_tile != None:
            tile = self.surround_tile
            for x in range(0, size[0], tile.get_width()):
                for y in range(0, size[1], tile.get_height()):
                    base.blit(tile, (x, y))
            pygame.draw.rect(base, theme.background_rgb, layout.rect)
        else:
            base.fill(theme.background_rgb)
        if self.background_svg != None:
            background = fit_scale(self.background_svg, layout.rect.size)
            base.blit(background, background.get_rect(center=layout.rect.center))
        
        self.base_sprite, self.base_key = base, key
        return base

    def make_territory_sprite(self, territory: dict[Point, Color]) -> pygame.Surface:
        layout, theme = self.layout, self.theme
        key = (frozenset(territory.items()), tuple(layout.rect))
        if key == self.territory_key:
            return self.territory_sprite

        sprite = pygame.Surface(layout.rect.size, pygame.SRCALPHA)
        half = layout.spacing*theme.territory_size /2
        for point, color in territory.items():
            rgb = theme.black_territory_rgb if color == Color.BLACK else theme.white_territory_rgb
            x = layout.start_x + point.x*layout.spacing - layout.rect.x
            y = layout.start_y + point.y*layout.spacing - layout.rect.y
            left, top = round(x - half), round(y - half)
            sprite.fill((*rgb, theme.territory_alpha), (left, top, round(x + half) - left, round(y + half) - top))

        self.territory_sprite, self.territory_key = sprite, key
        return sprite

    def make_stone_sprite(self, color: Color, radius: int) -> pygame.Surface:
        key = (color, radius)
        if key in self.stone_sprites:
            return self.stone_sprites[key]
 
        theme = self.theme
        big, center = supersample_canvas(radius)
        svg = self._black_svg if color == Color.BLACK else self._white_svg
        if svg != None:
            stone = fit_scale(svg, (radius*2*SUPERSAMPLE, radius*2*SUPERSAMPLE))
            big.blit(stone, stone.get_rect(center=center))
        else:
            fill_rgb = theme.black_rgb if color == Color.BLACK else theme.white_rgb
            edge = max(1, radius*theme.stone_edge) * SUPERSAMPLE
            pygame.draw.circle(big, theme.stone_edge_rgb, center, radius*SUPERSAMPLE)
            pygame.draw.circle(big, fill_rgb, center, radius*SUPERSAMPLE - edge)

        sprite = downsample(big)
        self.stone_sprites[key] = sprite
        return sprite

    def make_star_sprite(self, radius: int) -> pygame.Surface:
        if radius in self.star_sprites:
            return self.star_sprites[radius]
 
        big, center = supersample_canvas(radius)
        pygame.draw.circle(big, self.theme.star_rgb, center, radius*SUPERSAMPLE)
 
        sprite = downsample(big)
        self.star_sprites[radius] = sprite
        return sprite

    def make_marker_sprite(self, marker: Marker, rgb: RGB, radius: int) -> pygame.Surface:
        key = (marker, rgb, radius)
        if key in self.marker_sprites:
            return self.marker_sprites[key]

        theme = self.theme
        big, center = supersample_canvas(radius, blend_rgb=rgb)
        reach = radius*theme.marker_size*SUPERSAMPLE
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

        sprite = downsample(big)
        self.marker_sprites[key] = sprite
        return sprite

    def make_label_sprite(self, text: str, rgb: RGB, radius: int) -> pygame.Surface:
        key = (text, rgb, radius)
        if key in self.label_sprites:
            return self.label_sprites[key]

        font_size = max(1, round(radius*self.theme.label_size))
        if font_size not in self.label_fonts:
            self.label_sprites[font_size] = pygame.font.Font(self.theme.label_font, font_size)
        image = self.label_fonts[font_size].render(text, True, rgb)

        sprite = image.subsurface(image.get_bounding_rect()).copy()
        self.label_sprites[key] = sprite
        return sprite

    def make_clear_mask(self, radius: float) -> pygame.Surface:
        if radius in self.clear_masks:
            return self.clear_masks[radius]
        
        big, center = supersample_canvas(radius, blend_rgb=(255, 255, 255))
        pygame.draw.circle(big, (255, 255, 255, 255), center, radius*SUPERSAMPLE)

        sprite = downsample(big)
        self.clear_masks[radius] = sprite
        return sprite

    def clear_point(self, surface: pygame.Surface, base: pygame.Surface, center: tuple[float, float], radius: float):
        mask = self.make_clear_mask(radius)
        area = mask.get_rect(center=center)
        patch = pygame.Surface(area.size, pygame.SRCALPHA)
        patch.blit(base, (0, 0), area)
        patch.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(patch, area)

    def update_shifts(self):
        theme = self.theme
        now = pygame.time.get_ticks()
        stones = set(self.board.stones)
        self._shifts = {stone: shift for stone, shift in self._shifts.items() if stone in stones}
        self._slides = {point: slide for point, slide in self._slides.items() if now - slide[1] < theme.slide_ms}

        placed = stones - set(self._shifts)
        for point, color in placed:
            self._shifts[(point, color)] = (random.uniform(-1, 1), random.uniform(-1, 1))
            moved = self.settle_neighbors(point)
            if len(placed) == 1:
                angle = random.uniform(0, 2*math.pi)
                distance = theme.stone_slide*self.layout.spacing
                end_x, end_y = self.shift_offset(self._shifts[(point, color)])
                self._slides[point] = ((end_x + distance*math.cos(angle), end_y + distance*math.sin(angle)), now)
                for neighbor, old in moved.items():
                    self._slides[neighbor] = (self.shift_offset(old), now)

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
    
    def shift_offset(self, shift: tuple[float, float]) -> tuple[float, float]:
        layout, theme = self.layout, self.theme
        stone_radius = layout.stone_radius*theme.stone_image_fill
        reach = max(0, int(layout.spacing) - 2*stone_radius) * theme.stone_shift
        return (shift[0]*reach, shift[1]*reach)

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

def star_points(size: int = 19) -> list[Point]:
    points: list[Point] = []
    
    if size > 7:
        from_corner = 2 if size < 12 else 3
        far_corner = size - from_corner - 1

        #side
        if size % 2 == 1 and size >= 15:
            mid = size // 2
            for point in [Point(mid, from_corner), Point(from_corner, mid), Point(mid, far_corner), Point(far_corner, mid)]:
                points.append(point)

        #corner
        for point in [Point(from_corner, from_corner), Point(from_corner, far_corner), Point(far_corner, from_corner), Point(far_corner, far_corner)]:
            points.append(point)

    if size % 2 == 1 and size > 1: # tengen
        points.append(Point(size // 2, size // 2))
    return points

def triangle_points(center: tuple[float, float], radius: float) -> list[tuple[float, float]]: 
    x, y = center
    half_base = radius * 3**0.5 / 2
    return [(x, y - radius), (x + half_base, y + radius/2), (x - half_base, y + radius/2)]

def fit_scale(surface: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    return pygame.transform.smoothscale(surface, surface.get_rect().fit((0, 0, *size)).size)

def load_svg(path: str|Path|None, size: tuple[int, int]) -> pygame.Surface|None:
    if path == None:
        return None
    return pygame.image.load_sized_svg(path, size).convert_alpha()

def supersample_canvas(radius: float, blend_rgb: RGB = (0, 0, 0)) -> tuple[pygame.Surface, tuple[float, float]]:
    size = (int(radius*2) + 1) * SUPERSAMPLE
    big = pygame.Surface((size, size), pygame.SRCALPHA)
    big.fill((*blend_rgb, 0))
    return big, (size/2, size/2)
 
def downsample(big: pygame.Surface) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (big.get_width() // SUPERSAMPLE, big.get_height() // SUPERSAMPLE))

# board = Board(19)
# board.set(Point(0,0), Color.BLACK)
# board.set(Point(2,2), Color.WHITE)
# BoardRenderer().draw_ascii(board)
