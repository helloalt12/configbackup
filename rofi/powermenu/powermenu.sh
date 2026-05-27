#!/usr/bin/env bash
# powermenu.sh — Nord rofi powermenu for Hyprland

THEME="$HOME/.config/rofi/powermenu/powermenu.rasi"

# ── entries: icon (nerd font) + label ──────────────────────────────────────
# row 1
LOCK="󰌾  Lock"
SUSPEND="󰒲  Suspend"
HIBERNATE="󰤄  Hibernate"
# row 2
REBOOT="󰑓  Reboot"
SHUTDOWN="󰐥  Shutdown"
LOGOUT="󰍃  Logout"

# ── show rofi ──────────────────────────────────────────────────────────────
CHOICE=$(printf '%s\n' \
  "$LOCK" \
  "$SUSPEND" \
  "$HIBERNATE" \
  "$REBOOT" \
  "$SHUTDOWN" \
  "$LOGOUT" |
  rofi \
    -dmenu \
    -p "" \
    -theme "$THEME" \
    -selected-row 4 \
    -a "0,1,2" \
    -u "3,4,5" \
    -no-custom)

# ── handle selection ───────────────────────────────────────────────────────
case "$CHOICE" in
"$LOCK")
  # change to your locker: hyprlock / swaylock / etc.
  hyprlock
  ;;
"$SUSPEND")
  systemctl suspend
  ;;
"$HIBERNATE")
  systemctl hibernate
  ;;
"$REBOOT")
  systemctl reboot --no-wall
  ;;
"$SHUTDOWN")
  systemctl poweroff --no-wall
  ;;
"$LOGOUT")
  hyprctl dispatch 'hl.dsp.exit()'
  ;;
esac
