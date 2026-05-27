#!/usr/bin/env python3
"""
nord-launch v2 — macOS Spotlight for Hyprland
Dark glass · GTK4 · Python3 · Two-column layout

Hyprland rules  → ~/.config/hypr/conf/rules.conf:
  windowrule = float,        class:^(dev.rmustard.nordlaunch)$
  windowrule = center,       class:^(dev.rmustard.nordlaunch)$
  windowrule = size 700 -1,  class:^(dev.rmustard.nordlaunch)$
  windowrule = noborder,     class:^(dev.rmustard.nordlaunch)$
  windowrule = noshadow,     class:^(dev.rmustard.nordlaunch)$
  windowrule = noanim,       class:^(dev.rmustard.nordlaunch)$
  windowrule = stayfocused,  class:^(dev.rmustard.nordlaunch)$

Keybind:
  bind = SUPER, SPACE, exec, pkill -f "python3.*launcher.py" || python3 ~/.config/spotlight/launcher.py

Deps: sudo dnf install python3-gobject gtk4 wl-clipboard
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

import math
import os
import re
import shlex
import shutil
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from gi.repository import Gdk, GLib, Gtk, Pango

# ─────────────────────────────────────────────────────────────────────────────
#  CSS — Nord palette · Sleek two-column Spotlight
# ─────────────────────────────────────────────────────────────────────────────
#  Nord palette reference
#  Polar Night : #2E3440  #3B4252  #434C5E  #4C566A
#  Snow Storm  : #D8DEE9  #E5E9F0  #ECEFF4
#  Frost       : #8FBCBB  #88C0D0  #81A1C1  #5E81AC
#  Aurora      : #BF616A  #D08770  #EBCB8B  #A3BE8C  #B48EAD
# ─────────────────────────────────────────────────────────────────────────────
CSS = """
* { -gtk-icon-style: regular; }

window {
    background:  transparent;
    border:      none;
    box-shadow:  none;
    padding:     0;
    margin:      0;
}

/* GTK4 CSD layers — kill all */
window > decoration,
window > decoration-overlay,
.csd,
.csd > decoration,
.csd > decoration-overlay,
.solid-csd,
.solid-csd > decoration {
    border:      none;
    box-shadow:  none;
    background:  transparent;
    padding:     0;
    margin:      0;
}

/* ── Shell ───────────────────────────────────────────────────────────────── */
.shell {
    margin:        0;
    background:    rgba(46, 52, 64, 0.94);
    border:        1px solid rgba(136, 192, 208, 0.10);
    border-radius: 12px;
    box-shadow:
        0 48px 120px rgba(0, 0, 0, 0.70),
        0 12px 36px  rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(216, 222, 233, 0.05);
}

/* ── Search bar ──────────────────────────────────────────────────────────── */
.search-row {
    padding:       0 14px;
    margin:        12px 12px 10px 12px;
    min-height:    46px;
    background:    rgba(59, 66, 82, 0.60);
    border-radius: 10px;
    border:        1px solid rgba(136, 192, 208, 0.09);
}

.search-icon {
    color:        #6B7A90;
    margin-left:  10px;
    margin-right: 12px;
    min-width:    15px;
}

.search-entry,
.search-entry:focus,
.search-entry:hover,
.search-entry:active {
    background:       transparent;
    background-color: transparent;
    background-image: none;
    border:           none;
    outline:          none;
    box-shadow:       none;
    padding:          0;
    margin:           0;
    font-size:        17px;
    font-family:      'Inter', 'Cantarell', sans-serif;
    font-weight:      500;
    letter-spacing:   0px;
    caret-color:      #88C0D0;
    min-height:       0;
    min-width:        0;
    border-radius:    0;
}

.search-entry text {
    background:       transparent;
    background-color: transparent;
    color:            #ECEFF4;
    border:           none;
    box-shadow:       none;
    outli0one;
}

.search-entry selection {
    background-color: rgba(136, 192, 208, 0.20);
    color:            #ECEFF4;
}

.search-entry placeholder {
    color: #4C566A;
}

entry.flat,
entry.flat text,
entry > text {
    background:       transparent;
    background-color: transparent;
    border:           none;
    box-shadow:       none;
    outline:          none;
}

/* ── Dividers ────────────────────────────────────────────────────────────── */
.hdiv {
    background-color: rgba(76, 86, 106, 0.40);
    min-height:       1px;
    margin:           0 12px;
}

.vdiv {
    background-color: rgba(76, 86, 106, 0.40);
    min-width:        1px;
}

/* ── Left panel ──────────────────────────────────────────────────────────── */
.left-panel {
    min-width: 252px;
    max-width: 252px;
}

/* ── Section headers ─────────────────────────────────────────────────────── */
.section-header {
    color:          #8F9BB0;
    font-size:      10px;
    font-weight:    700;
    font-family:    'Inter', 'Cantarell', sans-serif;
    letter-spacing: 1px;
}

.section-label {
    color:          #6B7A90;
    font-size:      9px;
    font-weight:    700;
    font-family:    'Inter', 'Cantarell', sans-serif;
    letter-spacing: 1.1px;
}

/* ── Result rows ─────────────────────────────────────────────────────────── */
listbox {
    background: transparent;
    padding:    4px 6px 10px 6px;
}

listbox > row {
    background:    transparent;
    border-radius: 10px;
    margin:        0;
    padding:       0;
    border:        none;
    outline:       none;
}

listbox > row:selected {
    background: transparent;
}

.rrow {
    padding:       6px 10px;
    border-radius: 10px;
    min-height:    40px;
    transition:    background 90ms ease;
}

.rrow.hi {
    background: linear-gradient(
        135deg,
        rgba(94, 129, 172, 0.24) 0%,
        rgba(67, 76, 94, 0.50)   100%
    );
    box-shadow: inset 0 1px 0 rgba(136, 192, 208, 0.07);
}

.ri {
    margin-right:  10px;
    opacity:       0.92;
    border-radius: 5px;
}

.rname {
    color:          #F2F5FA;
    font-size:      13.5px;
    font-weight:    500;
    font-family:    'Inter', 'Cantarell', sans-serif;
    letter-spacing: 0px;
}

.rname.dim {
    color:       #9BB8D9;
    font-weight: 500;
}

.rdesc {
    color:       #8892A4;
    font-size:   10.5px;
    margin-top:  1px;
    font-family: 'Inter', 'Cantarell', sans-serif;
}

.rpath {
    color:       #93A3B8;
    font-size:   10.5px;
    margin-top:  2px;
    font-family: 'JetBrains Mono', 'Fira Mono', monospace;
}

/* ── Preview panel ───────────────────────────────────────────────────────── */
.preview {
    background: transparent;
    padding:    28px 26px 28px 26px;
    min-width:  340px;
}

.preview-icon {
    margin-bottom: 20px;
}

.preview-name {
    color:          #F2F5FA;
    font-size:      20px;
    font-weight:    500;
    font-family:    'Inter', 'Cantarell', sans-serif;
    letter-spacing: 0px;
    margin-bottom:  4px;
}

.preview-kind {
    color:          #8F9BB0;
    font-size:      10px;
    font-weight:    700;
    font-family:    'Inter', 'Cantarell', sans-serif;
    letter-spacing: 1px;
    margin-bottom:  16px;
}

.preview-desc {
    color:       #C0CAD8;
    font-size:   13px;
    font-family: 'Inter', 'Cantarell', sans-serif;
    line-height: 1.55;
}

.preview-path {
    color:       #93A3B8;
    font-size:   10.5px;
    font-family: 'JetBrains Mono', 'Fira Mono', monospace;
    margin-top:  14px;
    line-height: 1.4;
}

.preview-calc-expr {
    color:          #94A3B8;
    font-size:      12.5px;
    font-family:    'JetBrains Mono', 'Fira Mono', monospace;
    letter-spacing: 0px;
    margin-bottom:  8px;
}

.preview-calc-result {
    color:          #A3BE8C;
    font-size:      42px;
    font-family:    'Inter', 'Cantarell', sans-serif;
    font-weight:    500;
    letter-spacing: -1px;
    margin-top:     2px;
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
scrollbar {
    background: transparent;
    min-width:  4px;
}

scrollbar slider {
    background-color: rgba(76, 86, 106, 0.50);
    border-radius:    999px;
    min-width:        3px;
    min-height:       20px;
}

scrolledwindow {
    background: transparent;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────
_KIND_ORDER: dict[str, int] = {
    "calc": 0,
    "run": 1,
    "app": 2,
    "file": 3,
    "web": 4,
}
_KIND_LABELS: dict[str, str] = {
    "calc": "CALCULATOR",
    "app": "APPLICATIONS",
    "web": "WEB",
    "file": "FILES",
    "run": "SHELL",
}
_KIND_NAMES: dict[str, str] = {
    "calc": "Calculator",
    "app": "Application",
    "web": "Web Search",
    "file": "File",
    "run": "Shell Command",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Data
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Result:
    name: str
    desc: str
    kind: str
    icon: str = "application-x-executable"
    cmd: str = ""
    score: int = 0
    copy_val: str = ""
    desktop_path: str = ""
    file_path: str = ""


# ─────────────────────────────────────────────────────────────────────────────
#  App indexer
# ─────────────────────────────────────────────────────────────────────────────
class AppIndexer:
    _DIRS = [
        Path.home() / ".local/share/applications",
        Path("/usr/share/applications"),
        Path("/usr/local/share/applications"),
        Path("/var/lib/flatpak/exports/share/applications"),
        Path.home() / ".local/share/flatpak/exports/share/applications",
    ]

    def __init__(self):
        self.apps: list[Result] = []
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        seen: set[str] = set()
        out: list[Result] = []
        for d in self._DIRS:
            if not d.exists():
                continue
            for f in sorted(d.glob("*.desktop")):
                if f.name in seen:
                    continue
                seen.add(f.name)
                r = self._parse(f)
                if r:
                    out.append(r)
        out.sort(key=lambda a: a.name.lower())
        self.apps = out

    def _parse(self, path: Path) -> Optional[Result]:
        kv: dict[str, str] = {}
        in_entry = False
        try:
            for raw in path.read_text(errors="ignore").splitlines():
                line = raw.strip()
                if line == "[Desktop Entry]":
                    in_entry = True
                elif line.startswith("[") and in_entry:
                    break
                elif in_entry and "=" in line:
                    k, _, v = line.partition("=")
                    kv[k.strip()] = v.strip()
        except Exception:
            return None
        if kv.get("NoDisplay", "").lower() == "true":
            return None
        if kv.get("Hidden", "").lower() == "true":
            return None
        if kv.get("Type") != "Application":
            return None
        name = kv.get("Name", "").strip()
        if not name:
            return None
        cmd = re.sub(r"%[fFuUdDnNickvm]", "", kv.get("Exec", "")).strip()
        return Result(
            name=name,
            desc=kv.get("Comment", kv.get("GenericName", "")),
            kind="app",
            icon=kv.get("Icon", "application-x-executable"),
            cmd=cmd,
            desktop_path=str(path),
        )

    def search(self, q: str, limit: int = 6) -> list[Result]:
        ql = q.lower()
        out = []
        for app in self.apps:
            nl = app.name.lower()
            dl = app.desc.lower()
            if nl == ql:
                score = 200
            elif nl.startswith(ql):
                score = 150
            elif ql in nl:
                score = 100 - nl.index(ql)
            elif all(t in nl or t in dl for t in ql.split()):
                score = 40
            elif ql in dl:
                score = 20
            else:
                continue
            out.append(Result(**{**app.__dict__, "score": score}))
        out.sort(key=lambda r: -r.score)
        return out[:limit]


# ─────────────────────────────────────────────────────────────────────────────
#  File searcher
# ─────────────────────────────────────────────────────────────────────────────
_FILE_ICONS = {
    ".py": "text-x-python",
    ".js": "text-x-javascript",
    ".ts": "text-x-typescript",
    ".html": "text-html",
    ".htm": "text-html",
    ".css": "text-x-css",
    ".json": "text-x-json",
    ".md": "text-x-markdown",
    ".txt": "text-plain",
    ".pdf": "application-pdf",
    ".png": "image-png",
    ".jpg": "image-jpeg",
    ".jpeg": "image-jpeg",
    ".svg": "image-svg+xml",
    ".sh": "text-x-script",
    ".c": "text-x-csrc",
    ".cpp": "text-x-c++src",
    ".rs": "text-x-rust",
    ".lua": "text-x-lua",
    ".toml": "text-x-toml",
    ".yaml": "text-x-yaml",
    ".yml": "text-x-yaml",
    ".vue": "text-x-vue",
    ".go": "text-x-go",
}


class FileSearcher:
    def search_async(self, query: str, callback):
        threading.Thread(target=self._run, args=(query, callback), daemon=True).start()

    def _run(self, query: str, callback):
        try:
            proc = subprocess.run(
                [
                    "find",
                    str(Path.home()),
                    "-maxdepth",
                    "12",
                    "-type",
                    "f",
                    "-iname",
                    f"*{query}*",
                    "-not",
                    "-path",
                    "*/.git/*",
                    "-not",
                    "-path",
                    "*/.cache/*",
                    "-not",
                    "-path",
                    "*/node_modules/*",
                    "-not",
                    "-path",
                    "*/__pycache__/*",
                    "-not",
                    "-path",
                    "*/.local/share/Trash/*",
                ],
                capture_output=True,
                text=True,
                timeout=6,
            )
            paths = proc.stdout.strip().splitlines()[:10]
        except Exception:
            paths = []
        results = []
        home = Path.home()
        for p in paths:
            path = Path(p)
            try:
                desc = "~/" + str(path.parent.relative_to(home))
            except:
                desc = str(path.parent)
            results.append(
                Result(
                    name=path.name,
                    desc=desc,
                    kind="file",
                    icon=_FILE_ICONS.get(path.suffix.lower(), "text-x-generic"),
                    file_path=str(path),
                    score=50,
                )
            )
        GLib.idle_add(callback, results)


# ─────────────────────────────────────────────────────────────────────────────
#  Calculator
# ─────────────────────────────────────────────────────────────────────────────
_MATH_RE = re.compile(r"[\d].*[\+\-\*\/\^%]|[\+\-\*\/\^%].*\d")
_SAFE_RE = re.compile(r"^[\d\s\+\-\*\/\(\)\.\,\^%sqrtpielog\!]+$", re.I)


def calc_eval(expr: str) -> Optional[str]:
    expr = expr.strip()
    if not _MATH_RE.search(expr):
        return None
    if not _SAFE_RE.match(expr):
        return None
    try:
        s = expr.replace("^", "**").replace(",", ".")
        s = re.sub(r"\bsqrt\b", "math.sqrt", s)
        s = re.sub(r"\bsin\b", "math.sin", s)
        s = re.sub(r"\bcos\b", "math.cos", s)
        s = re.sub(r"\btan\b", "math.tan", s)
        s = re.sub(r"\bln\b", "math.log", s)
        s = re.sub(r"\blog\b", "math.log10", s)
        s = re.sub(r"\bpi\b", "math.pi", s)
        s = re.sub(r"\be\b", "math.e", s)
        result = eval(s, {"__builtins__": {}, "math": math})  # noqa: S307
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                return str(int(result))
            return f"{result:.8g}"
        return str(result)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Window
# ─────────────────────────────────────────────────────────────────────────────
class NordLaunch(Gtk.ApplicationWindow):
    WIDTH = 700
    MAX_ROWS = 8

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("nord-launch")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(self.WIDTH, -1)
        # Strip GTK4's automatic client-side decoration layer
        self.remove_css_class("csd")
        self.remove_css_class("solid-csd")

        self._indexer = app.indexer
        self._results: list[Result] = []
        self._active = -1

        self._load_css()
        self._build()
        self._setup_input()

    # ── CSS ──────────────────────────────────────────────────────────────────
    def _load_css(self):
        p = Gtk.CssProvider()
        p.load_from_data(CSS.encode())
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    # ── UI layout ────────────────────────────────────────────────────────────
    def _build(self):
        # Root: vertical shell (for border-radius + bg)
        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        shell.add_css_class("shell")
        self.set_child(shell)

        # Outer horizontal row — always present
        main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        shell.append(main)

        # ── Left column: search frame + divider + results ─────────────────
        #
        #   The search frame lives INSIDE the left column, so its right edge
        #   naturally aligns with the results list below it and stops at the
        #   vertical divider — no extra width calculation needed.
        #
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left.add_css_class("left-panel")
        left.set_size_request(252, -1)

        # Search bar
        sr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        sr.add_css_class("search-row")
        sr.set_valign(Gtk.Align.CENTER)

        ico = Gtk.Image.new_from_icon_name("system-search-symbolic")
        ico.set_pixel_size(15)
        ico.add_css_class("search-icon")
        ico.set_valign(Gtk.Align.CENTER)
        sr.append(ico)

        self._entry = Gtk.Entry()
        self._entry.add_css_class("search-entry")
        self._entry.add_css_class("flat")
        self._entry.set_has_frame(False)
        self._entry.set_hexpand(True)
        self._entry.set_overflow(Gtk.Overflow.HIDDEN)
        self._entry.set_placeholder_text("Search")
        self._entry.set_valign(Gtk.Align.CENTER)
        self._entry.connect("changed", self._on_changed)
        sr.append(self._entry)
        left.append(sr)

        # Thin divider — hidden when query is empty
        self._hdiv = Gtk.Box()
        self._hdiv.add_css_class("hdiv")
        self._hdiv.set_visible(False)
        left.append(self._hdiv)

        # Results listbox — hidden when query is empty
        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self._listbox.connect("row-activated", self._on_row_click)
        self._listbox.set_header_func(self._header_func)

        self._scroll = Gtk.ScrolledWindow()
        self._scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self._scroll.set_max_content_height(330)
        self._scroll.set_propagate_natural_height(True)
        self._scroll.set_child(self._listbox)
        self._scroll.set_visible(False)
        left.append(self._scroll)

        main.append(left)

        # ── Vertical separator — hidden when query is empty ────────────────
        self._vdiv = Gtk.Box()
        self._vdiv.add_css_class("vdiv")
        self._vdiv.set_visible(False)
        main.append(self._vdiv)

        # ── Right: preview panel — hidden when query is empty ─────────────
        self._preview = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._preview.add_css_class("preview")
        self._preview.set_hexpand(True)
        self._preview.set_valign(Gtk.Align.START)
        self._preview.set_visible(False)

        self._prev_icon = Gtk.Image()
        self._prev_icon.set_pixel_size(64)
        self._prev_icon.add_css_class("preview-icon")
        self._prev_icon.set_halign(Gtk.Align.START)
        self._preview.append(self._prev_icon)

        self._prev_name = Gtk.Label()
        self._prev_name.set_halign(Gtk.Align.START)
        self._prev_name.set_ellipsize(Pango.EllipsizeMode.END)
        self._prev_name.set_max_width_chars(22)
        self._prev_name.add_css_class("preview-name")
        self._preview.append(self._prev_name)

        self._prev_kind = Gtk.Label()
        self._prev_kind.set_halign(Gtk.Align.START)
        self._prev_kind.add_css_class("preview-kind")
        self._preview.append(self._prev_kind)

        self._prev_desc = Gtk.Label()
        self._prev_desc.set_halign(Gtk.Align.START)
        self._prev_desc.set_wrap(True)
        self._prev_desc.set_max_width_chars(28)
        self._prev_desc.set_xalign(0.0)
        self._prev_desc.add_css_class("preview-desc")
        self._preview.append(self._prev_desc)

        self._prev_path = Gtk.Label()
        self._prev_path.set_halign(Gtk.Align.START)
        self._prev_path.set_wrap(True)
        self._prev_path.set_max_width_chars(28)
        self._prev_path.set_xalign(0.0)
        self._prev_path.add_css_class("preview-path")
        self._preview.append(self._prev_path)

        self._prev_calc_expr = Gtk.Label()
        self._prev_calc_expr.set_halign(Gtk.Align.START)
        self._prev_calc_expr.add_css_class("preview-calc-expr")
        self._preview.append(self._prev_calc_expr)

        self._prev_calc = Gtk.Label()
        self._prev_calc.set_halign(Gtk.Align.START)
        self._prev_calc.add_css_class("preview-calc-result")
        self._preview.append(self._prev_calc)

        main.append(self._preview)

    # ── Input wiring ─────────────────────────────────────────────────────────
    def _setup_input(self):
        self._entry.connect("activate", lambda _: self._launch(self._active))
        kc = Gtk.EventControllerKey()
        kc.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        kc.connect("key-pressed", self._on_key)
        self._entry.add_controller(kc)

    def _on_key(self, _c, kv, _kc, _st):
        if kv == Gdk.KEY_Escape:
            self.close()
            return True
        if kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            self._launch(self._active)
            return True
        if kv in (Gdk.KEY_Up, Gdk.KEY_ISO_Left_Tab):
            self._move(-1)
            return True
        if kv in (Gdk.KEY_Down, Gdk.KEY_Tab):
            self._move(1)
            return True
        return False

    def _move(self, d: int):
        n = len(self._results)
        if n:
            self._set_active((self._active + d) % n)

    # ── Section headers ───────────────────────────────────────────────────────
    def _header_func(self, row, before):
        idx = row.get_index()
        if idx >= len(self._results):
            row.set_header(None)
            return
        kind = self._results[idx].kind
        if before is None:
            row.set_header(self._make_section_header(kind))
        else:
            prev_idx = before.get_index()
            prev_kind = (
                self._results[prev_idx].kind if prev_idx < len(self._results) else None
            )
            row.set_header(
                self._make_section_header(kind) if prev_kind != kind else None
            )

    def _make_section_header(self, kind: str) -> Gtk.Widget:
        box = Gtk.Box()
        box.add_css_class("section-header")
        lbl = Gtk.Label(label=_KIND_LABELS.get(kind, kind.upper()))
        lbl.add_css_class("section-label")
        lbl.set_halign(Gtk.Align.START)
        box.append(lbl)
        return box

    # ── Rebuild results ───────────────────────────────────────────────────────
    def _on_changed(self, _e):
        self._rebuild(self._entry.get_text().strip())

    def _rebuild(self, query: str):
        while row := self._listbox.get_row_at_index(0):
            self._listbox.remove(row)
        self._results.clear()
        self._active = -1

        # Show/hide secondary elements together
        show = bool(query)
        self._hdiv.set_visible(show)
        self._scroll.set_visible(show)
        self._vdiv.set_visible(show)
        self._preview.set_visible(show)

        if not query:
            return

        results: list[Result] = []

        val = calc_eval(query)
        if val is not None:
            results.append(
                Result(
                    name="Copy result",
                    desc=f"= {val}",
                    kind="calc",
                    icon="accessories-calculator",
                    score=999,
                    copy_val=val,
                )
            )

        if query.startswith("!") and len(query) > 1:
            raw = query[1:].strip()
            results.append(
                Result(
                    name=f"Run: {raw}",
                    desc="Execute in shell",
                    kind="run",
                    icon="utilities-terminal",
                    cmd=raw,
                    score=900,
                )
            )

        results.extend(self._indexer.search(query))

        results.append(
            Result(
                name=f'Search "{query}"',
                desc="Open in browser",
                kind="web",
                icon="applications-internet",
                cmd=f"https://www.google.com/search?q={query.replace(' ', '+')}",
                score=1,
            )
        )

        results.sort(key=lambda r: (_KIND_ORDER.get(r.kind, 99), -r.score))
        self._results = results[: self.MAX_ROWS]

        for r in self._results:
            self._listbox.append(self._make_row(r))

        self._set_active(0)

    # ── Row widget ────────────────────────────────────────────────────────────
    def _make_row(self, r: Result) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("rrow")
        box.set_valign(Gtk.Align.CENTER)

        iw = Gtk.Image()
        iw.add_css_class("ri")
        iw.set_valign(Gtk.Align.CENTER)
        self._apply_icon(iw, r, 26)
        box.append(iw)

        tc = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tc.set_hexpand(True)
        tc.set_valign(Gtk.Align.CENTER)

        nl = Gtk.Label(label=r.name)
        nl.set_halign(Gtk.Align.START)
        nl.set_ellipsize(Pango.EllipsizeMode.END)
        nl.set_max_width_chars(22)
        nl.add_css_class("rname")
        if r.kind == "web":
            nl.add_css_class("dim")
        tc.append(nl)

        if r.desc and r.kind != "calc":
            dl = Gtk.Label(label=r.desc)
            dl.set_halign(Gtk.Align.START)
            dl.set_ellipsize(
                Pango.EllipsizeMode.START
                if r.kind == "file"
                else Pango.EllipsizeMode.END
            )
            dl.set_max_width_chars(24)
            dl.add_css_class("rpath" if r.kind == "file" else "rdesc")
            tc.append(dl)

        box.append(tc)
        row.set_child(box)
        return row

    # ── Preview ───────────────────────────────────────────────────────────────
    def _update_preview(self, r: Result):
        self._apply_icon(self._prev_icon, r, 64)
        self._prev_name.set_text(r.name)
        self._prev_kind.set_text(_KIND_NAMES.get(r.kind, r.kind.title()))

        if r.kind == "calc":
            self._prev_desc.set_visible(False)
            self._prev_path.set_visible(False)
            self._prev_calc_expr.set_text(
                r.desc.split("=")[0].strip() if r.desc else ""
            )
            self._prev_calc_expr.set_visible(True)
            self._prev_calc.set_text(f"= {r.copy_val}")
            self._prev_calc.set_visible(True)
        else:
            self._prev_calc_expr.set_visible(False)
            self._prev_calc.set_visible(False)
            self._prev_desc.set_text(r.desc or "")
            self._prev_desc.set_visible(bool(r.desc))
            if r.file_path:
                self._prev_path.set_text(r.file_path)
                self._prev_path.set_visible(True)
            elif r.kind == "web" and r.cmd:
                self._prev_path.set_text(r.cmd[:70])
                self._prev_path.set_visible(True)
            elif r.kind == "app" and r.desktop_path:
                self._prev_path.set_text(r.desktop_path)
                self._prev_path.set_visible(True)
            else:
                self._prev_path.set_visible(False)

    # ── Icon helper ───────────────────────────────────────────────────────────
    def _apply_icon(self, widget: Gtk.Image, r: Result, size: int):
        widget.set_pixel_size(size)
        _FALLBACK = {
            "app": "application-x-executable",
            "calc": "accessories-calculator",
            "web": "applications-internet",
            "file": "text-x-generic",
            "run": "utilities-terminal",
        }
        if r.icon.startswith("/") and Path(r.icon).exists():
            widget.set_from_file(r.icon)
            return
        display = Gdk.Display.get_default()
        theme = Gtk.IconTheme.get_for_display(display) if display else None
        name = r.icon
        if theme and not theme.has_icon(name):
            name = _FALLBACK.get(r.kind, "application-x-executable")
        widget.set_from_icon_name(name)

    # ── Active row highlight ──────────────────────────────────────────────────
    def _set_active(self, idx: int):
        n = len(self._results)
        if n == 0:
            return
        if 0 <= self._active < n:
            old = self._listbox.get_row_at_index(self._active)
            if old and old.get_child():
                old.get_child().remove_css_class("hi")
        self._active = max(0, min(idx, n - 1))
        new = self._listbox.get_row_at_index(self._active)
        if new and new.get_child():
            new.get_child().add_css_class("hi")
        self._update_preview(self._results[self._active])

    def _on_row_click(self, _lb, row):
        self._launch(row.get_index())

    # ── Launch ────────────────────────────────────────────────────────────────
    def _launch(self, idx: int):
        import traceback

        log = open("/tmp/nord-launch.log", "a")
        log.write(f"\n=== _launch idx={idx} total={len(self._results)} ===\n")
        try:
            if not (0 <= idx < len(self._results)):
                log.write("idx out of range\n")
                return
            r = self._results[idx]
            log.write(f"kind={r.kind!r} name={r.name!r} cmd={r.cmd!r}\n")
            if r.kind == "calc":
                self._copy_to_clipboard(r.copy_val)
            elif r.kind == "app":
                self._launch_app(r)
            elif r.kind == "web":
                self._open_url(r.cmd)
            elif r.kind == "file":
                self._open_in_nvim(r.file_path)
            elif r.kind == "run":
                self._popen(r.cmd, shell=True)
        except Exception as e:
            log.write(f"EXCEPTION: {e}\n{traceback.format_exc()}\n")
        finally:
            log.close()
        self.close()

    def _copy_to_clipboard(self, text: str):
        wlcopy = shutil.which("wl-copy")
        if wlcopy:
            subprocess.run(
                [wlcopy, text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        else:
            try:
                Gdk.Display.get_default().get_clipboard().set(text)
            except Exception:
                pass

    def _hypr_exec(self, cmd: str):
        log = open("/tmp/nord-launch.log", "a")
        log.write(f"\n[exec] {cmd!r}\n")
        hyprctl = shutil.which("hyprctl")
        if hyprctl:
            try:
                r = subprocess.run(
                    [hyprctl, "dispatch", "exec", cmd],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                log.write(f"[exec] rc={r.returncode} stdout={r.stdout!r}\n")
                if r.returncode == 0:
                    log.close()
                    return
            except Exception as e:
                log.write(f"[exec] hyprctl exception: {e}\n")
        try:
            p = subprocess.Popen(
                cmd,
                shell=True,
                env={**os.environ},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            log.write(f"[exec] fallback Popen pid={p.pid}\n")
        except Exception as e:
            log.write(f"[exec] Popen exception: {e}\n")
        log.close()

    def _launch_app(self, r: Result):
        if r.desktop_path:
            self._hypr_exec(f"gtk-launch {Path(r.desktop_path).stem}")
        elif r.cmd:
            self._hypr_exec(r.cmd)

    def _open_in_nvim(self, filepath: str):
        fp = filepath.replace("'", "'\\''")
        self._hypr_exec(f"kitty nvim '{fp}'")

    def _open_url(self, url: str):
        safe = url.replace("'", "%27")
        for b in (
            "firefox",
            "firefox-esr",
            "chromium",
            "chromium-browser",
            "google-chrome",
            "brave",
            "brave-browser",
            "librewolf",
        ):
            if shutil.which(b):
                self._hypr_exec(f"{b} '{safe}'")
                return
        self._hypr_exec(f"xdg-open '{safe}'")

    def _popen(self, cmd, shell=False):
        if isinstance(cmd, list):
            cmd = " ".join(shlex.quote(c) for c in cmd)
        self._hypr_exec(cmd)


# ─────────────────────────────────────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────────────────────────────────────
class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="dev.rmustard.nordlaunch")
        self.indexer = AppIndexer()

    def do_activate(self):
        NordLaunch(self).present()


if __name__ == "__main__":
    import sys

    App().run(sys.argv)
