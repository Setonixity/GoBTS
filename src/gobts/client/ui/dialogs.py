from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, TypeVar

import pygame

SGF_TYPES = [("SGF files", ("*.sgf", "*.SGF")), ("All files", "*")]
KEEP_APP_ALIVE_MS = 100

T = TypeVar("T")

def ask_open_path(title: str = "Open", filetypes=SGF_TYPES) -> str|None:
    path = run(lambda root: filedialog.askopenfilename(parent=root, title=title, filetypes=filetypes))
    return path if path else None

def ask_save_path(title: str = "Save", filetypes=SGF_TYPES) -> str|None:
    path = run(lambda root: filedialog.asksaveasfilename(parent=root, title=title, filetypes=filetypes, defaultextension=".sgf"))
    return path if path else None

def run(dialog_func: Callable[[tk.Tk], T]) -> T: # always destroy the root afterwards
    root = tk.Tk()
    root.withdraw()
    if pygame.display.get_init():
        root.after(KEEP_APP_ALIVE_MS, keep_app_alive, root)
    try:
        return dialog_func(root)
    finally:
        root.destroy()
        if pygame.display.get_init():
            pygame.event.clear((pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)) # clear clicks on board

def keep_app_alive(root: tk.Tk):
    pygame.event.pump()
    root.after(KEEP_APP_ALIVE_MS, keep_app_alive, root)

def show_error(title: str, message:str) -> None:
    run(lambda root: messagebox.showerror(title, message, parent=root))

def open_folder(path: Path) -> None: # in the os file manager
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path], env=system_env())

def system_env() -> dict[str, str]:
    env = dict(os.environ)
    if getattr(sys, "frozen", False): 
        original = env.pop("LD_LIBRARY_PATH_ORIG", None)
        if original != None:
            env["LD_LIBRARY_PATH"] = original
        else:
            env.pop("LD_LIBRARY_PATH", None)
    return env