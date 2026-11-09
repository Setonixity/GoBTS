from __future__ import annotations

from gobts.core.board import Board, Color, Marker, Point
from gobts.core.rules import play
from gobts.sgf.node import SGFNode

COORDS_LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
SETUP = {"AB": Color.BLACK, "AW": Color.WHITE, "AE": None}
MOVES = {"B": Color.BLACK, "W": Color.WHITE}

def board_size(root: SGFNode) -> int:
    value = root.get("SZ")[0] if root.get("SZ") else str(19)
    cols, _, _ = value.partition(":") # "19" or "19:19"
    size = int(cols)
    return size

def apply_node(board: Board, node:SGFNode) -> None:
    if any(id in node for id in SETUP):
        board.ko = None
    for id, color in SETUP.items():
        for point in parse_points(node.get(id), board.size):
            board.set(point, color)
    for id, color in MOVES.items():
        if id in node:
            point = parse_point(node.get(id)[0], board.size)
            if point != None:
                play(board, point, color)
            else: # pass
                board.ko = None

def parse_point(value: str, size: int) -> Point|None:
    value = value.strip()
    if value == "" or (value == "tt" and size <= 19): #B[] or B[tt] is pass
        return None
    x, y = COORDS_LETTERS.find(value[0]), COORDS_LETTERS.find(value[1])
    return Point(x, y)

def parse_points(values: list[str], size: int) -> list[Point]:
    points = []
    for value in values:
        if ":" in value:
            first, last = (parse_point(corner, size) for corner in value.split(':', maxsplit=1))
            for y in range(min(first.y, last.y), max(first.y, last.y) + 1):
                for x in range(min(first.x, last.x), max(first.x, last.x) + 1):
                    points.append(Point(x, y))
        else:
            point = parse_point(value, size)
            if point != None:
                points.append(point)
    return points

def board_at(node: SGFNode) -> Board: # check FROM current node 
    tree_path: list[SGFNode] = []
    current: SGFNode | None = node
    while current != None:
        tree_path.append(current)
        current = current.parent
    tree_path.reverse() 

    root = tree_path[0]
    board = Board(board_size(root))
    for step in tree_path:
        apply_node(board, step)
    return board

def format_point(point: Point) -> str:
    return COORDS_LETTERS[point.x] + COORDS_LETTERS[point.y]

def markers_at(node: SGFNode, size: int) -> dict[Point, Marker]: 
    markers: dict[Point, Marker] = {}
    for marker in Marker:
        for point in parse_points(node.get(marker.value), size):
            if 0 <= point.x < size and 0 <= point.y < size:
                markers[point] = marker
    return markers

def set_marker(node: SGFNode, point: Point, marker: Marker|None, size: int) -> None:
    for m in Marker:
        points = parse_points(node.get(m.value), size)
        if (point in points) == (m == marker):
            continue
        points = [p for p in points if p != point] + ([point] if m == marker else [])
        if points:
            node.properties[m.value] = [format_point(p) for p in points]
        else:
            node.properties.pop(m.value, None)
