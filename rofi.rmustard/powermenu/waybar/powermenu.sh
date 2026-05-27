#!/usr/bin/env bash
#
# powermenu.sh — rmustard
# Grid 2×3 powermenu · Nord theme
#

THEME="$HOME/.config/rofi/powermenu/waybar/powermenu.rasi"

lock="󰌾  Lock"
logout="󰍃  Logout"
shutdown="󰐥  Shutdown"
suspend="󰒲  Suspend"
reboot="󰜉  Reboot"
hibernate="󰤄  Hibernate"

options="$lock\n$logout\n$shutdown\n$suspend\n$reboot\n$hibernate"

chosen=$(echo -e "$options" | rofi \
  -dmenu \
  -i \
  -p "" \
  -theme "$THEME" \
  -u 2,4) # Shutdown (idx 2) & Reboot (idx 4) = urgent merah

case "$chosen" in
"$shutdown") systemctl poweroff ;;
"$reboot") systemctl reboot ;;
"$hibernate") systemctl hibernate ;;
"$suspend")
  hyprlock &
  sleep 0.5
  systemctl suspend
  ;;
"$lock") hyprlock ;;
"$logout") hyprctl dispatch exit ;;
esac
