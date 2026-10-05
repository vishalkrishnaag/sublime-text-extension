"""Felidae: Check Document - the interpreter's own parser, with clickable results.

Runs `felidae --check-json FILE` (nothing is executed and no database is
opened) and lists the problems in an output panel as `file:line:column:
severity: message`; double-click one, or press F4 / Shift+F4, to jump to it.
The interpreter path is the `felidae_interpreter` setting (default `felidae`).
"""

import json
import os
import subprocess
import threading

import sublime
import sublime_plugin

PANEL = "felidae_check"
TIMEOUT_SECONDS = 30


def format_diagnostics(file_name, output):
    """Compilation-style lines for the diagnostics in OUTPUT (check-json text).

    OUTPUT that is not JSON (the interpreter could not check at all, for
    example without an init.fx) is returned as a single text line."""
    try:
        diagnostics = json.loads(output)["diagnostics"]
    except (ValueError, KeyError, TypeError):
        text = output.strip()
        return [text] if text else []
    lines = []
    for diagnostic in diagnostics:
        start = diagnostic.get("start", {})
        lines.append(
            "%s:%d:%d: %s: %s"
            % (
                file_name,
                start.get("line", 1),
                start.get("column", 1),
                diagnostic.get("severity", "error"),
                diagnostic.get("message", ""),
            )
        )
    return lines


class FelidaeCheckCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        view = self.window.active_view()
        return bool(view and view.file_name() and view.match_selector(0, "source.felidae"))

    def run(self):
        view = self.window.active_view()
        if view.is_dirty():
            view.run_command("save")
        file_name = view.file_name()
        interpreter = view.settings().get("felidae_interpreter", "felidae")
        threading.Thread(target=self._check, args=(interpreter, file_name), daemon=True).start()

    def _check(self, interpreter, file_name):
        try:
            result = subprocess.run(
                [interpreter, "--check-json", file_name],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
            lines = format_diagnostics(file_name, result.stdout or result.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            lines = ["Cannot check with %s: %s" % (interpreter, error)]
        sublime.set_timeout(lambda: self._show(file_name, lines), 0)

    def _show(self, file_name, lines):
        if not lines:
            self.window.run_command("hide_panel", {"panel": "output." + PANEL})
            self.window.status_message("Felidae: no problems in %s" % os.path.basename(file_name))
            return
        panel = self.window.create_output_panel(PANEL)
        panel.settings().set("result_file_regex", r"^(.+?):(\d+):(\d+): (.*)$")
        panel.settings().set("result_base_dir", os.path.dirname(file_name))
        panel.run_command("append", {"characters": "\n".join(lines) + "\n"})
        self.window.run_command("show_panel", {"panel": "output." + PANEL})
