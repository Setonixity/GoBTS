# Changelog

## [0.0.1] - 2-11-2026
### Added
- setup project structure
- README, CHANGELOG, and ARCHITECTURE
- (core) shared board library
- (core) shared rules library
- (client) ascii board rendering
- (client) pygame board rendering
- (client) mouse input and stone placement
- (client) stone ghost previews

### Fixed
- (client) jitter during window resizing
- (client) inconsistent star point scaling

## [0.0.2] - 4-11-2026
### Added
- (client) working menubar
- (client) dropdown box, and callable menuitems
- (sgf) dataclass for sgf nodes
- (sgf) parser for sgf notation
- (sgf) converter for parsed to go game
- (client) new game
- (client) open game from file
- (client) open file dialog box

### Fixed
- (client) wrong move order
- (client) new game not resetting play color
- (client) when loading sgf, layout size doesn't update

### Changed
- (core) moved play() to core/rules.py

## [0.0.3] - 5-11-2026
### Added
- (client) a game tree viewer
- (client) up-down traversal keybinds
- (client) centered current node

### Changed
- (client) switched color changing marker for bg highlight
- (client) root node marker.

## [0.0.4] - 6-11-2026
### Added
- (sgf) sgf writer
- (client) save game dialog box
- (client) left-right traversal keybinds
- (client) mouse click to node in tree
- (client) scroll up-down traversal
- (client) view and toggle to menubar
- (client) game tree is togglable

### Fixed
- (Client) window resizing when enough horizontal space for tree

## [0.0.5] - 8-11-2026
### Added
- (client) theme default values
- (client) rounded dropbox 

### Changed
- (client) decoupled board magic numbers
- (client) decoupled tree magic numbers
- (client) decoupled ui magic numbers
- (client) default menu sizes
- (client) built-in default font and icons

## [0.0.6] - 10-11-2026
### Added
- (core) ko and self-capture rule
- (client) side-panel to store other widgets along with game tree
- (client) shape markers
- (client) shape and setup stones widget in side-panel
- (client) label letter/number widget in side-panel
- (sgf) converter now recognises LB, TR, MA, CR, SQ

### Fixed
- (client) using pygame depecrated methods in pygame-ce

## [0.0.7] - 12-11-2026
### Added
- (client) theme loader
- (client) optional themes svg for stones, tree nodes, surround img, and board bg 
- (client) theme switcher menu
- (client) animated stone placement variance
- (client) stone placement sound effects
- (client) pitch variance for stone sfx

### Changed
- (client) labels and shapes now renders the bg as the backing
- (client) merged surround, bg handling, backing into base_sprite
- (client) random now don't allow consecutive repeats

### Fixed
- (client) stone border calculation always being based on texture size
- (client) resolve_in recognising only files

## [0.0.8] - 14-11-2026
### Added
- (client) actionbar