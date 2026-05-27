#!/usr/bin/env python3
"""
start-menu.py — Sleek Start Menu for Hyprland  |  Nord Theme

  ↑↓ / j k      navigate list
  ←→ / h l      switch panel (cats ↔ apps)
  Tab            cycle panels
  Enter          launch / confirm
  Esc            clear → close
  Alt_L          toggle power menu
"""
import gi, sys, os, glob, configparser, pwd, subprocess
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango

# ── Layer Shell ───────────────────────────────────────────────────────────────
HAS_LAYER_SHELL = False; LayerShell = None
try:
    gi.require_version('Gtk4LayerShell','1.0')
    from gi.repository import Gtk4LayerShell as LayerShell; HAS_LAYER_SHELL = True
except (ValueError, ImportError):
    try:
        gi.require_version('GtkLayerShell','0.1')
        from gi.repository import GtkLayerShell as LayerShell; HAS_LAYER_SHELL = True
    except (ValueError, ImportError): pass

# ── Layout ────────────────────────────────────────────────────────────────────
WIN_W = 640; WIN_H = 460; SIDEBAR_W = 148
WAYBAR_H = 34; MARGIN_TOP_EXTRA = 20; MARGIN = 6
ANIM_IN = 180; ANIM_OUT = 130

# ── Nord ──────────────────────────────────────────────────────────────────────
N0="#2E3440"; N1="#3B4252"; N2="#434C5E"; N3="#4C566A"
N4="#D8DEE9"; N5="#E5E9F0"; N6="#ECEFF4"
CYAN="#88C0D0"; BLUE="#81A1C1"; TEAL="#8FBCBB"
RED="#BF616A"; ORG="#D08770"; YEL="#EBCB8B"; GRN="#A3BE8C"; PUR="#B48EAD"
DIM="#6B7A90"

CSS = f"""
window {{ background: transparent; }}

@keyframes slide-in {{
  0%   {{ opacity:0; margin-left:-20px; }}
  100% {{ opacity:1; margin-left:{MARGIN}px; }}
}}
@keyframes slide-out {{
  0%   {{ opacity:1; margin-left:{MARGIN}px; }}
  100% {{ opacity:0; margin-left:-20px; }}
}}

/* ── Card ── */
.card {{
  background: {N0};
  border-radius: 14px;
  border: 1px solid {N2};
  box-shadow: 0 12px 40px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.3);
  animation: slide-in {ANIM_IN}ms cubic-bezier(0.22,1,0.36,1) both;
}}
.card.closing {{
  animation: slide-out {ANIM_OUT}ms cubic-bezier(0.4,0,1,1) both;
}}

/* ── Sidebar ── */
.sidebar {{
  background: {N1};
  border-right: 1px solid {N2};
  border-radius: 14px 0 0 0;
  padding: 10px 4px 6px;
}}

/* Search */
.search-box {{
  background: {N0};
  border: 1px solid {N2};
  border-radius: 8px;
  margin: 0 6px 8px 6px;
  padding: 1px 8px;
  transition: border-color 150ms;
}}
.search-box:focus-within {{
  border-color: {CYAN};
  box-shadow: 0 0 0 2px rgba(136,192,208,0.12);
}}
.s-icon {{ color:{DIM}; font-size:12px; margin-right:5px; }}
.s-entry {{
  background: transparent; border: none; outline: none;
  color: {N6}; font-size: 12.5px;
  padding: 6px 0; caret-color: {CYAN};
  min-width:0;
}}
.s-entry:focus {{ outline:none; box-shadow:none; }}

/* Category rows */
.sec-lbl {{
  color: {DIM}; font-size:9px; font-weight:800;
  letter-spacing:1.3px; padding: 4px 10px 2px;
}}
.cats {{ background:transparent; padding:0 3px; }}
.cats row {{
  background:transparent; border-radius:7px;
  margin:1px 0; border:none; outline:none;
  min-height:0;
}}
.cats row:hover          {{ background:{N2}; }}
.cats row:selected       {{ background:{N2}; }}
.cats row:selected:focus {{ background:{N2}; outline:none; box-shadow:none; }}

/* Active panel = cyan left border on selected cat */
.cats.focused row:selected {{
  background: linear-gradient(90deg,{CYAN}28 0%,{N2} 80%);
  border-left: 2px solid {CYAN};
}}

.c-icon {{ color:{DIM}; font-size:13px; min-width:18px; }}
.c-name {{ color:{N4}; font-size:12px; font-weight:500; padding:5px 5px; }}
.cats row:selected .c-icon,
.cats.focused row:selected .c-icon {{ color:{CYAN}; }}
.cats row:selected .c-name,
.cats.focused row:selected .c-name  {{ color:{N6}; font-weight:600; }}

/* ── App panel ── */
.apanel {{ background:{N0}; border-radius:0 14px 0 0; }}

.alist-hdr {{
  padding:10px 12px 6px 12px;
  border-bottom:1px solid {N1};
}}
.alist-title {{ color:{DIM}; font-size:9px; font-weight:800; letter-spacing:1.3px; }}
.alist-count {{ color:{N3}; font-size:9px; }}

list {{ background:transparent; }}
row {{
  background:transparent; border-radius:7px;
  margin:1px 5px; border:none;
}}
row:hover          {{ background:{N1}; }}
row:selected       {{ background:{N2}; outline:none; }}
row:selected:focus {{ background:{N2}; outline:none; box-shadow:none; }}

/* Active panel = cyan border on selected app */
.alist.focused row:selected {{
  background: linear-gradient(90deg,{CYAN}18 0%,{N2} 70%);
  border-left: 2px solid {CYAN};
}}

.a-name {{ color:{N6}; font-size:13px; font-weight:500; }}
.a-desc {{ color:{DIM}; font-size:11px; }}
.a-badge {{
  color:{N3}; font-size:9px; font-weight:700; letter-spacing:0.4px;
  background:{N1}; border-radius:4px; padding:1px 5px;
}}

/* ── Bottom bar ── */
.btm {{
  background:{N1}; border-top:1px solid {N2};
  border-radius:0 0 14px 14px; padding:7px 12px;
}}
.u-name {{ color:{N6}; font-size:12.5px; font-weight:700; }}
.u-host {{ color:{DIM}; font-size:10.5px; }}
.hint   {{ color:{N3}; font-size:9px; font-family:monospace; }}
.hint-k {{ color:{CYAN}; font-size:9px; font-weight:700; font-family:monospace; }}

.pw-btn {{
  background:transparent; border:1px solid {N2};
  border-radius:7px; padding:5px 9px;
  color:{DIM}; font-size:14px; min-width:0; min-height:0;
  transition: all 120ms;
}}
.pw-btn:hover {{ background:{N2}; border-color:{RED}44; color:{RED}; }}

/* ── Power overlay ── */
.pow-view {{
  background:{N0}; border-radius:0 14px 0 0;
}}
.pow-card {{
  background:{N1}; border-radius:10px;
  border:1px solid {N2};
  padding:18px 14px 14px;
  margin:4px;
  transition: all 130ms;
  min-width:120px;
}}
.pow-card:hover {{
  background:{N2}; border-color:{N3};
}}
.pow-card.selected {{
  background:{N2}; border-color:{CYAN};
  box-shadow: 0 0 0 1px {CYAN}44;
}}
.pow-card-icon {{ color:{N4}; font-size:26px; margin-bottom:4px; }}
.pow-card-name {{ color:{N5}; font-size:12px; font-weight:600; }}
.pow-card-desc {{ color:{DIM}; font-size:10px; margin-top:2px; }}

.pow-card.shutdown .pow-card-icon {{ color:{RED}; }}
.pow-card.reboot   .pow-card-icon {{ color:{YEL}; }}
.pow-card.logout   .pow-card-icon {{ color:{ORG}; }}
.pow-card.lock     .pow-card-icon {{ color:{BLUE}; }}
.pow-card.suspend  .pow-card-icon {{ color:{PUR}; }}

.pow-hint {{ color:{N3}; font-size:10px; font-family:monospace; margin-top:8px; }}

/* ── Confirm dialog ── */
.dlg-card {{
  background:{N1}; border-radius:12px;
  border:1px solid {N3};
  box-shadow: 0 20px 60px rgba(0,0,0,0.7);
}}
.dlg-icon  {{ color:{RED}; font-size:28px; padding:20px 22px 2px; }}
.dlg-title {{ color:{N6}; font-size:15px; font-weight:700; padding:0 22px 3px; }}
.dlg-sub   {{ color:{DIM}; font-size:11.5px; padding:0 22px 16px; }}
.dlg-sep   {{ background:{N2}; min-height:1px; }}
.dlg-yes {{
  background:{RED}; color:{N6}; border:none;
  border-radius:0 0 0 11px;
  padding:12px 0; font-size:12.5px; font-weight:600; min-height:0;
}}
.dlg-yes:hover {{ background:#C85060; }}
.dlg-yes.sel {{ box-shadow:inset 0 -2px 0 rgba(255,255,255,0.15); }}
.dlg-no {{
  background:{N2}; color:{N4}; border:none;
  border-left:1px solid {N3};
  border-radius:0 0 11px 0;
  padding:12px 0; font-size:12.5px; min-height:0;
}}
.dlg-no:hover {{ background:{N3}; color:{N6}; }}
.dlg-no.sel   {{ background:{N3}; color:{N6}; }}

scrollbar {{ background:transparent; min-width:4px; }}
scrollbar slider {{
  background:{N2}; border-radius:4px;
  min-width:4px; min-height:20px; margin:2px;
}}
scrollbar slider:hover {{ background:{CYAN}; }}
"""

# ── Categories ────────────────────────────────────────────────────────────────
CATEGORIES = [
    ("All",        "󰣆", None),
    ("Internet",   "󰖟", ["Network","WebBrowser","Email","InstantMessaging","Chat"]),
    ("Multimedia", "󰝚", ["AudioVideo","Audio","Video","Music","Player","Recorder"]),
    ("Dev",        "󰘦", ["Development","IDE","Debugger","WebDevelopment"]),
    ("Graphics",   "󰏘", ["Graphics","Photography","2DGraphics","3DGraphics"]),
    ("Office",     "󱉟", ["Office","WordProcessor","Spreadsheet","Presentation"]),
    ("Games",      "󰊗", ["Game","ActionGame","AdventureGame","Emulator"]),
    ("System",     "󱁿", ["System","Monitor","TerminalEmulator","FileManager"]),
    ("Settings",   "󰒓", ["Settings","HardwareSettings","PackageManager"]),
    ("Other",      "󰏗", []),
]
POWER_ITEMS = [
    ("󰌾", "Lock",     "lock",    "Lock screen",    "loginctl lock-session",       False),
    ("󰍃", "Log Out",  "logout",  "End session",    "hyprctl dispatch exit",       False),
    ("󰒲", "Suspend",  "suspend", "Sleep",          "systemctl suspend",           False),
    ("󰜉", "Reboot",   "reboot",  "Restart system", "systemctl reboot --no-wall",  True),
    ("󰐥", "Shutdown", "shutdown","Power off",      "systemctl poweroff --no-wall",True),
]

def get_category(cats):
    for name, _, keys in CATEGORIES:
        if keys and cats.intersection(keys): return name
    return "Other"

def parse_apps():
    dirs = ["/usr/share/applications","/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications"),
            "/var/lib/flatpak/exports/share/applications",
            os.path.expanduser("~/.local/share/flatpak/exports/share/applications")]
    apps, seen = [], set()
    for d in dirs:
        for p in glob.glob(f"{d}/*.desktop"):
            try:
                cfg = configparser.ConfigParser(interpolation=None, strict=False)
                cfg.read(p, encoding="utf-8")
                if "Desktop Entry" not in cfg: continue
                e = cfg["Desktop Entry"]
                if e.get("Type","") != "Application": continue
                if e.get("NoDisplay","false").lower() == "true": continue
                if e.get("Hidden","false").lower() == "true": continue
                name = e.get("Name","").strip()
                if not name or name in seen: continue
                seen.add(name)
                cats = {c.strip() for c in e.get("Categories","").split(";") if c.strip()}
                apps.append({"name":name,"comment":e.get("Comment","").strip(),
                             "exec":e.get("Exec","").strip(),"icon":e.get("Icon","").strip(),
                             "category":get_category(cats)})
            except Exception: continue
    return sorted(apps, key=lambda x: x["name"].lower())

def launch(s):
    subprocess.Popen(s.split("%")[0].strip(), shell=True, start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ── Window ────────────────────────────────────────────────────────────────────
class StartMenu(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Start Menu")
        self.set_decorated(False); self.set_resizable(False)
        self._apps    = parse_apps()
        self._cur_cat = "All"
        self._query   = ""
        self._area    = "apps"   # "cats" | "apps"
        self._power   = False    # power view active
        self._pow_idx = 0        # selected power item index
        self._setup_layer_shell()
        self._apply_css()
        self._build_ui()
        self._populate_apps()
        self._setup_keys()
        self._update_focus_style()

    def _setup_layer_shell(self):
        if not HAS_LAYER_SHELL:
            self.set_default_size(WIN_W, WIN_H); return
        LayerShell.init_for_window(self)
        LayerShell.set_layer(self, LayerShell.Layer.TOP)
        for e in (LayerShell.Edge.LEFT, LayerShell.Edge.TOP,
                  LayerShell.Edge.RIGHT, LayerShell.Edge.BOTTOM):
            LayerShell.set_anchor(self, e, True)
        LayerShell.set_exclusive_zone(self, -1)
        LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.EXCLUSIVE)

    def _apply_css(self):
        p = Gtk.CssProvider()
        p.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # ── Keyboard ──────────────────────────────────────────────────────────────
    def _setup_keys(self):
        kc = Gtk.EventControllerKey()
        kc.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        kc.connect("key-pressed", self._on_key)
        self.add_controller(kc)

    def _on_key(self, ctrl, keyval, keycode, state):
        # ── Always handle these ──
        if keyval == Gdk.KEY_Escape:
            if self._power:
                self._set_power_view(False); return True
            if self._search.get_text():
                self._search.set_text(""); return True
            self._animated_close(); return True

        # Alt_L toggles power menu
        if keyval in (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R):
            self._set_power_view(not self._power); return True

        # ── Power view nav ──
        if self._power:
            n = len(POWER_ITEMS)
            if keyval in (ord('j'), Gdk.KEY_Down, ord('l'), Gdk.KEY_Right):
                self._pow_idx = (self._pow_idx + 1) % n
                self._update_pow_selection(); return True
            if keyval in (ord('k'), Gdk.KEY_Up, ord('h'), Gdk.KEY_Left):
                self._pow_idx = (self._pow_idx - 1) % n
                self._update_pow_selection(); return True
            if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                icon, name, cls, desc, cmd, confirm = POWER_ITEMS[self._pow_idx]
                if confirm:
                    self._confirm_power(name, icon, cmd)
                else:
                    self.close(); launch(cmd)
                return True
            return True  # eat all keys in power view

        # ── Normal view nav ──
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            if self._area == "apps":
                row = self._app_list.get_selected_row()
                if row and hasattr(row, "_app"):
                    launch(row._app["exec"]); self._animated_close()
            elif self._area == "cats":
                self._switch_area("apps")
            return True

        if keyval == Gdk.KEY_Tab:
            self._switch_area("cats" if self._area == "apps" else "apps")
            return True

        # Arrow keys always navigate (captured before search entry)
        if keyval == Gdk.KEY_Down:  self._move(+1); return True
        if keyval == Gdk.KEY_Up:    self._move(-1); return True
        if keyval == Gdk.KEY_Left:  self._switch_area("cats"); return True
        if keyval == Gdk.KEY_Right: self._switch_area("apps"); return True

        # hjkl only when search does NOT have focus
        if not self._search.has_focus():
            if keyval == ord('h'): self._switch_area("cats"); return True
            if keyval == ord('l'): self._switch_area("apps"); return True
            if keyval == ord('j'): self._move(+1); return True
            if keyval == ord('k'): self._move(-1); return True

        return False

    def _switch_area(self, area):
        self._area = area
        self._update_focus_style()
        if area == "cats":
            self._cat_list.grab_focus()
            if not self._cat_list.get_selected_row():
                self._cat_list.select_row(self._cat_list.get_row_at_index(0))
        else:
            self._app_list.grab_focus()
            if not self._app_list.get_selected_row():
                self._app_list.select_row(self._app_list.get_row_at_index(0))

    def _update_focus_style(self):
        if self._area == "cats":
            self._cat_list.add_css_class("focused")
            self._app_list.remove_css_class("focused")
        else:
            self._app_list.add_css_class("focused")
            self._cat_list.remove_css_class("focused")

    def _move(self, d):
        lb = self._cat_list if self._area == "cats" else self._app_list
        sel = lb.get_selected_row()
        idx = max(0, (sel.get_index() if sel else -1) + d)
        row = lb.get_row_at_index(idx)
        if row:
            lb.select_row(row); row.grab_focus()

    # ── Power view ────────────────────────────────────────────────────────────
    def _set_power_view(self, active: bool):
        self._power = active
        self._content_stack.set_visible_child_name("power" if active else "main")
        if active:
            self._pow_idx = 0
            self._update_pow_selection()
        else:
            self._switch_area(self._area)

    def _update_pow_selection(self):
        for i, btn in enumerate(self._pow_btns):
            if i == self._pow_idx:
                btn.add_css_class("selected")
            else:
                btn.remove_css_class("selected")

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = Gtk.Box()
        root.set_hexpand(True); root.set_vexpand(True)
        self.set_child(root)

        self._card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._card.add_css_class("card")
        self._card.set_size_request(WIN_W, WIN_H)
        self._card.set_halign(Gtk.Align.START)
        self._card.set_valign(Gtk.Align.START)
        self._card.set_margin_start(MARGIN)
        self._card.set_margin_top(WAYBAR_H + MARGIN + MARGIN_TOP_EXTRA)
        root.append(self._card)

        # Main row (sidebar + stack)
        main_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_row.set_vexpand(True)
        self._card.append(main_row)

        self._build_sidebar(main_row)

        # Stack: main view vs power view
        self._content_stack = Gtk.Stack()
        self._content_stack.set_hexpand(True)
        self._content_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self._content_stack.set_transition_duration(120)
        main_row.append(self._content_stack)

        self._build_app_panel()
        self._build_power_panel()
        self._build_bottom()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        sb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sb.add_css_class("sidebar")
        sb.set_size_request(SIDEBAR_W, -1)
        parent.append(sb)

        # Search
        swrap = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        swrap.add_css_class("search-box")
        ic = Gtk.Label(label=""); ic.add_css_class("s-icon")
        self._search = Gtk.Entry()
        self._search.add_css_class("s-entry")
        self._search.set_placeholder_text("Search…")
        self._search.set_hexpand(True)
        self._search.connect("changed", lambda e: (
            setattr(self, '_query', e.get_text().strip()),
            self._populate_apps()))
        self._search.connect("activate", lambda _: self._switch_area("apps"))
        swrap.append(ic); swrap.append(self._search)
        sb.append(swrap)

        lbl = Gtk.Label(label="APPS"); lbl.add_css_class("sec-lbl"); lbl.set_xalign(0)
        sb.append(lbl)

        self._cat_list = Gtk.ListBox()
        self._cat_list.add_css_class("cats")
        self._cat_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._cat_list.set_activate_on_single_click(True)
        sb.append(self._cat_list)

        for name, icon, _ in CATEGORIES:
            row = Gtk.ListBoxRow(); row._cat = name
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=7)
            box.set_margin_top(1); box.set_margin_bottom(1)
            box.set_margin_start(7); box.set_margin_end(5)
            ic2 = Gtk.Label(label=icon); ic2.add_css_class("c-icon"); ic2.set_valign(Gtk.Align.CENTER)
            nm  = Gtk.Label(label=name); nm.add_css_class("c-name"); nm.set_xalign(0); nm.set_hexpand(True)
            box.append(ic2); box.append(nm)
            row.set_child(box); self._cat_list.append(row)

        self._cat_list.select_row(self._cat_list.get_row_at_index(0))
        self._cat_list.connect("row-selected", self._on_cat_selected)

        # Alt hint at bottom of sidebar
        spacer = Gtk.Box(); spacer.set_vexpand(True)
        sb.append(spacer)
        alt_lbl = Gtk.Label(label="󰐥  Alt  power")
        alt_lbl.add_css_class("sec-lbl")
        alt_lbl.set_xalign(0); alt_lbl.set_margin_bottom(4)
        sb.append(alt_lbl)

    # ── App panel ─────────────────────────────────────────────────────────────
    def _build_app_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel.add_css_class("apanel")
        self._content_stack.add_named(panel, "main")

        hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hdr.add_css_class("alist-hdr")
        self._title_lbl = Gtk.Label(label="ALL"); self._title_lbl.add_css_class("alist-title")
        self._title_lbl.set_xalign(0); self._title_lbl.set_hexpand(True)
        self._count_lbl = Gtk.Label(label=""); self._count_lbl.add_css_class("alist-count")
        hdr.append(self._title_lbl); hdr.append(self._count_lbl)
        panel.append(hdr)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        panel.append(scroll)

        self._app_list = Gtk.ListBox()
        self._app_list.add_css_class("alist")
        self._app_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._app_list.set_margin_bottom(4)
        self._app_list.connect("row-activated", self._on_app_activated)
        scroll.set_child(self._app_list)

    # ── Power panel ───────────────────────────────────────────────────────────
    def _build_power_panel(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel.add_css_class("pow-view")
        self._content_stack.add_named(panel, "power")

        center = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        center.set_vexpand(True); center.set_valign(Gtk.Align.CENTER)
        center.set_halign(Gtk.Align.CENTER); center.set_spacing(4)
        panel.append(center)

        # Row 1: Lock  Logout  Suspend
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row1.set_halign(Gtk.Align.CENTER)
        # Row 2: Reboot  Shutdown
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        row2.set_halign(Gtk.Align.CENTER)

        self._pow_btns = []
        for i, (icon, name, cls, desc, cmd, confirm) in enumerate(POWER_ITEMS):
            btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            btn_box.add_css_class("pow-card")
            btn_box.add_css_class(cls)
            btn_box.set_halign(Gtk.Align.CENTER)

            ic_lbl = Gtk.Label(label=icon); ic_lbl.add_css_class("pow-card-icon")
            nm_lbl = Gtk.Label(label=name); nm_lbl.add_css_class("pow-card-name")
            ds_lbl = Gtk.Label(label=desc); ds_lbl.add_css_class("pow-card-desc")

            btn_box.append(ic_lbl); btn_box.append(nm_lbl); btn_box.append(ds_lbl)

            gc = Gtk.GestureClick()
            final_i = i
            def on_click(g, n, x, y, idx=final_i):
                _icon, _name, _cls, _desc, _cmd, _confirm = POWER_ITEMS[idx]
                self._pow_idx = idx
                self._update_pow_selection()
                if _confirm:
                    self._confirm_power(_name, _icon, _cmd)
                else:
                    self.close(); launch(_cmd)
            gc.connect("pressed", on_click)
            btn_box.add_controller(gc)

            self._pow_btns.append(btn_box)
            if i < 3: row1.append(btn_box)
            else:      row2.append(btn_box)

        center.append(row1); center.append(row2)

        hint = Gtk.Label(label="j/k ←/→ navigate   Enter select   Alt / Esc back")
        hint.add_css_class("pow-hint"); hint.set_margin_top(6)
        center.append(hint)

    # ── Bottom bar ────────────────────────────────────────────────────────────
    def _build_bottom(self):
        btm = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        btm.add_css_class("btm"); self._card.append(btm)

        try:
            pw = pwd.getpwuid(os.getuid())
            fullname = pw.pw_gecos.split(",")[0].strip() or pw.pw_name
            hostname = os.uname().nodename
        except Exception:
            fullname, hostname = "user", "localhost"

        ubox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        u = Gtk.Label(label=fullname); u.add_css_class("u-name"); u.set_xalign(0)
        h = Gtk.Label(label=f"@{hostname}"); h.add_css_class("u-host"); h.set_xalign(0)
        ubox.append(u); ubox.append(h)
        btm.append(ubox)

        # Keyboard hints centered
        hints_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        hints_box.set_hexpand(True); hints_box.set_halign(Gtk.Align.CENTER)
        hints_box.set_valign(Gtk.Align.CENTER)
        for i, (k, v) in enumerate([("↑↓","move"),("h/l","panel"),("Tab","switch"),("Enter","open"),("Alt","power"),("Esc","close")]):
            if i: sep = Gtk.Label(label=" · "); sep.add_css_class("hint"); hints_box.append(sep)
            kl = Gtk.Label(label=k); kl.add_css_class("hint-k"); hints_box.append(kl)
            vl = Gtk.Label(label=f" {v}"); vl.add_css_class("hint"); hints_box.append(vl)
        btm.append(hints_box)

        # Power buttons (right side, small)
        pbx = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        pbx.set_valign(Gtk.Align.CENTER)
        for icon, tip, cls, desc, cmd, confirm in POWER_ITEMS:
            if cls in ("lock","logout","suspend"): continue  # only reboot/shutdown
            btn = Gtk.Button(label=icon); btn.add_css_class("pw-btn"); btn.set_tooltip_text(tip)
            if confirm:
                btn.connect("clicked", lambda _, t=tip, i=icon, c=cmd: self._confirm_power(t, i, c))
            else:
                btn.connect("clicked", lambda _, c=cmd: (self.close(), launch(c)))
            pbx.append(btn)
        btm.append(pbx)

    # ── Populate ──────────────────────────────────────────────────────────────
    def _populate_apps(self):
        child = self._app_list.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._app_list.remove(child); child = nxt

        q = self._query.lower()
        if q:
            filtered = [a for a in self._apps if q in a["name"].lower() or q in a["comment"].lower()]
            self._title_lbl.set_label(f'"{self._query}"')
        else:
            filtered = [a for a in self._apps if self._cur_cat == "All" or a["category"] == self._cur_cat]
            self._title_lbl.set_label(self._cur_cat.upper())

        self._count_lbl.set_label(f"{len(filtered)}")
        itheme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())

        for app in filtered:
            row = Gtk.ListBoxRow(); row._app = app
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox.set_margin_top(5); hbox.set_margin_bottom(5)
            hbox.set_margin_start(10); hbox.set_margin_end(10)

            img = Gtk.Image(); img.set_pixel_size(26)
            if app["icon"] and itheme.has_icon(app["icon"]):
                img.set_from_icon_name(app["icon"])
            elif os.path.isabs(app["icon"]) and os.path.exists(app["icon"]):
                img.set_from_file(app["icon"])
            else:
                img.set_from_icon_name("application-x-executable")
            hbox.append(img)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            vbox.set_hexpand(True); vbox.set_valign(Gtk.Align.CENTER)
            n = Gtk.Label(label=app["name"]); n.add_css_class("a-name")
            n.set_xalign(0); n.set_ellipsize(Pango.EllipsizeMode.END)
            vbox.append(n)
            if app["comment"]:
                d = Gtk.Label(label=app["comment"]); d.add_css_class("a-desc")
                d.set_xalign(0); d.set_ellipsize(Pango.EllipsizeMode.END)
                vbox.append(d)
            hbox.append(vbox)

            if q or self._cur_cat == "All":
                badge = Gtk.Label(label=app["category"])
                badge.add_css_class("a-badge"); badge.set_valign(Gtk.Align.CENTER)
                hbox.append(badge)

            row.set_child(hbox); self._app_list.append(row)

        first = self._app_list.get_row_at_index(0)
        if first: self._app_list.select_row(first)

    # ── Confirm dialog ────────────────────────────────────────────────────────
    def _confirm_power(self, name, icon, cmd):
        sel = [1]   # 0=yes, 1=no (default No)
        dlg = Gtk.Window(title=""); dlg.set_decorated(False)
        dlg.set_resizable(False); dlg.set_transient_for(self)
        dlg.set_modal(True); dlg.set_default_size(270, -1)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        card.add_css_class("dlg-card"); dlg.set_child(card)

        ic = Gtk.Label(label=icon); ic.add_css_class("dlg-icon"); ic.set_xalign(0); card.append(ic)
        tl = Gtk.Label(label=name); tl.add_css_class("dlg-title"); tl.set_xalign(0); card.append(tl)
        sl = Gtk.Label(label=f"Are you sure you want to {name.lower()}?")
        sl.add_css_class("dlg-sub"); sl.set_xalign(0); sl.set_wrap(True); card.append(sl)

        sep = Gtk.Separator(); sep.add_css_class("dlg-sep"); card.append(sep)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        btn_row.set_homogeneous(True)
        yes_btn = Gtk.Button(label=f"Yes, {name}"); yes_btn.add_css_class("dlg-yes")
        no_btn  = Gtk.Button(label="Cancel");        no_btn.add_css_class("dlg-no")
        yes_btn.connect("clicked", lambda _: (dlg.close(), self.close(), launch(cmd)))
        no_btn.connect("clicked",  lambda _: dlg.close())
        btn_row.append(yes_btn); btn_row.append(no_btn)
        card.append(btn_row)

        def set_sel(s):
            sel[0] = s
            if s == 0: yes_btn.add_css_class("sel"); no_btn.remove_css_class("sel")
            else:       no_btn.add_css_class("sel"); yes_btn.remove_css_class("sel")

        def on_key(ctrl, kv, kc, st):
            if kv == Gdk.KEY_Escape: dlg.close(); return True
            if kv in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                if sel[0] == 0: dlg.close(); self.close(); launch(cmd)
                else: dlg.close()
                return True
            if kv in (ord('h'), Gdk.KEY_Left):  set_sel(0); return True
            if kv in (ord('l'), Gdk.KEY_Right): set_sel(1); return True
            return False

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", on_key)
        dlg.add_controller(kc)
        set_sel(1)
        dlg.present()

    # ── Callbacks ─────────────────────────────────────────────────────────────
    def _on_cat_selected(self, lb, row):
        if not row: return
        self._cur_cat = row._cat; self._query = ""
        self._search.set_text(""); self._populate_apps()

    def _on_app_activated(self, lb, row):
        if hasattr(row, "_app"):
            launch(row._app["exec"]); self._animated_close()

    def _animated_close(self):
        self._card.add_css_class("closing")
        GLib.timeout_add(ANIM_OUT, self.close)

# ── PID ───────────────────────────────────────────────────────────────────────
PIDFILE = "/tmp/start-menu.pid"
def cleanup_pid():
    try: os.unlink(PIDFILE)
    except FileNotFoundError: pass

class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hyprland.startmenu")

    def do_activate(self):
        win = StartMenu(self)
        win.connect("destroy", lambda _: cleanup_pid())
        win.present()
        GLib.timeout_add(80, lambda: (win._search.grab_focus(), False))

if __name__ == "__main__":
    import atexit; atexit.register(cleanup_pid)
    App().run(sys.argv)
