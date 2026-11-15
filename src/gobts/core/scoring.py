from __future__ import annotations

from dataclasses import dataclass

from gobts.core.board import Board, Color, Point
import gobts.core.goscorer as goscorer
from gobts.core.rules import group_and_liberties

TO_GOSCORER = {None: goscorer.EMPTY, Color.BLACK: goscorer.BLACK, Color.WHITE: goscorer.WHITE}
FROM_GOSCORER = {goscorer.BLACK: Color.BLACK, goscorer.WHITE: Color.WHITE}

@dataclass
class Score:
    black: float
    white: float
    territory: dict[Point, Color]
    dead: set[Point]

    @property
    def result(self) -> str: # sgf ex. B+3.5
        margin = self.black - self.white
        if margin == 0:
            return "Draw"
        winner = Color.BLACK if margin > 0 else Color.WHITE
        return f"{winner.value}+{abs(margin):g}"

def territory_score(board: Board, komi: float, dead: set[Point]|None = None) -> Score:
    dead = dead or set()
    size = board.size
    stones = [[TO_GOSCORER[board.get(Point(x, y))] for x in range(size)] for y in range(size)]
    marked_dead = [[Point(x, y) in dead for x in range(size)] for y in range(size)]
    scoring = goscorer.territory_scoring(stones, marked_dead)

    territory = {
        Point(x, y): FROM_GOSCORER[loc.is_territory_for]
        for y, row in enumerate(scoring) for x, loc in enumerate(row)
        if loc.is_territory_for in FROM_GOSCORER
    }

    points = {color: board.captures[color] for color in Color}
    for color in territory.values():
        points[color] += 1
    for point in dead:
        stone = board.get(point)
        if stone != None: 
            points[stone.switch()] += 1
    return Score(
        black = points[Color.BLACK],
        white = points[Color.WHITE] + komi,
        territory = territory,
        dead = dead
    )

def toggle_dead(board: Board, dead: set[Point], point: Point) -> set[Point]:
    if board.is_empty(point):
        return set(dead)
    group, _ = group_and_liberties(board, point)
    return dead - group if point in dead else dead | group