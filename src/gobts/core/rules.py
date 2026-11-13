from __future__ import annotations

from gobts.core.board import *

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
                to_check.append(neighbor)
            elif board.get(neighbor) == None:
                liberties.add(neighbor)
    return (group, liberties)

def is_legal(board: Board, point: Point, color: Color) -> bool:
    if not board.contains(point) or not board.is_empty(point) or point == board.ko:
        return False
    for neighbor in board.neighbors(point):
        neighbor_color = board.get(neighbor)
        if neighbor_color == None:
            return True
        _, liberties = group_and_liberties(board, neighbor)
        if neighbor_color == color and liberties != {point}:
            return True
        if neighbor_color != color and liberties == {point}:
            return True
    return False

def play(board:Board, point: Point, color: Color):
    board.set(point, color)

    captured: set[Point] = set()
    for neighbor in board.neighbors(point):
        if board.get(neighbor) == color.switch():
            group, liberties = group_and_liberties(board, neighbor)
            if not liberties:
                for stone in group:
                    board.set(stone, None) 
                captured |= group
    board.captures[color] += len(captured)

    group, liberties = group_and_liberties(board, point)
    if not liberties:
        for stone in group:
            board.set(stone, None)
        board.captures[color.switch()] += len(group)

    is_ko = len(captured) == 1 and len(group) == 1 and len(liberties) == 1
    board.ko = list(captured)[0] if is_ko else None
    return captured

# board = Board()
# board.set(Point(3,3), Color.WHITE)
# BoardRenderer().draw_ascii(board)
# while True:
#     _play = input()
#     _point = Point(int(_play[0]), int(_play[1]))
#     play(board, _point, Color.BLACK)
#     BoardRenderer().draw_ascii(board)
