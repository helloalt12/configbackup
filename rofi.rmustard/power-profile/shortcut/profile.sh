#!/usr/bin/env bash

dir="$HOME/.config/rofi/power-profile/shortcut/"

SCRIPT=$(mktemp /tmp/rofi-profile-XXXXXX.sh)
chmod +x "$SCRIPT"

cat >"$SCRIPT" <<'ENDSCRIPT'
#!/usr/bin/env bash

retv="${ROFI_RETV:-0}"
input="$1"

current=$(powerprofilesctl get)

active_tag() {
    [ "$1" = "$current" ] && echo "  ●" || echo ""
}

# ── Handle selection ─────────────────────────────────
if [ "$retv" = "1" ]; then
    case "$input" in
        *"Battery Saver"*)  powerprofilesctl set power-saver ;;
        *"Balanced"*)       powerprofilesctl set balanced ;;
        *"Performance"*)    powerprofilesctl set performance ;;
    esac
    exit
fi

# ── Display ──────────────────────────────────────────
# 󰤄 = daun/eco   ⚖ = timbangan   󱐋 = petir
printf "󰤄  Battery Saver%s\0icon\x1fpower-profile-power-saver\n"   "$(active_tag power-saver)"
printf "⚖  Balanced%s\0icon\x1fpower-profile-balanced\n"            "$(active_tag balanced)"
printf "󱐋  Performance%s\0icon\x1fpower-profile-performance\n"      "$(active_tag performance)"
ENDSCRIPT

rofi \
  -modi "profile:$SCRIPT" \
  -show profile \
  -theme "${dir}/profile.rasi"

rm -f "$SCRIPT"
