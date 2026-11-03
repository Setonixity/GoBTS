from __future__ import annotations

from pathlib import Path
import re

from gobts.sgf.node import SGFNode

def load(path: str | Path) -> list[SGFNode]:
    return parse(Path(path).read_text())

def parse(text: str) -> list[SGFNode]:
    return Parser(text).parse()

WHITESPACE = re.compile(r"\s*")

class Parser:

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def parse(self) -> list[SGFNode]:
        text = self.text
        roots: list[SGFNode] = []
        branch_points: list[SGFNode|None] = []
        current: SGFNode|None = None

        while True:
            if not branch_points:
                match = re.search(r"\(\s*;", text, self.pos)
                if match is None:
                    break
                self.pos = match.start()
                # print(self.pos)
            
            """(;C[root] (;C[a];C[b] (;C[c]) (;C[d];C[e]) ) )
            - ( starts a subtree, so save the preceding node as a branch point we will go back to once it closes with ), another ( right away would make the next node a second child of the branch point.
            """
            char = text[self.pos]
            if char == "(":
                branch_points.append(current)
                self.pos = WHITESPACE.match(text, self.pos + 1).end()
            elif char == ")":
                current = branch_points.pop()
                self.pos += 1
            elif char == ";":
                node = SGFNode(parent=current)
                if current == None:
                    roots.append(node)
                else:
                    current.children.append(node)
                current = node
                self.pos += 1
            # elif char.isascii() and char.isalpha():
                
    def read_id(self) -> str:
        name = re.match(r"[A-Za-z]+", self.text, self.pos).group()
        self.pos += len(name)
        return "".join(c for c in name if c.isupper())

    def read_value(self) -> str:
        self.pos += 1
        parts = []
        while True:
            # handle \] as literal
            match = re.search(r"[\]\\]", self.text, self.pos)
            parts.append(self.text[self.pos:match.start()])
            if match.group() == "]":
                self.pos = match.end()
                return "".join(parts)
            escaped = self.text[match.end():match.end() + 1]
            if escaped != "\n":
                parts.append(escaped)
            self.pos = match.end() + 1

    def read_values(self, id: str) -> list[str]:
        values = []
        self.pos = WHITESPACE.match(self.text, self.pos).end()
        while self.text.startswitch("[", self.pos):
            values.append(self.read_value())


parse('(;C[root](;C[a];C[b](;C[c])(;C[d];C[e])))')

    