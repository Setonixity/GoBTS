# Architecture

The project is designed loosely according Object Oriented Programming (OOP) principles.
```
GOBTS/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── ARCHITECTURE.md
├── data/gobts/
|   └── images/
|   └── sgf/
└── src/gobts/
    └── client/
    └── core/
    └── server/
    └── sgf/
```
sgf/parser - parses the syntax into a tree of nodes
sgf/converter - convert nodes into positions on the board

## Conventions
In Go, the convention for [board coordinates](https://senseis.xmp.net/?Coordinates) is symmetrical from all sides, ex 4-4 can refer to any of the four corner star points in a 19x19 board.
With respect to the code, the board coordinates are not symmetrical and instead zero-indexed numbered (x, y).

For SGF parsing, the code follows this [naming convention](https://homepages.cwi.nl/~aeb/go/misc/sgf.html).

## Solution Credits
- gfxdraw circle aliasing: [supersampling](https://www.reddit.com/r/pygame/comments/uuqlh1/comment/i9hjkkr/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button) 
- pygame toolbar: [self-made module](https://stackoverflow.com/questions/24970676/creating-a-toolbar-in-pygame-window) and [creating menus](https://pygame-menu.readthedocs.io/en/4.0.1/_source/create_menu.html)
- smooth redraw window resizing: [pygame](https://www.pygame.org/wiki/WindowResizing)
- sgf parsing: (referenced repos) [go-sgf](https://github.com/bhaskarb/go-sgf) [anki-sgf](https://bitbucket.org/mkmatlock/ankisgf/src/master/) (documentation) [red-bean](https://www.red-bean.com/sgf/sgf4.html)
- tkinter dialog: [pythontutorial](https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/) [tutorialspoint](https://www.tutorialspoint.com/article/how-to-use-tkinter-filedialog-without-a-window)
- pygame SDL and tkinter on Linux: [github issue](https://github.com/pygame/pygame/issues/1995)
- keep pygame responsive: [riptutorial](https://riptutorial.com/pygame/example/18046/event-loop)
- lru cache safeguard: [reddit](https://www.reddit.com/r/pygame/comments/10kgugs/looking_for_tips_on_how_to_optimize_my_pygame/)
- fix supersampling gamma-average: [ericbasseur](https://www.ericbrasseur.org/gamma.html?i=1)