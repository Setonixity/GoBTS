"""
FF[4] syntax (https://www.red-bean.com/sgf/sgf4.html):

    Collection = GameTree { GameTree }
    GameTree   = "(" Sequence { GameTree } ")"
    Sequence   = Node { Node }
    Node       = ";" { Property }
    Property   = PropIdent PropValue { PropValue }
    PropIdent  = UcLetter { UcLetter }
    PropValue  = "[" CValueType "]"
    CValueType = (ValueType | Compose)
    ValueType  = (None | Number | Real | Double | Color | SimpleText |
                Text | Point  | Move | Stone)

Chain of nodes (https://www.red-bean.com/sgf/images/ta3.gif):
    (;FF[4]C[root](;C[a];C[b](;C[c])
    (;C[d];C[e]))
    (;C[f](;C[g];C[h];C[i])
    (;C[j])))
A node starts with ';' and is one step in the record. The first node is the root.
Properties are uppercase ids with a bracketed value(s): AB[dd][pp].
() evalopes a game tree, can be nested () as a branch. The first being the mainline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterator

@dataclass(eq=False)
class SGFNode:
    properties: dict[str, list[str]] = field(default_factory=dict)
    parent: SGFNode|None = field(default=None, repr=False)
    children: list[SGFNode] = field(default_factory=list, repr=True)

    def get(self, id: str) -> list[str]:
        return list(self.properties.get(id, []))

    def __contains__(self, id: str) -> bool:
        return id in self.properties

    def main_line(self) -> Iterator[SGFNode]:
        node: SGFNode|None = self
        while node != None:
            yield node
            node = node.children[0] if node.children else None