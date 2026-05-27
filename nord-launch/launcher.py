#!/usr/bin/env python3
"""
nord-launch — macOS Spotlight for Hyprland
Single-column · Nord Dark · GTK4 · Python3

Hyprland rules (~/.config/hypr/conf/rules.conf):
  windowrule = float,        class:^(dev.rmustard.nordlaunch)$
  windowrule = center,       class:^(dev.rmustard.nordlaunch)$
  windowrule = size 620 -1,  class:^(dev.rmustard.nordlaunch)$
  windowrule = noborder,     class:^(dev.rmustard.nordlaunch)$
  windowrule = noshadow,     class:^(dev.rmustard.nordlaunch)$
  windowrule = noanim,       class:^(dev.rmustard.nordlaunch)$
  windowrule = stayfocused,  class:^(dev.rmustard.nordlaunch)$

Keybind:
  bind = SUPER, SPACE, exec, pkill -f "python3.*launcher.py" || python3 ~/.config/spotlight/launcher.py

Deps:
  sudo dnf install python3-gobject gtk4 wl-clipboard imv
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

import math
import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from gi.repository import Gdk, Gio, Gtk, Pango

_SEARCH_BG = "#353C4E"

CSS = f"""
window {{
    background: transparent;
    border: none; box-shadow: none; padding: 0; margin: 0;
}}
window > decoration, window > decoration-overlay,
.csd > decoration, .csd > decoration-overlay {{
    border: none; box-shadow: none; background: transparent; padding: 0; margin: 0;
}}

/* ── Shell ── */
.shell {{
    background-color: rgba(43, 48, 59, 0.96);
    border:           1px solid rgba(76, 86, 106, 0.50);
    border-radius:    18px;
    box-shadow:
        0 32px 80px rgba(0, 0, 0, 0.55),
        0 8px 24px  rgba(0, 0, 0, 0.28),
        inset 0 1px 0 rgba(216, 222, 233, 0.04);
}}

/* ── Search row ── */
.search-row {{
    background:    {_SEARCH_BG};
    border-radius: 13px;
    margin:        10px;
    padding:       0 14px;
    min-height:    50px;
}}
.search-icon {{
    color:        #6B7A90;
    margin-left: 3px;
    margin-right: 3px;
}}

/* Kill all GTK Entry decoration */
.search-entry,
.search-entry:focus,
.search-entry:hover,
.search-entry:active,
.search-entry:disabled,
searchfield, searchfield:focus {{
    background:       {_SEARCH_BG};
    background-color: {_SEARCH_BG};
    background-image: none;
    border: none; outline: none; box-shadow: none;
    padding: 0; margin: 0; border-radius: 0;
    font-size:   17px;
    font-family: 'Inter', 'Cantarell', sans-serif;
    font-weight: 400;
    caret-color: #88C0D0;
    min-height: 0; min-width: 0;
}}
.search-entry text, .search-entry > text,
.search-entry undershoot.left, .search-entry undershoot.right,
.search-entry overshoot.left,  .search-entry overshoot.right,
searchfield text, searchfield > text,
searchfield undershoot, searchfield overshoot {{
    background: {_SEARCH_BG}; background-color: {_SEARCH_BG};
    color: #ECEFF4; border: none; box-shadow: none;
}}
.search-entry placeholder {{ color: #4C566A; }}
.search-entry selection   {{ background-color: rgba(136,192,208,0.22); }}

/* ── Divider ── */
.hdiv {{ background-color: rgba(59,66,82,0.80); min-height: 1px; margin: 0 10px; }}

/* ── Results list ── */
listbox {{
    background: transparent;
    padding:    4px 6px 8px 6px;
}}
listbox > row {{
    background:    transparent;
    border-radius: 10px;
    padding: 0; margin: 0; border: none; outline: none;
}}
listbox > row:selected {{ background: transparent; }}

.rrow {{
    padding:       7px 10px;
    border-radius: 10px;
    min-height:    44px;
    border-left:   2px solid transparent;
}}

/* ── Selected: solid grey, NO left accent ── */
.rrow.hi {{
    background:    rgba(67, 76, 94, 0.70);
    border-radius: 10px;
    border-left:   2px solid transparent;
}}

.ricon {{
    margin-right: 12px;
}}

/* Name only — no description */
.rname {{
    color:       #E5E9F0;
    font-size:   13px;
    font-weight: 400;
    font-family: 'Inter', 'Cantarell', sans-serif;
}}
.rname.muted {{ color: #81A1C1; }}

/* Calculator result row */
.calc-result-name {{
    color:       #A3BE8C;
    font-size:   15px;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.5px;
}}
.calc-sub {{
    color:       #4C566A;
    font-size:   10px;
    font-family: 'Inter', 'Cantarell', sans-serif;
    margin-top:  1px;
}}

/* File path subtitle */
.file-sub {{
    color:       #4C566A;
    font-size:   10px;
    font-family: 'Inter', 'Cantarell', sans-serif;
    margin-top:  1px;
}}

/* ── Scrollbar ── */
scrollbar              {{ background: transparent; min-width: 4px; }}
scrollbar slider       {{ background-color: rgba(67,76,94,0.60); border-radius: 999px;
                          min-width: 3px; min-height: 16px; }}
scrolledwindow         {{ background: transparent; }}
"""

_KIND_ORDER = {"calc": 0, "run": 1, "app": 2, "file": 3, "web": 4}

_FALLBACK = {
    "app": "application-x-executable",
    "calc": "accessories-calculator",
    "web": "applications-internet",
    "run": "utilities-terminal",
    "file": "text-x-generic",
}

ASSET_DIR = Path.home() / ".config/nord-launch/assets"

_FILE_ICON_ASSETS: dict[str, str] = {
    ".3ds": "3ds-svgrepo-com.svg",
    ".ai": "ai-ai-svgrepo-com.svg",
    ".avi": "avi-svgrepo-com.svg",
    ".bmp": "bmp-svgrepo-com.svg",
    ".cad": "cad-svgrepo-com.svg",
    ".cdr": "cdr-svgrepo-com.svg",
    ".dat": "dat-svgrepo-com.svg",
    ".dll": "dll-svgrepo-com.svg",
    ".dmg": "dmg-svgrepo-com.svg",
    ".doc": "doc-svgrepo-com.svg",
    ".eps": "eps-svgrepo-com.svg",
    ".fla": "fla-svgrepo-com.svg",
    ".flv": "flv-svgrepo-com.svg",
    ".gif": "gif-svgrepo-com.svg",
    ".indd": "indd-svgrepo-com.svg",
    ".iso": "iso-svgrepo-com.svg",
    ".jpg": "jpg-svgrepo-com.svg",
    ".jpeg": "jpg-svgrepo-com.svg",
    ".midi": "midi-svgrepo-com.svg",
    ".mp3": "mp3-svgrepo-com.svg",
    ".pdf": "pdf-svgrepo-com.svg",
    ".png": "png-svgrepo-com.svg",
    ".ppt": "ppt-svgrepo-com.svg",
    ".psd": "psd-svgrepo-com.svg",
    ".raw": "raw-svgrepo-com.svg",
    ".sql": "sql-svgrepo-com.svg",
    ".svg": "svg-svgrepo-com.svg",
    ".tif": "tif-svgrepo-com.svg",
    ".tiff": "tif-svgrepo-com.svg",
    ".txt": "txt-svgrepo-com.svg",
    ".wmv": "wmv-svgrepo-com.svg",
    ".xml": "xml-svgrepo-com.svg",
    ".zip": "zip-svgrepo-com.svg",
    ".py": "PYTHON.svg",
    ".lua": "LUA.svg",
    ".js": "JS.svg",
    ".php": "PHP.svg",
    ".java": "JAVA.svg",
    ".c": "C.svg",
    ".cpp": "C++.svg",
    ".cc": "C++.svg",
    ".cxx": "C++.svg",
    ".h": "C.svg",
    ".hpp": "C++.svg",
}

_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}

_EXT_ICON: dict[str, str] = {
    ".aep": "text-x-generic",
    ".ai": "image-x-generic",
    ".avi": "video-x-generic",
    ".bin": "application-x-executable",
    ".c4d": "application-x-executable",
    ".cdr": "image-x-generic",
    ".css": "text-x-css",
    ".dll": "application-x-executable",
    ".dwt": "text-x-generic",
    ".epub": "application-epub+zip",
    ".html": "text-html",
    ".ico": "image-x-generic",
    ".jpg": "image-x-generic",
    ".jpeg": "image-x-generic",
    ".m3u": "audio-x-generic",
    ".max": "application-x-executable",
    ".mp4": "video-x-generic",
    ".mpeg": "video-x-generic",
    ".mpg": "video-x-generic",
    ".obj": "application-x-executable",
    ".odt": "x-office-document",
    ".pdf": "application-pdf",
    ".png": "image-x-generic",
    ".proj": "text-x-generic",
    ".psd": "image-x-generic",
    ".tif": "image-x-generic",
    ".tiff": "image-x-generic",
    ".wmv": "video-x-generic",
    ".xls": "x-office-spreadsheet",
}


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


# ─────────────────────────────────────────────────────────────
# App indexer
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
# File indexer — home only, no hidden dirs/files
# ─────────────────────────────────────────────────────────────
class FileIndexer:
    """
    Walks $HOME in a background thread.
    Skips any directory or file whose name starts with '.'.
    Stores (filename_lower, filename, full_path) tuples for fast search.
    """

    _MAX_FILES = 150_000

    def __init__(self):
        self._entries: list[tuple[str, str, str]] = []
        self._ready = False
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        home = Path.home()
        entries: list[tuple[str, str, str]] = []
        try:
            for root, dirs, files in os.walk(home, topdown=True, followlinks=False):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for fname in files:
                    if fname.startswith("."):
                        continue
                    entries.append((fname.lower(), fname, os.path.join(root, fname)))
                    if len(entries) >= self._MAX_FILES:
                        break
                if len(entries) >= self._MAX_FILES:
                    break
        except Exception:
            pass

        self._entries = entries
        self._ready = True

    def search(self, q: str, limit: int = 4) -> list[Result]:
        if not self._ready or len(q) < 2:
            return []

        ql = q.lower()
        out: list[tuple[int, str, str]] = []

        for nl, name, path in self._entries:
            if nl == ql:
                score = 200
            elif nl.startswith(ql):
                score = 150
            elif ql in nl:
                score = 80
            else:
                continue
            out.append((score, name, path))

        out.sort(key=lambda t: -t[0])

        results: list[Result] = []
        for score, name, path in out[:limit]:
            parent = Path(path).parent
            try:
                rel = "~/" + str(parent.relative_to(Path.home()))
            except ValueError:
                rel = str(parent)

            suffix = Path(name).suffix.lower()
            icon_path = _FILE_ICON_ASSETS.get(suffix)

            if icon_path is not None:
                asset = ASSET_DIR / icon_path
                icon = (
                    str(asset)
                    if asset.is_file()
                    else _EXT_ICON.get(suffix, "text-x-generic")
                )
            else:
                icon = _EXT_ICON.get(suffix, "text-x-generic")

            results.append(
                Result(
                    name=name,
                    desc=rel,
                    kind="file",
                    icon=icon,
                    cmd=path,
                    score=score,
                )
            )

        return results


# ─────────────────────────────────────────────────────────────
# Calculator
# ─────────────────────────────────────────────────────────────
_MATH_RE = re.compile(r"[\d].*[\+\-\*\/\^%]|[\+\-\*\/\^%].*\d")
_SAFE_RE = re.compile(r"^[\d\s\+\-\*\/\(\)\.\,\^%sqrtpielog\!]+$", re.I)


def calc_eval(expr: str) -> Optional[str]:
    expr = expr.strip()
    if not _MATH_RE.search(expr) or not _SAFE_RE.match(expr):
        return None

    try:
        s = expr.replace("^", "**").replace(",", ".")
        for fn, rep in [
            ("sqrt", "math.sqrt"),
            ("sin", "math.sin"),
            ("cos", "math.cos"),
            ("tan", "math.tan"),
            ("ln", "math.log"),
            ("log", "math.log10"),
            ("pi", "math.pi"),
            ("e", "math.e"),
        ]:
            s = re.sub(rf"\b{fn}\b", rep, s)

        result = eval(s, {"__builtins__": {}, "math": math})
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                return str(int(result))
            return f"{result:.8g}"
        return str(result)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────────────────────
class NordLaunch(Gtk.ApplicationWindow):
    WIDTH = 620
    MAX_ROWS = 8

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("nord-launch")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(self.WIDTH, -1)
        self.remove_css_class("csd")
        self.remove_css_class("solid-csd")

        self._indexer = app.indexer
        self._file_indexer = app.file_indexer
        self._results: list[Result] = []
        self._active = -1

        self._load_css()
        self._build()
        self._setup_input()

    def _load_css(self):
        p = Gtk.CssProvider()
        p.load_from_data(CSS.encode())
        d = Gdk.Display.get_default()
        if d:
            Gtk.StyleContext.add_provider_for_display(
                d, p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def _build(self):
        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        shell.add_css_class("shell")
        self.set_child(shell)
        shell.append(self._build_search())
        shell.append(self._build_hdiv())
        shell.append(self._build_body())

    def _build_search(self) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        row.add_css_class("search-row")
        row.set_valign(Gtk.Align.CENTER)

        ico = Gtk.Image.new_from_icon_name("system-search-symbolic")
        ico.set_pixel_size(16)
        ico.add_css_class("search-icon")
        ico.set_valign(Gtk.Align.CENTER)
        row.append(ico)

        self._entry = Gtk.Entry()
        self._entry.set_css_name("searchfield")
        self._entry.add_css_class("search-entry")
        self._entry.add_css_class("flat")
        self._entry.set_has_frame(False)
        self._entry.set_hexpand(True)
        self._entry.set_valign(Gtk.Align.CENTER)
        self._entry.set_placeholder_text("Spotlight Search")
        self._entry.connect("changed", self._on_changed)
        row.append(self._entry)
        return row

    def _build_hdiv(self) -> Gtk.Box:
        self._hdiv = Gtk.Box()
        self._hdiv.add_css_class("hdiv")
        self._hdiv.set_visible(False)
        return self._hdiv

    def _build_body(self) -> Gtk.Box:
        self._body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._body.set_visible(False)

        self._listbox = Gtk.ListBox()
        self._listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self._listbox.set_activate_on_single_click(True)
        self._listbox.connect("row-activated", self._on_row_click)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_max_content_height(320)
        scroll.set_propagate_natural_height(True)
        scroll.set_child(self._listbox)
        self._body.append(scroll)

        return self._body

    def _setup_input(self):
        self._entry.connect("activate", lambda _: self._launch(self._active))
        kc = Gtk.EventControllerKey()
        kc.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        kc.connect("key-pressed", self._on_key)
        self._entry.add_controller(kc)

    def _on_key(self, _c, kv, _kc, _st) -> bool:
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

    def _on_changed(self, _e):
        self._rebuild(self._entry.get_text().strip())

    def _rebuild(self, query: str):
        while row := self._listbox.get_row_at_index(0):
            self._listbox.remove(row)

        self._results.clear()
        self._active = -1

        show = bool(query)
        self._hdiv.set_visible(show)
        self._body.set_visible(show)
        if not show:
            return

        results: list[Result] = []

        val = calc_eval(query)
        if val is not None:
            results.append(
                Result(
                    name=f"= {val}",
                    desc="Copy to clipboard",
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
                    name=raw,
                    desc="Execute in shell",
                    kind="run",
                    icon="utilities-terminal",
                    cmd=raw,
                    score=900,
                )
            )

        results.extend(self._indexer.search(query))
        results.extend(self._file_indexer.search(query))

        q_enc = query.replace(" ", "+")
        results.append(
            Result(
                name=f'Search "{query}"',
                desc="google.com",
                kind="web",
                icon="applications-internet",
                cmd=f"https://www.google.com/search?q={q_enc}",
                score=1,
            )
        )

        results.sort(key=lambda r: (_KIND_ORDER.get(r.kind, 99), -r.score))
        self._results = results[: self.MAX_ROWS]

        for r in self._results:
            self._listbox.append(self._make_row(r))

        self._set_active(0)

    def _make_row(self, r: Result) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add_css_class("rrow")
        box.set_valign(Gtk.Align.CENTER)

        size = 26 if r.kind == "calc" else 30
        ico = Gtk.Image()
        ico.set_pixel_size(size)
        ico.add_css_class("ricon")
        ico.set_valign(Gtk.Align.CENTER)
        self._apply_icon(ico, r, size=size)
        box.append(ico)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        text.set_hexpand(True)
        text.set_valign(Gtk.Align.CENTER)

        if r.kind == "calc":
            name_lbl = Gtk.Label(label=r.name)
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(30)
            name_lbl.add_css_class("calc-result-name")
            text.append(name_lbl)

            sub = Gtk.Label(label=r.desc)
            sub.set_halign(Gtk.Align.START)
            sub.add_css_class("calc-sub")
            text.append(sub)

        elif r.kind == "file":
            name_lbl = Gtk.Label(label=r.name)
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(34)
            name_lbl.add_css_class("rname")
            text.append(name_lbl)

            path_lbl = Gtk.Label(label=r.desc)
            path_lbl.set_halign(Gtk.Align.START)
            path_lbl.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            path_lbl.set_max_width_chars(44)
            path_lbl.add_css_class("file-sub")
            text.append(path_lbl)

        else:
            name_lbl = Gtk.Label(label=r.name)
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(34)
            name_lbl.add_css_class("rname")
            if r.kind == "web":
                name_lbl.add_css_class("muted")
            text.append(name_lbl)

        box.append(text)
        row.set_child(box)
        return row

    def _apply_icon(self, widget: Gtk.Image, r: Result, size: int = 30):
        widget.set_pixel_size(size)

        if r.icon.startswith("/") and Path(r.icon).exists():
            widget.set_from_file(r.icon)
            return

        if r.kind == "file":
            ext = Path(r.cmd).suffix.lower()
            if ext in _FILE_ICON_ASSETS:
                asset_path = ASSET_DIR / _FILE_ICON_ASSETS[ext]
                if asset_path.exists():
                    widget.set_from_file(str(asset_path))
                    return

            widget.set_from_icon_name(
                _EXT_ICON.get(ext, _FALLBACK.get(r.kind, "text-x-generic"))
            )
            return

        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        name = (
            r.icon
            if theme.has_icon(r.icon)
            else _FALLBACK.get(r.kind, "application-x-executable")
        )
        widget.set_from_icon_name(name)

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

    def _on_row_click(self, _lb, row):
        self._launch(row.get_index())

    def _is_image_file(self, path: str) -> bool:
        return Path(path).suffix.lower() in _IMAGE_EXTS

    def _launch_file(self, path: str):
        ext = Path(path).suffix.lower()
        if ext in _IMAGE_EXTS:
            opener = shutil.which("imv")
            if opener:
                subprocess.Popen(
                    [opener, path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return

        subprocess.Popen(
            ["xdg-open", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    def _launch(self, idx: int):
        if not (0 <= idx < len(self._results)):
            return

        r = self._results[idx]

        if r.kind == "calc":
            wlcopy = shutil.which("wl-copy")
            if wlcopy:
                subprocess.run(
                    [wlcopy, r.copy_val],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            self.close()
            return

        if r.kind == "app":
            try:
                if r.desktop_path:
                    appinfo = Gio.DesktopAppInfo.new_from_filename(r.desktop_path)
                    if appinfo and appinfo.launch([], None):
                        self.close()
                        return
            except Exception:
                pass

            if r.cmd:
                subprocess.Popen(
                    r.cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            self.close()
            return

        if r.kind == "file":
            self._launch_file(r.cmd)
            self.close()
            return

        if r.kind == "web":
            subprocess.Popen(
                ["xdg-open", r.cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self.close()
            return

        if r.kind == "run":
            subprocess.Popen(
                r.cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            self.close()
            return


# ─────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────
class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="dev.rmustard.nordlaunch")
        self.indexer = AppIndexer()
        self.file_indexer = FileIndexer()

    def do_activate(self):
        NordLaunch(self).present()


if __name__ == "__main__":
    import sys

    App().run(sys.argv)
