#!/usr/bin/env python3
"""
Start Menu · Hyprland · Nord
  ↑↓ / j k    navigate      h / l   switch panel
  Tab          switch        Enter   launch
  Alt_L        power menu    Esc     back / close
  Confirm:  h=Yes  l=No  Enter=confirm
"""

import configparser
import glob
import os
import pwd
import subprocess
import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, GLib, Gtk, Pango

HAS_LS = False
LS = None
try:
    gi.require_version("Gtk4LayerShell", "1.0")
    from gi.repository import Gtk4LayerShell as LS

    HAS_LS = True
except (ValueError, ImportError):
    try:
        gi.require_version("GtkLayerShell", "0.1")
        from gi.repository import GtkLayerShell as LS

        HAS_LS = True
    except (ValueError, ImportError):
        pass

WIN_W = 680
WIN_H = 490
SIDEBAR_W = 158
WAYBAR_H = 34
MARGIN_TOP_EXTRA = 20
MARGIN = 6

N0 = "#2E3440"
N1 = "#3B4252"
N2 = "#434C5E"
N3 = "#4C566A"
N4 = "#D8DEE9"
N5 = "#E5E9F0"
N6 = "#ECEFF4"
DIM = "#5E6E85"
CYN = "#88C0D0"
BLU = "#81A1C1"
RED = "#BF616A"
ORG = "#D08770"
YEL = "#EBCB8B"
PUR = "#B48EAD"


def mk_css():
    return f"""
@define-color window_bg_color         {N0};
@define-color window_fg_color         {N6};
@define-color view_bg_color           {N0};
@define-color view_fg_color           {N6};
@define-color card_bg_color           {N1};
@define-color card_fg_color           {N6};
@define-color popover_bg_color        {N1};
@define-color popover_fg_color        {N6};
@define-color sidebar_bg_color        {N1};
@define-color sidebar_fg_color        {N5};
@define-color headerbar_bg_color      {N1};
@define-color headerbar_fg_color      {N6};
@define-color accent_color            {CYN};
@define-color accent_bg_color         {CYN};
@define-color accent_fg_color         {N0};
@define-color theme_selected_bg_color {CYN};
@define-color theme_selected_fg_color {N0};
@define-color theme_bg_color          {N1};
@define-color theme_fg_color          {N6};
@define-color theme_base_color        {N0};
@define-color theme_text_color        {N6};
@define-color error_color             {RED};
@define-color success_color           {GRN};
@define-color warning_color           {YEL};

window {{ background:transparent; }}

@keyframes open  {{ from{{opacity:0;margin-left:-16px}} to{{opacity:1;margin-left:{MARGIN}px}} }}
@keyframes close {{ from{{opacity:1;margin-left:{MARGIN}px}} to{{opacity:0;margin-left:-16px}} }}

.card {{
    background-color:{N0};
    border-radius:10px;
    border:1px solid {N2};
    box-shadow:0 20px 60px rgba(0,0,0,.65),0 4px 12px rgba(0,0,0,.30);
    animation:open 180ms cubic-bezier(.22,1,.36,1) both;
}}
.card.closing {{ animation:close 120ms ease-in both; }}

.sidebar {{
    background-color:{N1};
    border-right:1px solid {N2};
    border-radius:10px 0 0 10px;
    padding:8px 4px 6px;
}}
.slbl {{
    color:{DIM}; font-size:9px; font-weight:800;
    letter-spacing:1.3px; padding:4px 10px 3px 9px;
}}
.sw {{
    background-color:{N0}; border:1px solid {N3};
    border-radius:7px; margin:6px 6px 4px; padding:0 8px;
    transition:border-color 140ms, box-shadow 140ms;
}}
.sw:focus-within {{ border-color:{CYN}; box-shadow:0 0 0 2px {CYN}22; }}
.sico {{ color:{DIM}; font-size:12px; margin-right:5px; }}

entry, entry:focus {{
    background:none !important; background-color:transparent !important;
    color:{N6} !important; border:none !important;
    box-shadow:none !important; outline:none !important;
    padding:7px 0; font-size:12.5px; caret-color:{CYN}; min-width:0;
}}
entry > text {{ color:{N6} !important; caret-color:{CYN} !important; }}
entry > text > placeholder {{ color:{DIM} !important; opacity:1; }}
entry undershoot.left, entry undershoot.right {{ background:none !important; }}
entry selection {{ background-color:{CYN}44 !important; color:{N6} !important; }}

list.cats {{
    background:none !important; background-color:transparent !important;
    padding:0 3px;
}}
list.cats > row {{
    background:none !important; background-color:transparent !important;
    border-radius:7px; margin:1px 0; min-height:0;
    border:none !important; outline:none !important; box-shadow:none !important;
    transition:background-color 90ms;
}}
list.cats > row:hover          {{ background-color:{N2} !important; }}
list.cats > row:selected       {{ background-color:{N2} !important; outline:none !important; box-shadow:none !important; }}
list.cats > row:selected:focus {{ background-color:{N2} !important; outline:none !important; box-shadow:none !important; }}
list.cats.on > row:selected    {{
    background:linear-gradient(90deg,{CYN}2C 0%,{N2} 72%) !important;
    border-left:2px solid {CYN} !important;
}}
.cico {{ color:{DIM}; font-size:13px; min-width:18px; }}
.cnam {{ color:{N4}; font-size:12px; font-weight:500; padding:5px 4px; }}
list.cats > row:selected .cico {{ color:{CYN}; }}
list.cats > row:selected .cnam {{ color:{N6}; font-weight:600; }}

.apanel {{ background-color:{N0}; border-radius:0 10px 0 0; }}
.ahdr {{ padding:9px 13px 6px; border-bottom:1px solid {N1}; }}
.atitle {{ color:{DIM}; font-size:9px; font-weight:800; letter-spacing:1.3px; }}
.acnt   {{ color:{N3}; font-size:9px; }}

list.apps {{
    background:none !important; background-color:transparent !important;
}}
list.apps > row {{
    background:none !important; background-color:transparent !important;
    border-radius:7px; margin:1px 5px;
    border:none !important; outline:none !important;
    transition:background-color 80ms;
}}
list.apps > row:hover          {{ background-color:{N1} !important; }}
list.apps > row:selected       {{ background-color:{N2} !important; outline:none !important; box-shadow:none !important; }}
list.apps > row:selected:focus {{ background-color:{N2} !important; outline:none !important; box-shadow:none !important; }}
list.apps.on > row:selected    {{
    background:linear-gradient(90deg,{CYN}1E 0%,{N2} 68%) !important;
    border-left:2px solid {CYN} !important;
}}
.anam  {{ color:{N6}; font-size:13px; font-weight:500; }}
.adesc {{ color:{DIM}; font-size:11px; }}
.abadge {{
    color:{N3}; font-size:9px; font-weight:700;
    background-color:{N1}; border-radius:4px; padding:1px 5px;
}}

.powpanel {{ background-color:{N0}; border-radius:0 10px 0 0; }}
.powhint  {{ color:{DIM}; font-size:9px; font-family:monospace; }}
.pcard {{
    background-color:{N1}; border-radius:9px; border:1px solid {N2};
    padding:18px 10px 14px; margin:5px; min-width:110px;
    transition:background-color 110ms, border-color 110ms;
}}
.pcard:hover {{ background-color:{N2}; border-color:{N3}; }}
.pcard.psel  {{ background-color:{N2}; border-color:{CYN}; box-shadow:0 0 0 1px {CYN}44; }}
.pico {{ font-size:26px; }}
.pnam {{ color:{N5}; font-size:12px; font-weight:600; margin-top:6px; }}
.pdsc {{ color:{DIM}; font-size:10px; margin-top:1px; }}
.pc-lock    .pico {{ color:{BLU}; }}
.pc-logout  .pico {{ color:{ORG}; }}
.pc-suspend .pico {{ color:{PUR}; }}
.pc-reboot  .pico {{ color:{YEL}; }}
.pc-off     .pico {{ color:{RED}; }}

.btm {{
    background-color:{N1}; border-top:1px solid {N2};
    border-radius:0 0 10px 10px; padding:7px 11px;
}}
.unam  {{ color:{N6}; font-size:13px; font-weight:700; }}
.uhost {{ color:{DIM}; font-size:10.5px; }}
.hk    {{ color:{CYN}; font-size:9px; font-weight:700; font-family:monospace; }}
.hd    {{ color:{N3}; font-size:9px; }}

button.pbtn {{
    background:transparent !important; background-color:transparent !important;
    border:1px solid {N2} !important; border-radius:7px;
    padding:5px 9px; color:{DIM}; font-size:14px;
    min-width:0; min-height:0; box-shadow:none !important;
    transition:all 100ms;
}}
button.pbtn:hover {{ background-color:{N2} !important; border-color:{RED}66 !important; color:{RED}; }}

.cfmbg   {{ background-color:rgba(46,52,64,.85) !important; border-radius:10px; }}
.cfmcard {{
    background-color:{N1} !important; border-radius:11px;
    border:1px solid {N3}; box-shadow:0 28px 80px rgba(0,0,0,.80);
}}
.cfmico  {{ color:{RED}; font-size:30px; padding:22px 22px 4px; }}
.cfmttl  {{ color:{N6}; font-size:15px; font-weight:700; padding:0 22px 4px; }}
.cfmsub  {{ color:{DIM}; font-size:11.5px; padding:0 22px 6px; }}
.cfmhint {{ color:{DIM}; font-size:9px; font-family:monospace; padding:0 22px 16px; }}
.cfmsep  {{ background-color:{N2}; min-height:1px; }}
button.cfmyes {{
    background-color:{RED} !important; color:{N6} !important;
    border:none !important; border-radius:0 0 0 10px;
    padding:13px 0; font-size:13px; font-weight:600; min-height:0;
    box-shadow:none !important; transition:background-color 100ms;
}}
button.cfmyes:hover {{ background-color:#C85060 !important; }}
button.cfmyes.sel   {{ background-color:#C85060 !important; }}
button.cfmno {{
    background-color:{N2} !important; color:{N4} !important;
    border:none !important; border-left:1px solid {N3} !important;
    border-radius:0 0 10px 0; padding:13px 0; font-size:13px; min-height:0;
    box-shadow:none !important; transition:background-color 100ms;
}}
button.cfmno:hover {{ background-color:{N3} !important; color:{N6} !important; }}
button.cfmno.sel   {{ background-color:{N3} !important; color:{N6} !important; }}

scrollbar {{ background:transparent; min-width:4px; }}
scrollbar slider {{
    background-color:{N2}; border-radius:4px;
    min-width:4px; min-height:20px; margin:2px;
}}
scrollbar slider:hover {{ background-color:{CYN}; }}
"""


CATS = [
    ("All", "󰣆", None),
    ("Internet", "󰖟", ["Network", "WebBrowser", "Email", "InstantMessaging", "Chat"]),
    (
        "Multimedia",
        "󰝚",
        ["AudioVideo", "Audio", "Video", "Music", "Player", "Recorder"],
    ),
    ("Dev", "󰘦", ["Development", "IDE", "Debugger", "WebDevelopment"]),
    ("Graphics", "󰏘", ["Graphics", "Photography", "2DGraphics", "3DGraphics"]),
    ("Office", "󱉟", ["Office", "WordProcessor", "Spreadsheet", "Presentation"]),
    ("Games", "󰊗", ["Game", "ActionGame", "AdventureGame", "Emulator"]),
    ("System", "󱁿", ["System", "Monitor", "TerminalEmulator", "FileManager"]),
    ("Settings", "󰒓", ["Settings", "HardwareSettings", "PackageManager"]),
    ("Other", "󰏗", []),
]
POWER = [
    ("󰌾", "Lock", "pc-lock", "Lock screen", "loginctl lock-session", False),
    ("󰍃", "Log Out", "pc-logout", "End session", "hyprctl dispatch exit", False),
    ("󰒲", "Suspend", "pc-suspend", "Sleep", "systemctl suspend", False),
    ("󰜉", "Reboot", "pc-reboot", "Restart", "systemctl reboot --no-wall", True),
    ("󰐥", "Shutdown", "pc-off", "Power off", "systemctl poweroff --no-wall", True),
]


def _getcat(cats):
    for n, _, k in CATS:
        if k and cats.intersection(k):
            return n
    return "Other"


def load_apps():
    dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/flatpak/exports/share/applications",
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
    ]
    apps, seen = [], set()
    for d in dirs:
        for p in glob.glob(f"{d}/*.desktop"):
            try:
                c = configparser.ConfigParser(interpolation=None, strict=False)
                c.read(p, encoding="utf-8")
                if "Desktop Entry" not in c:
                    continue
                e = c["Desktop Entry"]
                if e.get("Type", "") != "Application":
                    continue
                if e.get("NoDisplay", "false").lower() == "true":
                    continue
                if e.get("Hidden", "false").lower() == "true":
                    continue
                nm = e.get("Name", "").strip()
                if not nm or nm in seen:
                    continue
                seen.add(nm)
                cats = {
                    x.strip() for x in e.get("Categories", "").split(";") if x.strip()
                }
                apps.append(
                    dict(
                        name=nm,
                        desc=e.get("Comment", "").strip(),
                        exec=e.get("Exec", "").strip(),
                        icon=e.get("Icon", "").strip(),
                        cat=_getcat(cats),
                    )
                )
            except Exception:
                continue
    return sorted(apps, key=lambda a: a["name"].lower())


def spawn(cmd):
    subprocess.Popen(
        cmd.split("%")[0].strip(),
        shell=True,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class Menu(Gtk.ApplicationWindow):
    def __init__(self, ga):
        super().__init__(application=ga, title="Start Menu")
        self.set_decorated(False)
        self.set_resizable(False)
        self._apps = load_apps()
        self._cat = "All"
        self._q = ""
        self._area = "apps"
        self._pm = False
        self._pidx = 0
        self._pbtns = []
        self._cfm = False
        self._cfmcmd = ""
        self._cfmfoc = 1
        self._layer()
        self._css()
        self._build()
        self._fill()
        self._keybind()
        self._sync()

    def _layer(self):
        if not HAS_LS:
            self.set_default_size(WIN_W, WIN_H)
            return
        LS.init_for_window(self)
        LS.set_layer(self, LS.Layer.TOP)
        for e in (LS.Edge.LEFT, LS.Edge.TOP, LS.Edge.RIGHT, LS.Edge.BOTTOM):
            LS.set_anchor(self, e, True)
        LS.set_exclusive_zone(self, -1)
        LS.set_keyboard_mode(self, LS.KeyboardMode.EXCLUSIVE)

    def _css(self):
        # Force dark theme so Adwaita starts from a dark baseline
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-application-prefer-dark-theme", True)
        p = Gtk.CssProvider()
        p.load_from_data(mk_css().encode())
        # Priority 800 = STYLE_PROVIDER_PRIORITY_USER (highest)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), p, 800)

    def _keybind(self):
        k = Gtk.EventControllerKey()
        k.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        k.connect("key-pressed", self._key)
        self.add_controller(k)

    def _key(self, _, kv, __, ___):
        # ── confirm open ──
        if self._cfm:
            if kv == Gdk.KEY_Escape:
                self._chide()
                return True
            if kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                (self._cyes if self._cfmfoc == 0 else self._chide)()
                return True
            if kv in (ord("h"), Gdk.KEY_Left):
                self._cfoc(0)
                return True
            if kv in (ord("l"), Gdk.KEY_Right):
                self._cfoc(1)
                return True
            return True
        # ── global ──
        if kv == Gdk.KEY_Escape:
            if self._pm:
                self._pmshow(False)
                return True
            if self._search.get_text():
                self._search.set_text("")
                return True
            self._close()
            return True
        if kv in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
            self._pmshow(not self._pm)
            return True
        if kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self._pm:
                self._pmrun(self._pidx)
            elif self._area == "apps":
                r = self._alist.get_selected_row()
                if r and hasattr(r, "_app"):
                    spawn(r._app["exec"])
                    self._close()
            else:
                self._setarea("apps")
            return True
        # ── power nav ──
        if self._pm:
            n = len(POWER)
            if kv in (ord("j"), ord("l"), Gdk.KEY_Down, Gdk.KEY_Right):
                self._pidx = (self._pidx + 1) % n
                self._pmref()
                return True
            if kv in (ord("k"), ord("h"), Gdk.KEY_Up, Gdk.KEY_Left):
                self._pidx = (self._pidx - 1) % n
                self._pmref()
                return True
            return True
        # ── normal nav ──
        if kv == Gdk.KEY_Tab:
            self._setarea("cats" if self._area == "apps" else "apps")
            return True
        if kv == Gdk.KEY_Up:
            self._move(-1)
            return True
        if kv == Gdk.KEY_Down:
            self._move(+1)
            return True
        if not self._search.has_focus():
            if kv in (ord("h"), Gdk.KEY_Left):
                self._setarea("cats")
                return True
            if kv in (ord("l"), Gdk.KEY_Right):
                self._setarea("apps")
                return True
            if kv == ord("k"):
                self._move(-1)
                return True
            if kv == ord("j"):
                self._move(+1)
                return True
        return False

    def _setarea(self, a):
        self._area = a
        self._sync()
        if a == "cats":
            self._clist.grab_focus()
            if not self._clist.get_selected_row():
                self._clist.select_row(self._clist.get_row_at_index(0))
        else:
            self._alist.grab_focus()
            if not self._alist.get_selected_row():
                self._alist.select_row(self._alist.get_row_at_index(0))

    def _sync(self):
        if self._area == "cats":
            self._clist.add_css_class("on")
            self._alist.remove_css_class("on")
        else:
            self._alist.add_css_class("on")
            self._clist.remove_css_class("on")

    def _move(self, d):
        lb = self._clist if self._area == "cats" else self._alist
        sel = lb.get_selected_row()
        idx = max(0, (sel.get_index() if sel else -1) + d)
        r = lb.get_row_at_index(idx)
        if r:
            lb.select_row(r)
            r.grab_focus()

    def _pmshow(self, on):
        self._pm = on
        self._stack.set_visible_child_name("pow" if on else "main")
        if on:
            self._pidx = 0
            self._pmref()
        else:
            self._setarea(self._area)

    def _pmref(self):
        for i, b in enumerate(self._pbtns):
            (b.add_css_class if i == self._pidx else b.remove_css_class)("psel")

    def _pmrun(self, idx):
        ico, lbl, _, __, cmd, cfm = POWER[idx]
        if cfm:
            self._cshow(lbl, ico, cmd)
        else:
            self.close()
            spawn(cmd)

    # ── Confirm ──
    def _cshow(self, lbl, ico, cmd):
        self._cfmcmd = cmd
        self._cfmico_w.set_label(ico)
        self._cfmttl_w.set_label(lbl)
        self._cfmsub_w.set_label(f"Are you sure you want to {lbl.lower()}?")
        self._cfmyes_w.set_label(f"Yes, {lbl}")
        self._cfoc(1)
        self._cfm = True
        self._cfmbg.set_visible(True)

    def _chide(self):
        self._cfm = False
        self._cfmbg.set_visible(False)

    def _cfoc(self, f):
        self._cfmfoc = f
        if f == 0:
            self._cfmyes_w.add_css_class("sel")
            self._cfmno_w.remove_css_class("sel")
        else:
            self._cfmno_w.add_css_class("sel")
            self._cfmyes_w.remove_css_class("sel")

    def _cyes(self):
        cmd = self._cfmcmd
        self._chide()
        self.close()
        spawn(cmd)

    # ── Build ──
    def _build(self):
        root = Gtk.Box()
        root.set_hexpand(True)
        root.set_vexpand(True)
        self.set_child(root)
        ov = Gtk.Overlay()
        ov.add_css_class("card")
        ov.set_size_request(WIN_W, WIN_H)
        ov.set_halign(Gtk.Align.START)
        ov.set_valign(Gtk.Align.START)
        ov.set_margin_start(MARGIN)
        ov.set_margin_top(WAYBAR_H + MARGIN_TOP_EXTRA + MARGIN)
        root.append(ov)
        self._ov = ov

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        ov.set_child(main)
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        body.set_vexpand(True)
        main.append(body)
        self._mksb(body)
        self._stack = Gtk.Stack()
        self._stack.set_hexpand(True)
        self._stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._stack.set_transition_duration(100)
        body.append(self._stack)
        self._mkapps()
        self._mkpow()
        self._mkbtm(main)
        self._mkcfm()
        ov.add_overlay(self._cfmbg)

    def _mksb(self, parent):
        sb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sb.add_css_class("sidebar")
        sb.set_size_request(SIDEBAR_W, -1)
        parent.append(sb)
        # search
        sw = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        sw.add_css_class("sw")
        ic = Gtk.Label(label="")
        ic.add_css_class("sico")
        self._search = Gtk.Entry()
        self._search.set_placeholder_text("Search apps…")
        self._search.set_hexpand(True)
        self._search.connect(
            "changed",
            lambda e: (setattr(self, "_q", e.get_text().strip()), self._fill()),
        )
        self._search.connect("activate", lambda _: self._setarea("apps"))
        sw.append(ic)
        sw.append(self._search)
        sb.append(sw)
        # cats label
        lbl = Gtk.Label(label="CATEGORIES")
        lbl.add_css_class("slbl")
        lbl.set_xalign(0)
        sb.append(lbl)
        # cat list
        self._clist = Gtk.ListBox()
        self._clist.add_css_class("cats")
        self._clist.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._clist.set_activate_on_single_click(True)
        sb.append(self._clist)
        for name, icon, _ in CATS:
            row = Gtk.ListBoxRow()
            row._cat = name
            bx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            bx.set_margin_top(1)
            bx.set_margin_bottom(1)
            bx.set_margin_start(8)
            bx.set_margin_end(5)
            ci = Gtk.Label(label=icon)
            ci.add_css_class("cico")
            ci.set_valign(Gtk.Align.CENTER)
            cn = Gtk.Label(label=name)
            cn.add_css_class("cnam")
            cn.set_xalign(0)
            cn.set_hexpand(True)
            bx.append(ci)
            bx.append(cn)
            row.set_child(bx)
            self._clist.append(row)
        self._clist.select_row(self._clist.get_row_at_index(0))
        self._clist.connect("row-selected", self._oncat)
        sp = Gtk.Box()
        sp.set_vexpand(True)
        sb.append(sp)
        ah = Gtk.Label(label="  Alt → power")
        ah.add_css_class("slbl")
        ah.set_xalign(0)
        ah.set_margin_bottom(4)
        sb.append(ah)

    def _mkapps(self):
        p = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        p.add_css_class("apanel")
        self._stack.add_named(p, "main")
        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hdr.add_css_class("ahdr")
        self._atitle = Gtk.Label(label="ALL APPLICATIONS")
        self._atitle.add_css_class("atitle")
        self._atitle.set_xalign(0)
        self._atitle.set_hexpand(True)
        self._acnt = Gtk.Label(label="")
        self._acnt.add_css_class("acnt")
        hdr.append(self._atitle)
        hdr.append(self._acnt)
        p.append(hdr)
        sc = Gtk.ScrolledWindow()
        sc.set_vexpand(True)
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        p.append(sc)
        self._alist = Gtk.ListBox()
        self._alist.add_css_class("apps")
        self._alist.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._alist.set_margin_bottom(4)
        self._alist.connect("row-activated", self._onapp)
        sc.set_child(self._alist)

    def _mkpow(self):
        p = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        p.add_css_class("powpanel")
        self._stack.add_named(p, "pow")
        ctr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        ctr.set_vexpand(True)
        ctr.set_valign(Gtk.Align.CENTER)
        ctr.set_halign(Gtk.Align.CENTER)
        p.append(ctr)
        r1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        r1.set_halign(Gtk.Align.CENTER)
        r2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        r2.set_halign(Gtk.Align.CENTER)
        ctr.append(r1)
        ctr.append(r2)
        for i, (ico, lbl, css, dsc, cmd, cfm) in enumerate(POWER):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            card.add_css_class("pcard")
            card.add_css_class(css)
            card.set_halign(Gtk.Align.CENTER)
            ic = Gtk.Label(label=ico)
            ic.add_css_class("pico")
            ic.set_xalign(0.5)
            nm = Gtk.Label(label=lbl)
            nm.add_css_class("pnam")
            nm.set_xalign(0.5)
            ds = Gtk.Label(label=dsc)
            ds.add_css_class("pdsc")
            ds.set_xalign(0.5)
            card.append(ic)
            card.append(nm)
            card.append(ds)
            gc = Gtk.GestureClick()
            gc.connect(
                "pressed",
                lambda g, n, x, y, _i=i: (
                    setattr(self, "_pidx", _i),
                    self._pmref(),
                    self._pmrun(_i),
                ),
            )
            card.add_controller(gc)
            self._pbtns.append(card)
            (r1 if i < 3 else r2).append(card)
        hint = Gtk.Label(label="h j k l / ←↑↓→  nav   Enter  select   Alt/Esc  back")
        hint.add_css_class("powhint")
        hint.set_margin_top(16)
        ctr.append(hint)

    def _mkbtm(self, parent):
        btm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        btm.add_css_class("btm")
        parent.append(btm)
        try:
            pw = pwd.getpwuid(os.getuid())
            fname = pw.pw_gecos.split(",")[0].strip() or pw.pw_name
            host = os.uname().nodename
        except:
            fname, host = "user", "localhost"
        ub = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        u = Gtk.Label(label=fname)
        u.add_css_class("unam")
        u.set_xalign(0)
        h = Gtk.Label(label=f"@{host}")
        h.add_css_class("uhost")
        h.set_xalign(0)
        ub.append(u)
        ub.append(h)
        btm.append(ub)
        hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        hb.set_hexpand(True)
        hb.set_halign(Gtk.Align.CENTER)
        hb.set_valign(Gtk.Align.CENTER)
        for i, (k, v) in enumerate(
            [
                ("↑↓", "nav"),
                ("h/l", "panel"),
                ("Tab", "switch"),
                ("Enter", "launch"),
                ("Alt", "power"),
                ("Esc", "close"),
            ]
        ):
            if i:
                s = Gtk.Label(label=" · ")
                s.add_css_class("hd")
                hb.append(s)
            kl = Gtk.Label(label=k)
            kl.add_css_class("hk")
            hb.append(kl)
            vl = Gtk.Label(label=f" {v}")
            vl.add_css_class("hd")
            hb.append(vl)
        btm.append(hb)
        pb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        pb.set_valign(Gtk.Align.CENTER)
        for ico, lbl, css, dsc, cmd, cfm in POWER:
            if css not in ("pc-reboot", "pc-off"):
                continue
            btn = Gtk.Button(label=ico)
            btn.add_css_class("pbtn")
            btn.set_tooltip_text(lbl)
            if cfm:
                btn.connect(
                    "clicked", lambda _, lb=lbl, ic=ico, cm=cmd: self._cshow(lb, ic, cm)
                )
            else:
                btn.connect("clicked", lambda _, cm=cmd: (self.close(), spawn(cm)))
            pb.append(btn)
        btm.append(pb)

    def _mkcfm(self):
        self._cfmbg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._cfmbg.add_css_class("cfmbg")
        self._cfmbg.set_hexpand(True)
        self._cfmbg.set_vexpand(True)
        self._cfmbg.set_halign(Gtk.Align.FILL)
        self._cfmbg.set_valign(Gtk.Align.FILL)
        self._cfmbg.set_visible(False)
        dlg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        dlg.add_css_class("cfmcard")
        dlg.set_halign(Gtk.Align.CENTER)
        dlg.set_valign(Gtk.Align.CENTER)
        dlg.set_size_request(285, -1)
        self._cfmbg.append(dlg)
        self._cfmico_w = Gtk.Label()
        self._cfmico_w.add_css_class("cfmico")
        self._cfmico_w.set_xalign(0)
        self._cfmttl_w = Gtk.Label()
        self._cfmttl_w.add_css_class("cfmttl")
        self._cfmttl_w.set_xalign(0)
        self._cfmsub_w = Gtk.Label()
        self._cfmsub_w.add_css_class("cfmsub")
        self._cfmsub_w.set_xalign(0)
        self._cfmsub_w.set_wrap(True)
        cfmh = Gtk.Label(label="h/←  Yes    l/→  No    Enter  confirm    Esc  cancel")
        cfmh.add_css_class("cfmhint")
        cfmh.set_xalign(0)
        dlg.append(self._cfmico_w)
        dlg.append(self._cfmttl_w)
        dlg.append(self._cfmsub_w)
        dlg.append(cfmh)
        sep = Gtk.Separator()
        sep.add_css_class("cfmsep")
        dlg.append(sep)
        br = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        br.set_homogeneous(True)
        self._cfmyes_w = Gtk.Button(label="Yes")
        self._cfmyes_w.add_css_class("cfmyes")
        self._cfmno_w = Gtk.Button(label="Cancel")
        self._cfmno_w.add_css_class("cfmno")
        self._cfmyes_w.connect("clicked", lambda _: self._cyes())
        self._cfmno_w.connect("clicked", lambda _: self._chide())
        br.append(self._cfmyes_w)
        br.append(self._cfmno_w)
        dlg.append(br)

    def _fill(self):
        ch = self._alist.get_first_child()
        while ch:
            nx = ch.get_next_sibling()
            self._alist.remove(ch)
            ch = nx
        q = self._q.lower()
        if q:
            apps = [
                a
                for a in self._apps
                if q in a["name"].lower() or q in a["desc"].lower()
            ]
            self._atitle.set_label(f'"{self._q}"')
        else:
            apps = [
                a for a in self._apps if self._cat == "All" or a["cat"] == self._cat
            ]
            self._atitle.set_label(f"{self._cat.upper()}")
        self._acnt.set_label(str(len(apps)))
        ith = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        for app in apps:
            row = Gtk.ListBoxRow()
            row._app = app
            hb = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hb.set_margin_top(5)
            hb.set_margin_bottom(5)
            hb.set_margin_start(10)
            hb.set_margin_end(10)
            img = Gtk.Image()
            img.set_pixel_size(26)
            if app["icon"] and ith.has_icon(app["icon"]):
                img.set_from_icon_name(app["icon"])
            elif os.path.isabs(app["icon"]) and os.path.exists(app["icon"]):
                img.set_from_file(app["icon"])
            else:
                img.set_from_icon_name("application-x-executable")
            hb.append(img)
            vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vb.set_hexpand(True)
            vb.set_valign(Gtk.Align.CENTER)
            n = Gtk.Label(label=app["name"])
            n.add_css_class("anam")
            n.set_xalign(0)
            n.set_ellipsize(Pango.EllipsizeMode.END)
            vb.append(n)
            if app["desc"]:
                d = Gtk.Label(label=app["desc"])
                d.add_css_class("adesc")
                d.set_xalign(0)
                d.set_ellipsize(Pango.EllipsizeMode.END)
                vb.append(d)
            hb.append(vb)
            if q or self._cat == "All":
                badge = Gtk.Label(label=app["cat"])
                badge.add_css_class("abadge")
                badge.set_valign(Gtk.Align.CENTER)
                hb.append(badge)
            row.set_child(hb)
            self._alist.append(row)
        f = self._alist.get_row_at_index(0)
        if f:
            self._alist.select_row(f)

    def _oncat(self, _, row):
        if not row:
            return
        self._cat = row._cat
        self._q = ""
        self._search.set_text("")
        self._fill()

    def _onapp(self, _, row):
        if hasattr(row, "_app"):
            spawn(row._app["exec"])
            self._close()

    def _close(self):
        self._ov.add_css_class("closing")
        GLib.timeout_add(120, self.close)


PIDFILE = "/tmp/start-menu.pid"


def pid_del():
    try:
        os.unlink(PIDFILE)
    except FileNotFoundError:
        pass


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hyprland.startmenu")

    def do_activate(self):
        w = Menu(self)
        w.connect("destroy", lambda _: pid_del())
        w.present()
        GLib.timeout_add(80, lambda: (w._search.grab_focus(), False))


if __name__ == "__main__":
    import atexit

    atexit.register(pid_del)
    App().run(sys.argv)
