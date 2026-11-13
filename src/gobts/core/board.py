from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterator

class Color(Enum):
    BLACK = 'B'
    WHITE = 'W'

    def switch(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

class Marker(Enum):
    TRIANGLE = 'TR' 
    CROSS = 'MA'
    CIRCLE = 'CR'
    SQUARE = 'SQ'

class Label(Enum): #LB
    LETTER = 'A'
    NUMBER = '1'

@dataclass(frozen=True)
class Point: # starts from (0, 0) which is 1-1 in go
    x: int 
    y: int 

    def __iter__(self):
        yield self.x
        yield self.y

class Board():

    def __init__(self, size: int = 19):
        self.size = size
        self._grid: list[list[Color|None]] = [[None]*self.size for _ in range(self.size)]
        self.ko: Point|None = None
        self.captures: dict[Color, int] = {Color.BLACK: 0, Color.WHITE: 0}

    def get(self, point: Point) -> Color|None:
        return self._grid[point.y][point.x]

    def set(self, point: Point, color: Color|None):
        self._grid[point.y][point.x] = color

    def contains(self, point: Point) -> bool:
        x, y = point
        return 0 <= x < self.size and 0 <= y < self.size

    def is_empty(self, point: Point) -> bool:
        return self.get(point) == None

    def clear(self):
        for y, row in enumerate(self._grid):
            for x, _ in enumerate(row):
                self.set(Point(x, y), None)
        self.captures = {Color.BLACK: 0, Color.WHITE: 0}

    @property
    def stones(self) -> Iterator[Point, Color]:
        for y, row in enumerate(self._grid):
            for x, color in enumerate(row):
                if color:
                    yield Point(x, y), color

    def neighbors(self, point: Point) -> Iterator[Point]:
        x, y = point
        for neighbor in [Point(x-1, y), Point(x+1, y), Point(x, y-1), Point(x, y+1)]:
            if self.contains(neighbor):
                yield neighbor

# print(Point(1, 2))
# print(Color.BLACK.switch())
# print("\n".join("".join('+' for item in row) for row in Board()._grid))
# board = Board(9)
# board.set(Point(0,0), Color.BLACK)
# print(board.get(Point(0,0)))
# print(list(board.stones))