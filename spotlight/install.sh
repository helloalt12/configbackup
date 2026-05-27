#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════╗
# ║  nord-launch install script                              ║
# ╚══════════════════════════════════════════════════════════╝

set -e
BOLD="\033[1m"; CYAN="\033[36m"; GREEN="\033[32m"; RESET="\033[0m"

echo -e "${BOLD}${CYAN}nord-launch installer${RESET}\n"

# ── 1. Check deps ─────────────────────────────────────────────────────────────
echo -e "${BOLD}[1/4] Checking dependencies...${RESET}"

if ! python3 -c "import gi; gi.require_version('Gtk','4.0'); from gi.repository import Gtk" 2>/dev/null; then
    echo "  → Installing python3-gobject and gtk4..."
    sudo dnf install -y python3-gobject gtk4 2>/dev/null || \
    sudo pacman -S --noconfirm python-gobject gtk4 2>/dev/null || \
    echo "  ⚠ Could not auto-install. Run: sudo dnf install python3-gobject gtk4"
else
    echo "  ✓ GTK4 + PyGObject found"
fi

# ── 2. Copy files ─────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[2/4] Installing files...${RESET}"
DEST="$HOME/.config/nord-launch"
mkdir -p "$DEST"

cp -f launcher.py   "$DEST/launcher.py"
cp -f nord-launch   "$DEST/nord-launch"
chmod +x            "$DEST/nord-launch"

echo "  ✓ Installed to $DEST/"

# ── 3. Hyprland config ────────────────────────────────────────────────────────
echo -e "\n${BOLD}[3/4] Hyprland config...${RESET}"
HYPR_CONF="$HOME/.config/hypr/conf/nord-launch.conf"
cp -f nord-launch.conf "$HYPR_CONF"
echo "  ✓ Wrote $HYPR_CONF"
echo ""
echo "  Add this line to your hyprland.conf or keybinds.conf:"
echo -e "  ${CYAN}source = ~/.config/hypr/conf/nord-launch.conf${RESET}"

# ── 4. Test ───────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}[4/4] Testing launch...${RESET}"
echo "  Running launcher (press Esc to close)"
sleep 1
python3 "$DEST/launcher.py" &

echo -e "\n${GREEN}${BOLD}Done!${RESET}"
echo "  Keybind: SUPER + SPACE"
echo "  Config:  ~/.config/nord-launch/launcher.py"
