#!/bin/bash

WALLPAPER_DIR="$HOME/Pictures/Wallpapers"
INDEX_FILE="$HOME/.cache/wallpaper_index"

mapfile -t WALLPAPERS < <(
  find "$WALLPAPER_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.webp" \) | sort
)

TOTAL=${#WALLPAPERS[@]}
[ "$TOTAL" -eq 0 ] && exit 1

CURRENT=$(cat "$INDEX_FILE" 2>/dev/null || echo "0")
INDEX=$((CURRENT % TOTAL))

WALLPAPER="${WALLPAPERS[$INDEX]}"
echo $(((INDEX + 1) % TOTAL)) >"$INDEX_FILE"

# pastikan daemon jalan
pgrep -x awww-daemon >/dev/null || awww-daemon >/dev/null 2>&1 &

sleep 0.2

# set wallpaper
awww img "$WALLPAPER" >/dev/null 2>&1 &
