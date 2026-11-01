from __future__ import annotations

from gobts.client.board.renderer import BoardRenderer
from gobts.core import *

def group_and_liberties(board: Board, point: Point) -> tuple[set[Point], set[Point]]:
    color = board.get(point)
    group: set[Point] = set()
    liberties: set[Point] = set()
    to_check = [point]
    while to_check:
        current = to_check.pop()
        if current in group:
            continue
        group.add(current)
        for neighbor in board.neighbors(current):
            if board.get(neighbor) == color:
                to_check.add(neighbor)
            elif board.get(neighbor) == None:
                liberties.add(neighbor)
    return (group, liberties)

def play(board:Board, point: Point, color: Color):
    board.set(point, color)

    for neighbor in board.neighbors(point):
        if board.get(neighbor) == color.switch():
            group, liberties = group_and_liberties(board, neighbor)
            print(group, liberties)
            if not liberties:
                for captured in group:
                    board.set(captured, None) 

# board = Board()
# board.set(Point(3,3), Color.WHITE)
# BoardRenderer().draw_ascii(board)
# while True:
#     _play = input()
#     _point = Point(int(_play[0]), int(_play[1]))
#     play(board, _point, Color.BLACK)
#     BoardRenderer().draw_ascii(board)
