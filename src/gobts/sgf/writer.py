from __future__ import annotations

from pathlib import Path
import re

from gobts.sgf.node import SGFNode

def save(root: SGFNode, path: str|Path) -> None:
    Path(path).write_text(serialize(root))

def serialize(root: SGFNode) -> str:
    parts: list[str] = []
    to_write: list[SGFNode|None] = [root]
    while to_write:
        node = to_write.pop()
        if node == None:
            parts.append(")")
            continue
        sequence = [node]
        while len(sequence[-1].children) == 1:
            sequence.append(sequence[-1].children[0])
        parts.append("(" + "".join(write_node(step) for step in sequence))
        to_write.append(None)
        to_write.extend(reversed(sequence[-1].children))
    return "".join(parts) + "\n"

NEEDS_ESCAPE = re.compile(r"[\]\\]")

def write_node(node: SGFNode) -> str:
    text = ";"
    for id, values in node.properties.items():
        text += id + "".join("[" + NEEDS_ESCAPE.sub(r"\\\g<0>", value) + "]" for value in values)
    return text