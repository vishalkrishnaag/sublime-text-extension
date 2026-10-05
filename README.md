# sublime-text-extension

Sublime Text package for Felidae (`.fx`) files.

Felidae has no Sublime-native parser, so — like this repository's VS Code
and IntelliJ extensions — syntax highlighting and formatting both work
directly on buffer text.

## Features

- `Felidae.sublime-syntax` — syntax highlighting: keywords, `#` comments,
  strings, numbers, declarations, `:=` bindings, standard-library module
  names, type annotations, and constants.
- **Felidae: Format Document** (command palette, `Ctrl+Shift+P` /
  `Cmd+Shift+P`) — a structural beautifier that recomputes indentation,
  collapses extra blank lines, and trims trailing whitespace. It is a
  line-for-line port of the same algorithm used by `vs-code-extension`'s
  "Format Document" and `intellij-idea-extension`'s "Format Felidae File",
  so all editors in this repository normalize `.fx` files the same way.
- **Felidae: Check Document** (command palette) — runs `felidae --check-json` (nothing is
  executed, no database is opened) and lists the problems in an output panel as
  `file:line:column: severity: message`; double-click one, or press `F4` / `Shift+F4`, to jump to it.
- **Felidae: Open REPL** (command palette; needs the [Terminus](https://packagecontrol.io/packages/Terminus)
  package) — `felidae --repl` in a terminal tab, in the file's folder (the REPL reads `./init.fx`).
- `Felidae.sublime-build` — `Tools > Build` runs the current file with
  `felidae`; the build variant (`Ctrl+Shift+B`) runs `celidae --html`.
- A few starter snippets (`import`, `fact`, `function`, `class`, `for`, `while`, `switch`, `try`, `throw` and more) ported from
  `vs-code-extension/snippets/felidae.json`.

## Installation

Copy (or symlink) this directory into your Sublime Text `Packages`
directory as `Felidae`:

- Windows: `%APPDATA%\Sublime Text\Packages\Felidae`
- macOS: `~/Library/Application Support/Sublime Text/Packages/Felidae`
- Linux: `~/.config/sublime-text/Packages/Felidae`

(`Preferences > Browse Packages…` opens that directory directly.)

## Configuration

The `felidae_interpreter` setting (`Felidae.sublime-settings`, default `felidae`) is the
executable used by *Felidae: Check Document*. The build system's `felidae` / `celidae` commands are
resolved via `$PATH` by default. Edit `Felidae.sublime-build` (`Tools >
Build System > Edit`) to point at absolute executable paths if they are not
on `$PATH`. The build system uses argument arrays to launch the native
interpreter directly. Use felidae.exe on Windows and felidae on Linux/macOS.
