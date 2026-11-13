from __future__ import annotations

from gobts.core.board import Board, Color, Marker, Point, Label
from gobts.core.rules import play
from gobts.sgf.node import SGFNode

COORDS_LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
LABEL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
SETUP = {"AB": Color.BLACK, "AW": Color.WHITE, "AE": None}
MOVES = {"B": Color.BLACK, "W": Color.WHITE}
LABEL = "LB"

def board_size(root: SGFNode) -> int:
    value = root.get("SZ")[0] if root.get("SZ") else str(19)
    cols, _, _ = value.partition(":") # "19" or "19:19"
    size = int(cols)
    return size

def komi(root: SGFNode) -> float:
    value = root.get("KM")[0] if root.get("KM") else "6.5"
    try:
        return float(value)
    except ValueError:
        return 6.5

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

def is_pass(node: SGFNode, color: Color, size: int) -> bool:
    values = node.get(color.value)
    return bool(values) and parse_point(values[0], size) == None

def toggle_setup_stone(node: SGFNode, point: Point, color: Color, size: int) -> None:
    before = board_at(node.parent) if node.parent != None else Board(size)
    target = None if board_at(node).get(point) == color else color
    setup = {id: [p for p in parse_points(node.get(id), size) if p != point] for id in SETUP}
    if target != before.get(point): 
        id = next(id for id, c in SETUP.items() if c == target)
        setup[id].append(point)
    for id, points in setup.items():
        if points:
            node.properties[id] = [format_point(p) for p in points]
        else:
            node.properties.pop(id, None)

def markers_at(node: SGFNode, size: int) -> dict[Point, Marker]: 
    markers: dict[Point, Marker] = {}
    for marker in Marker:
        for point in parse_points(node.get(marker.value), size):
            if 0 <= point.x < size and 0 <= point.y < size:
                markers[point] = marker
    return markers

def toggle_marker(node: SGFNode, point: Point, marker: Marker, size: int) -> None:
    markers = markers_at(node, size)
    if markers.get(point) == marker:
        del markers[point]
    else:
        markers[point] = marker
        labels = labels_at(node, size)
        if labels.pop(point, None) != None:
            set_labels(node, labels)
    for kind in Marker:
        values = [format_point(p) for p, m in markers.items() if m == kind]
        if values:
            node.properties[kind.value] = values
        else:
            node.properties.pop(kind.value, None)

def labels_at(node: SGFNode, size: int) -> dict[Point, str]:
    labels: dict[Point, str] = {}
    for value in node.get(LABEL):
        coord, _, text = value.partition(":") # "dd:A"
        point = parse_point(coord, size)
        if point != None and 0 <= point.x < size and 0 <= point.y < size:
            labels[point] = text
    return labels

def set_labels(node: SGFNode, labels: dict[Point, str]) -> None:
    values = [format_point(p) + ":" + text for p, text in labels.items()]
    if values:
        node.properties[LABEL] = values
    else:
        node.properties.pop(LABEL, None)
 
def label_kind(text: str) -> Label|None:
    if len(text) == 1 and text in LABEL_LETTERS:
        return Label.LETTER
    if text.isascii() and text.isdigit():
        return Label.NUMBER
    return None

def next_label(labels: dict[Point, str], label: Label) -> str|None:
    taken = {text for text in labels.values() if label_kind(text) == label}
    if label == Label.NUMBER:
        number = len(taken) + 1
        while str(number) in taken:
            number += 1
        return str(number)
    return next((c for c in LABEL_LETTERS[len(taken):] if c not in taken), None)

def toggle_label(node: SGFNode, point: Point, label: Label, size: int) -> None:
    labels = labels_at(node, size)
    if point in labels and label_kind(labels[point]) == label:
        del labels[point]
    else:
        labels.pop(point, None) 
        text = next_label(labels, label)
        if text == None: 
            return
        labels[point] = text
        marker = markers_at(node, size).get(point)
        if marker != None: 
            toggle_marker(node, point, marker, size)
    set_labels(node, labels)

def next_color(node: SGFNode) -> Color: 
    current: SGFNode|None = node
    while current != None:
        if "B" in current:
            return Color.WHITE
        if "W" in current:
            return Color.BLACK
        current = current.parent
    return Color.BLACK