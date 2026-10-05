"""Highlights only the block under the cursor in Felidae (.fx) files.

A long function that closes many nested blocks ends in a stack of `end`s.
Marking every one of them is noise; this marks the opener keyword and the
matching `end` of the innermost block around the cursor and nothing else.

The block-opening rules match the formatter and the other editor extensions:
class, `def ... =>`, `for`/`while`, switch and try own an explicit `end`.
"""

import re

import sublime
import sublime_plugin

OPEN_RE = re.compile(
    r"^\s*(class|for|while|switch|try)\b|^\s*(def)\s+[A-Za-z_][A-Za-z0-9_:.]*\s*\(.*\)\s*=>\s*(?:#.*)?$"
)
END_RE = re.compile(r"^\s*end\b")
REGION_KEY = "felidae_block"


def enclosing_block(lines, row):
    """Return (open_row, end_row) of the innermost block around ROW, or None."""
    open_row = None
    if OPEN_RE.match(lines[row]):
        open_row = row
    else:
        # An 'end' line is not counted: its own opener is the first unmatched
        # opener above it.
        depth = 0
        for candidate in range(row - 1, -1, -1):
            if END_RE.match(lines[candidate]):
                depth += 1
            elif OPEN_RE.match(lines[candidate]):
                if depth == 0:
                    open_row = candidate
                    break
                depth -= 1
    if open_row is None:
        return None
    depth = 0
    for candidate in range(open_row, len(lines)):
        if OPEN_RE.match(lines[candidate]):
            depth += 1
        elif END_RE.match(lines[candidate]):
            depth -= 1
            if depth == 0:
                return open_row, candidate
    return None


def _word_region(view, line_text, row):
    start = len(line_text) - len(line_text.lstrip())
    word = re.match(r"[A-Za-z_]+", line_text[start:])
    length = len(word.group(0)) if word else 3
    origin = view.text_point(row, start)
    return sublime.Region(origin, origin + length)


class FelidaeBlockListener(sublime_plugin.ViewEventListener):
    @classmethod
    def is_applicable(cls, settings):
        return (settings.get("syntax") or "").endswith("Felidae.sublime-syntax")

    def on_selection_modified_async(self):
        view = self.view
        if len(view.sel()) != 1:
            view.erase_regions(REGION_KEY)
            return
        row, _ = view.rowcol(view.sel()[0].b)
        lines = [view.substr(line) for line in view.lines(sublime.Region(0, view.size()))]
        if row >= len(lines):
            view.erase_regions(REGION_KEY)
            return
        block = enclosing_block(lines, row)
        if block is None:
            view.erase_regions(REGION_KEY)
            return
        open_row, end_row = block
        view.add_regions(
            REGION_KEY,
            [
                _word_region(view, lines[open_row], open_row),
                _word_region(view, lines[end_row], end_row),
            ],
            "region.yellowish",
            "",
            sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE,
        )
