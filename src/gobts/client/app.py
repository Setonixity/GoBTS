from __future__ import annotations

from gobts.client.board import *
from gobts.client.tree.layout import TreeLayout
from gobts.client.tree.renderer import TreeRenderer
from gobts.client.ui import *
from gobts.core import *

import gobts.sgf.converter as converter
from gobts.sgf.node import SGFNode
import gobts.sgf.parser as parser
import pygame

WINDOW_TITLE = "GO TO FUCKING SLEEP"
TREE_WIDTH = 240
WINDOW_SIZE = (800 + TREE_WIDTH, 822)
FPS = 60

REDRAW_EVENTS = {pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED, pygame.WINDOWEXPOSED, pygame.MOUSEMOTION}

class ClientApp:
    def __init__(self, size: int = 19):
        self.size = size
        self.board = Board(size)
        self.root = SGFNode()
        self.node = self.root
        # node = list(parser.load("data/gobts/sgf/test_1.sgf")[0].main_line())[-1]
        # self.board = converter.board_at(node)
        self.color_to_play = Color.BLACK

    def run(self):
        pygame.init()
        pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        pygame.display.set_caption(WINDOW_TITLE)

        self.layout_size = None
        font = pygame.font.SysFont("ubuntu,segoeui,dejavusans,arial", 13)
        self.menubar = MenuBar([
            Menu("File", [
                MenuItem("New Game", self.new_game),
                MenuItem("Open Game", self.open_game)
            ]),
            Menu("Edit", [
                MenuItem("Copy", lambda: print('TEST'))
            ])
        ], font)
        self.ui_renderer = UIRenderer(self.menubar, font)
        bar_h = self.menubar.layout.height

        self.b_renderer = BoardRenderer(self.board, BoardLayout.fit(self.size, WINDOW_SIZE[0] - TREE_WIDTH, WINDOW_SIZE[1] - bar_h, top=bar_h))
        self.t_renderer = TreeRenderer(TreeLayout.fit(self.root, self.node, pygame.Rect(WINDOW_SIZE[0] - TREE_WIDTH, bar_h, TREE_WIDTH, WINDOW_SIZE[1] - bar_h)))

        running = True
        needs_redraw = True
        while running:
            if not needs_redraw:
                events = [pygame.event.wait(), *pygame.event.get()]
            else:
                events = pygame.event.get()

            for event in events:
                if self.menubar.handle_event(event):
                    needs_redraw = True
                    continue
                if event.type == pygame.QUIT:
                    running = False
                elif event.type in REDRAW_EVENTS:
                    needs_redraw = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.on_click(self.b_renderer.layout.to_point(*event.pos))
                    needs_redraw = True

            if needs_redraw:
                screen = pygame.display.get_surface()
                if screen.get_size() != self.layout_size:
                    self.layout_size = screen.get_size()
                    self.b_renderer.layout = BoardLayout.fit(self.size, self.layout_size[0] - TREE_WIDTH, self.layout_size[1] - bar_h, top=bar_h)
                    self.t_renderer.layout = TreeLayout.fit(self.root, self.node, pygame.Rect(self.layout_size[0] - TREE_WIDTH, bar_h, TREE_WIDTH, self.layout_size[1] - bar_h))
                ghost_preview = None
                if pygame.mouse.get_focused():
                    point = self.b_renderer.layout.to_point(*pygame.mouse.get_pos())
                    if point != None:
                        ghost_preview = (point, self.color_to_play)
                self.b_renderer.draw(screen, ghost_preview)
                self.t_renderer.draw(screen)
                self.ui_renderer.draw(screen)
                pygame.display.flip()
                needs_redraw = False
            
        pygame.quit()

    def on_click(self, point: Point|None):
        if point == None or not self.board.is_empty(point):
            return
        play(self.board, point, self.color_to_play)
        self.color_to_play = self.color_to_play.switch()
    
    def open_game(self):
        path = dialogs.ask_open_path("Open Game")
        if path == None:
            return
        try:
            root = parser.load(path)[0]
            node = list(root.main_line())[-1]
            board = converter.board_at(node)
            self.board = board
            self.size = board.size
            self.color_to_play = Color.WHITE if "B" in node else Color.BLACK
            self.b_renderer.board = board
            self.root, self.node = root, node
            self.layout_size = None
        except:
            dialogs.show_error("Could not open file", f"{path}")

    def new_game(self):
        self.board.clear()
        self.color_to_play = Color.BLACK
        self.root = SGFNode()
        self.node = self.root
        self.layout_size = None


ClientApp().run()
