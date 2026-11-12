from __future__ import annotations

from gobts.client.board import *
from gobts.client.panel.layout import PanelLayout
from gobts.client.panel.renderer import PanelRenderer
from gobts.client.theme import Theme
from gobts.client.toolbar.layout import ToolbarLayout
from gobts.client.toolbar.renderer import ToolbarRenderer
from gobts.client.toolbar.tool import Tool
from gobts.client.tree.layout import TreeLayout
from gobts.client.tree.renderer import TreeRenderer
from gobts.client.ui import *
from gobts.core import *
from gobts.core.board import Label, Marker
from gobts.sgf.node import SGFNode

import gobts.core.rules as rules
import gobts.sgf.converter as converter
import gobts.sgf.parser as parser
import gobts.sgf.writer as writer

import pygame
from pygame._sdl2.video import Window

WINDOW_TITLE = "GO TO FUCKING SLEEP"
TREE_WIDTH = 240
WINDOW_SIZE = (800 + TREE_WIDTH, 822)
FPS = 60

REDRAW_EVENTS = {pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED, pygame.WINDOWEXPOSED, pygame.MOUSEMOTION}

class ClientApp:
    def __init__(self, size: int = 19):
        self.size = size
        self.board = Board(size)
        self.theme_names = Theme.available_themes()
        self.theme_name: str|None = None
        self.theme = self.load_theme(self.theme_name)
        self.show_panel = True
        self.show_tree = True
        self.tool: Tool|None = None
        self.new_game()

    def run(self):
        theme = self.theme
        pygame.init()
        self.window = Window(WINDOW_TITLE, WINDOW_SIZE, resizable=True)
        screen = self.window.get_surface()
        pygame.key.set_repeat(300, 50)

        self.layout_size = None
        self.maximized = False
        self.build_ui()

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
                elif event.type == pygame.WINDOWMAXIMIZED:
                    self.maximized = True
                elif event.type == pygame.WINDOWRESTORED:
                    self.maximized = False
                elif event.type in REDRAW_EVENTS:
                    needs_redraw = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    node = self.t_renderer.layout.to_node(*event.pos)
                    tool = self.tb_renderer.layout.to_tool(*event.pos)
                    if node != None:
                        self.go_to(node)
                    elif tool != None:
                        self.tool = None if tool == self.tool else tool
                    elif self.tool == None:
                        self.on_click(self.b_renderer.layout.to_point(*event.pos))
                    else:
                        self.on_edit(self.b_renderer.layout.to_point(*event.pos), self.tool.left)
                    needs_redraw = True
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if self.tool != None:
                        self.on_edit(self.b_renderer.layout.to_point(*event.pos), self.tool.right)
                        needs_redraw = True
                elif event.type == pygame.MOUSEWHEEL:
                    if self.t_renderer.layout.rect.collidepoint(pygame.mouse.get_pos()):
                        self.on_scroll(event.y)
                        needs_redraw = True
                elif event.type == pygame.KEYDOWN:
                    self.on_key(event.key)
                    needs_redraw = True

            if needs_redraw:
                screen = self.window.get_surface()
                if screen.get_size() != self.layout_size:
                    self.layout_size = screen.get_size()
                    self.b_renderer.layout, self.p_renderer.layout, self.t_renderer.layout, self.tb_renderer.layout = self.fit_layouts(self.layout_size)
                ghost_preview = None
                if self.tool == None and pygame.mouse.get_focused():
                    point = self.b_renderer.layout.to_point(*pygame.mouse.get_pos())
                    if point != None and rules.is_legal(self.board, point, self.color_to_play):
                        ghost_preview = (point, self.color_to_play)
                self.b_renderer.draw(screen, converter.markers_at(self.node, self.size), converter.labels_at(self.node, self.size), ghost_preview)
                if self.show_panel:
                    self.p_renderer.draw(screen)
                    if self.show_tree:
                        self.t_renderer.draw(screen, self.node)
                    self.tb_renderer.draw(screen, self.tool)
                self.ui_renderer.draw(screen)
                self.window.flip()
                needs_redraw = False
            
        pygame.quit()

    def on_click(self, point: Point|None, button: int = 1):
        if point == None or not rules.is_legal(self.board, point, self.color_to_play):
            return
        id, value = self.color_to_play.value, converter.format_point(point)
        child = next((child for child in self.node.children if child.get(id) == [value]), None)
        if child == None:
            child = SGFNode({id: [value]}, parent=self.node)
            self.node.children.append(child)
        self.go_to(child)

    def on_key(self, key: int):
        if key == pygame.K_UP and self.node.parent != None:
            self.go_to(self.node.parent)
        elif key == pygame.K_DOWN and self.node.children:
            self.go_to(self.node.children[0])
        elif key in (pygame.K_LEFT, pygame.K_RIGHT):
            step = -1 if key == pygame.K_LEFT else 1
            node = self.t_renderer.layout.row_neighbor(self.node, step)
            if node != None:
                self.go_to(node)

    def on_scroll(self, steps: int):
        node = self.node
        for _ in range(abs(steps)):
            next_node = node.parent if steps > 0 else (node.children[0] if node.children else None)
            if next_node == None:
                break
            node = next_node
        if node is not self.node:
            self.go_to(node)

    def on_edit(self, point: Point|None, edit: Color|Marker):
        if point == None:
            return
        if isinstance(edit, Label):
            converter.toggle_label(self.node, point, edit, self.size)
            return
        if isinstance(edit, Marker):
            converter.toggle_marker(self.node, point, edit, self.size)
            return
        node = self.node
        if "B" in node or "W" in node: 
            node = SGFNode(parent=self.node)
            self.node.children.append(node)
        converter.toggle_setup_stone(node, point, edit, self.size)
        self.go_to(node)


    def go_to(self, node: SGFNode):
        board = converter.board_at(node)
        self.board = board
        self.size = board.size
        self.color_to_play = converter.next_color(node)
        self.b_renderer.board = board
        self.node = node
        self.layout_size = None
    
    def open_game(self):
        path = dialogs.ask_open_path("Open Game")
        if path == None:
            return
        try:
            root = parser.load(path)[0]
            node = list(root.main_line())[-1]
            self.go_to(node)
            self.root= root
            
        except:
            dialogs.show_error("Could not open file", f"{path}")

    def save_game(self, ask_path: bool = False):
        path = self.path
        if ask_path or path == None:
            path = dialogs.ask_save_path("Save Game")
            if path == None:
                return
        try:
            writer.save(self.root, path)
            self.path = path
        except OSError as error:
            dialogs.show_error("Could not save file", f"{path}\n{error}")

    def new_game(self):
        self.board.clear()
        self.color_to_play = Color.BLACK
        self.root = SGFNode({"GM": ["1"], "FF": ["4"], "SZ": [str(self.size)]})
        self.node = self.root
        self.path = None
        self.layout_size = None

    def toggle_panel(self):
        self.show_panel = not self.show_panel
        screen = self.window.get_surface()
        if not (self.maximized or screen.get_flags() & pygame.FULLSCREEN):
            width, height = screen.get_size()
            full_board = height - self.menubar.layout.height
            panel_w = self.theme.panel.width
            if self.show_panel:
                new_width = max(width, min(width, full_board) + panel_w)
            else:
                new_width = min(width, max(width - panel_w, full_board))
            if new_width != width:
                self.window.size = (max(new_width, 1), height)
        self.layout_size = None

    def toggle_tree(self):
        self.show_tree = not self.show_tree
        self.layout_size = None

    def fit_layouts(self, window_size: tuple[int, int]) -> tuple[BoardLayout, PanelLayout, TreeLayout, ToolbarLayout]:
        width, height = window_size
        bar_h = self.menubar.layout.height
        panel_w = self.theme.panel.width if self.show_panel else 0
        board_layout = BoardLayout.fit(self.size, width - panel_w, height - bar_h, self.theme.board, top=bar_h)
        panel_layout = PanelLayout.fit(pygame.Rect(width - panel_w, bar_h, panel_w, height - bar_h), self.show_tree, self.theme.toolbar.height)
        tree_layout = TreeLayout.fit(self.root, self.node, panel_layout.tree_rect, self.theme.tree) 
        toolbar_layout = ToolbarLayout.fit(panel_layout.toolbar_rect, self.theme.toolbar)
        return board_layout, panel_layout, tree_layout, toolbar_layout

    def load_theme(self, name: str|None) -> Theme:
        return Theme() if name == None else Theme.from_dir(name)

    def reload_themes(self):
        self.theme_names = Theme.available_themes()
        if self.theme_name in self.theme_names:
            self.set_theme(self.theme_name)
        else:
            self.build_menubar()

    def set_theme(self, name: str|None):
        previous = (self.theme, self.theme_name)
        try:
            self.theme, self.theme_name = self.load_theme(name), name
            self.build_ui() # also fails on missing fonts/images
        except Exception as error:
            self.theme, self.theme_name = previous
            self.build_ui()
            dialogs.show_error("Could not load theme", f"{name or 'default'}\n{error}")

    def build_menubar(self):
        theme = self.theme
        font = pygame.font.Font(theme.menu.font, theme.menu.font_size)
        self.menubar = MenuBar([
            Menu("File", [
                MenuItem("New Game", self.new_game),
                MenuItem("Open Game", self.open_game),
                MenuItem("Save Game", self.save_game),
                MenuItem("Save Game As", lambda: self.save_game(ask_path=True))
            ]),
            Menu("Edit", [
                MenuItem("Copy", lambda: print('TEST'))
            ]),
            Menu("View", [
                MenuItem("Toggle Side Panel", self.toggle_panel, checked=lambda: self.show_panel),
                MenuItem("Toggle Game Tree", self.toggle_tree, checked=lambda: self.show_tree)
            ]),
            Menu("Themes", [
                MenuItem("Reload Themes Folder", self.reload_themes),
                MenuItem("default", lambda: self.set_theme(None), checked=lambda: self.theme_name == None),
                *(MenuItem(name, lambda name=name: self.set_theme(name), checked=lambda name=name: name == self.theme_name) for name in self.theme_names)
            ])
        ], font, theme.menu)
        self.ui_renderer = UIRenderer(self.menubar, font, theme.menu)

    def build_ui(self):
        theme = self.theme
        self.build_menubar()
        board_layout, panel_layout, tree_layout, toolbar_layout = self.fit_layouts(self.window.get_surface().get_size())
        self.b_renderer = BoardRenderer(self.board, board_layout, theme.board)
        self.p_renderer = PanelRenderer(panel_layout, theme.panel)
        self.t_renderer = TreeRenderer(tree_layout, theme.tree)
        self.tb_renderer = ToolbarRenderer(toolbar_layout, theme.toolbar)
        self.layout_size = None


ClientApp().run()
