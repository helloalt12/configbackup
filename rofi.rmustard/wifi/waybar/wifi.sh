#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════╗
# ║  wifi.sh — rmustard                                  ║
# ║  Rofi WiFi Manager · Nord · English                  ║
# ╚══════════════════════════════════════════════════════╝

THEME="$HOME/.config/rofi/wifi/waybar/wifi.rasi"

# ─── Rofi helpers ─────────────────────────────────────────────

# No search bar — main menu, confirmations, details
rofi_list() {
  local prompt="$1"
  shift
  rofi -dmenu -p "$prompt" -theme "$THEME" \
    -theme-str 'mainbox { children: [listview]; }' \
    "$@"
}

# With search bar — network list only
rofi_search() {
  local prompt="$1"
  local lines=8
  shift

  if [[ "${1:-}" =~ ^[0-9]+$ ]]; then
    lines="$1"
    shift
  fi

  rofi -dmenu -i -p "$prompt" -theme "$THEME" \
    -theme-str 'mainbox { children: [inputbar, listview]; spacing: 8px; }' \
    -theme-str "listview { lines: $lines; fixed-height: true; dynamic: false; scrollbar: false; spacing: 3px; padding: 0px; }" \
    -theme-str 'inputbar { background-color: #3b4252; border: 1px solid; border-color: #4c566a; border-radius: 8px; padding: 9px 14px; children: [prompt, entry]; spacing: 6px; }' \
    -theme-str 'prompt { background-color: transparent; text-color: #81a1c1; }' \
    -theme-str 'entry { background-color: transparent; text-color: #e5e9f0; placeholder: "search..."; placeholder-color: #4c566a; }' \
    "$@"
}
# No search bar — main menu, confirmations, details

notif() { notify-send -a "WiFi" -i network-wireless -t 3000 "$1" "$2" 2>/dev/null; }
notif_err() { notify-send -a "WiFi" -i network-wireless-offline -t 4000 "$1" "$2" 2>/dev/null; }

sig_icon() {
  local s=${1:-0}
  ((s >= 75)) && echo "󰤨" && return
  ((s >= 50)) && echo "󰤥" && return
  ((s >= 25)) && echo "󰤢" && return
  echo "󰤟"
}

# ─── Status (fast, no rescan) ─────────────────────────────────
get_status() {
  WIFI_ON=false
  CONNECTED=false
  ACTIVE_SSID=""
  ACTIVE_SIG=0

  local state
  state=$(nmcli -t radio wifi 2>/dev/null)
  [ "$state" = "enabled" ] && WIFI_ON=true || return

  local active
  active=$(nmcli -t -f NAME,TYPE connection show --active 2>/dev/null |
    awk -F: '$2=="802-11-wireless" {print $1; exit}')

  [ -z "$active" ] && return

  CONNECTED=true
  ACTIVE_SSID="$active"

  local sig
  sig=$(nmcli -t -f IN-USE,SIGNAL dev wifi list --rescan no 2>/dev/null |
    awk -F: '$1=="*" {print $2; exit}')
  ACTIVE_SIG=${sig:-0}
}

# ─── Scan (real hardware scan) ────────────────────────────────
do_scan() {
  notif "Scanning..." "Looking for networks"
  nmcli dev wifi list --rescan yes &>/dev/null

  local networks
  networks=$(nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list --rescan no 2>/dev/null |
    awk -F: 'NF>=3 && $2!="" && !seen[$2]++ {
          inuse=($1=="*"); sig=$3+0; sec=($4!="--" && $4!="")
          if(sig>=75) ic="󰤨"; else if(sig>=50) ic="󰤥";
          else if(sig>=25) ic="󰤢"; else ic="󰤟"
          printf "%s  %-33s %3d%%%s%s\n",
              ic, $2, sig,
              sec  ? " 󰌾" : "   ",
              inuse? " ✓" : ""
      }' |
    sort -k3 -nr)

  [ -z "$networks" ] && notif_err "Scan" "No networks found" && return

  local count
  count=$(printf '%s\n' "$networks" | sed '/^[[:space:]]*$/d' | wc -l)
  ((count < 1)) && count=1
  ((count > 12)) && count=12

  local chosen
  chosen=$(printf '%s\n' "$networks" | rofi_search "󰤨 Networks" "$count")

  [ -z "$chosen" ] && return

  local ssid
  ssid=$(echo "$chosen" |
    sed 's/^[^ ]*[[:space:]]*//' |
    grep -oP '^.+?(?=\s+\d+%)' |
    sed 's/[[:space:]]*$//')

  [ -n "$ssid" ] && do_connect "$ssid"
}

# ─── Connect ──────────────────────────────────────────────────
do_connect() {
  local ssid="$1"

  if nmcli -t -f NAME connection show 2>/dev/null | grep -qxF "$ssid"; then
    notif "Connecting..." "$ssid"
    nmcli connection up "$ssid" &>/dev/null &&
      notif "Connected ✓" "$ssid" ||
      notif_err "Failed to connect" "$ssid"
    return
  fi

  local sec
  sec=$(nmcli -t -f SSID,SECURITY dev wifi list --rescan no 2>/dev/null |
    grep -m1 "^${ssid}:" | cut -d: -f2)

  if [ -z "$sec" ] || [ "$sec" = "--" ]; then
    notif "Connecting..." "$ssid"
    nmcli dev wifi connect "$ssid" &>/dev/null &&
      notif "Connected ✓" "$ssid" ||
      notif_err "Failed to connect" "$ssid"
  else
    local pass
    pass=$(rofi_list "󰌾 Password" -password \
      -theme-str "window { width: 360px; }" \
      -theme-str "mainbox { children: [inputbar]; }" \
      -theme-str 'inputbar { background-color: #3b4252; border: 1px solid; border-color: #4c566a; border-radius: 8px; padding: 10px 14px; children: [prompt, entry]; spacing: 8px; }' \
      -theme-str 'prompt { background-color: transparent; text-color: #81a1c1; }' \
      -theme-str 'entry { background-color: transparent; text-color: #e5e9f0; placeholder: "password..."; placeholder-color: #4c566a; }')
    [ -z "$pass" ] && return
    notif "Connecting..." "$ssid"
    nmcli dev wifi connect "$ssid" password "$pass" &>/dev/null &&
      notif "Connected ✓" "$ssid" ||
      notif_err "Wrong password or weak signal" "$ssid"
  fi
}

# ─── Disconnect ───────────────────────────────────────────────
do_disconnect() {
  local dev
  dev=$(nmcli -t -f DEVICE,TYPE dev 2>/dev/null |
    grep ":wifi" | head -1 | cut -d: -f1)
  nmcli dev disconnect "$dev" &>/dev/null &&
    notif "Disconnected" "$ACTIVE_SSID" ||
    notif_err "Failed to disconnect" ""
}

# ─── Details ──────────────────────────────────────────────────
show_details() {
  local dev
  dev=$(nmcli -t -f DEVICE,TYPE dev 2>/dev/null |
    grep ":wifi" | head -1 | cut -d: -f1)

  local raw
  raw=$(nmcli -t -f \
    IP4.ADDRESS,IP4.GATEWAY,IP4.DNS,GENERAL.HWADDR \
    dev show "$dev" 2>/dev/null)

  local ip gw dns mac
  ip=$(echo "$raw" | grep 'IP4.ADDRESS' | head -1 | cut -d: -f2-)
  gw=$(echo "$raw" | grep 'IP4.GATEWAY' | head -1 | cut -d: -f2-)
  dns=$(echo "$raw" | grep 'IP4.DNS' | head -1 | cut -d: -f2-)
  mac=$(echo "$raw" | grep 'HWADDR' | head -1 | cut -d: -f2-)

  printf \
    "$(sig_icon $ACTIVE_SIG)  SSID       %s
   IP         %s
󰛳  Gateway    %s
󰀝  DNS        %s
   MAC        %s
   Signal     %s%%" \
    "$ACTIVE_SSID" "${ip:-N/A}" "${gw:-N/A}" \
    "${dns:-N/A}" "${mac:-N/A}" "$ACTIVE_SIG" |
    rofi_list "󰋼 Details" -no-custom
}

# ─── Forget ───────────────────────────────────────────────────
do_forget() {
  local saved
  saved=$(nmcli -t -f NAME,TYPE connection show 2>/dev/null |
    grep ":wifi" | cut -d: -f1 | sort)
  [ -z "$saved" ] && notif "Forget" "No saved networks" && return

  local chosen
  chosen=$(echo "$saved" | rofi_search "󰆴 Forget")
  [ -z "$chosen" ] && return

  local confirm
  confirm=$(printf "Delete\nCancel" | rofi_list "Delete «$chosen»?")
  [ "$confirm" = "Delete" ] || return

  nmcli connection delete "$chosen" &>/dev/null &&
    notif "Deleted" "$chosen" ||
    notif_err "Failed to delete" "$chosen"
}

# ─── Main ─────────────────────────────────────────────────────
main() {
  get_status

  local prompt
  if $CONNECTED; then
    prompt="$(sig_icon $ACTIVE_SIG) $ACTIVE_SSID"
  elif $WIFI_ON; then
    prompt="󰖩 WiFi"
  else
    prompt="󰖪 WiFi Off"
  fi

  local opts=()

  if $WIFI_ON; then
    opts+=("󰤨  Scan network")
    if $CONNECTED; then
      opts+=("󰖪  Disconnect network")
    fi
  else
    opts+=("󰖩  Turn On WiFi")
  fi

  local chosen
  chosen=$(printf "%s\n" "${opts[@]}" | rofi_list "$prompt")

  case "$chosen" in
  *"Scan network"*) do_scan ;;
  *"Disconnect network"*) do_disconnect ;;
  *"Turn On WiFi"*) nmcli radio wifi on && notif "WiFi" "Turned on" && sleep 1 && main ;;
  esac
}

main
