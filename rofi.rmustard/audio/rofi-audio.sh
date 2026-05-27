#!/usr/bin/env bash
# ══════════════════════════════════════════════
#  rofi-audio.sh — Audio Control Panel
#  Stays open after each action (Esc to close)
#  Nord · Minimalist · PipeWire/PulseAudio
# ══════════════════════════════════════════════

RASI=/tmp/rofi-audio.rasi
cat >"$RASI" <<'EOF'
* {
    bg:      #1C2130;
    bg-row:  #232A3A;
    sel:     #2C3550;
    border:  #3D5070;
    fg:      #C8D0E0;
    dim:     #4A5470;
    accent:  #7AA2C8;

    background-color: @bg;
    text-color:       @fg;
    font:             "JetBrainsMono Nerd Font 10.5";
    margin:  0;
    padding: 0;
    spacing: 0;
}

window {
    background-color: @bg;
    border:           1px solid;
    border-color:     @border;
    border-radius:    12px;
    width:            420px;
}

mainbox {
    background-color: transparent;
    children:         [ inputbar, listview ];
    spacing:          0;
}

inputbar {
    background-color: @bg;
    border-radius:    12px 12px 0 0;
    padding:          12px 16px 10px;
    spacing:          8px;
    children:         [ prompt, entry ];
    border:           0 0 1px 0;
    border-color:     @border;
}

prompt {
    text-color: @accent;
    font:       "JetBrainsMono Nerd Font 10.5";
}

entry {
    text-color:        @fg;
    placeholder:       "";
    placeholder-color: @dim;
}

listview {
    background-color: transparent;
    padding:          6px 6px 8px;
    spacing:          1px;
    lines:            10;
    scrollbar:        false;
    fixed-height:     false;
    cycle:            true;
}

element {
    background-color: transparent;
    border-radius:    7px;
    padding:          8px 12px;
    children:         [ element-text ];
    cursor:           pointer;
}

element normal.normal    { background-color: transparent; text-color: @fg;  }
element alternate.normal { background-color: transparent; text-color: @fg;  }
element selected.normal  { background-color: @sel;        text-color: @fg;  }

element-text {
    background-color: transparent;
    text-color:       inherit;
    vertical-align:   0.5;
    font:             "JetBrainsMono Nerd Font 10.5";
}
EOF

# ── Helpers ──────────────────────────────────
notify_() {
  command -v notify-send &>/dev/null &&
    notify-send -a "audio" -t 1800 "$1" "$2"
}

get_vol() {
  pactl get-sink-volume @DEFAULT_SINK@ |
    grep -oP '\d+%' | head -1 | tr -d '%'
}

vol_bar() {
  local p="$1" f=$((($1 + 9) / 10))
  [[ $f -gt 10 ]] && f=10
  local e=$((10 - f)) b=""
  for ((i = 0; i < f; i++)); do b+="█"; done
  for ((i = 0; i < e; i++)); do b+="░"; done
  printf "%s %d%%" "$b" "$p"
}

sink_muted() { pactl get-sink-mute @DEFAULT_SINK@ | grep -q yes; }
source_muted() { pactl get-source-mute @DEFAULT_SOURCE@ | grep -q yes; }

col() { printf "%-34s%s" "$1" "$2"; }

desc_of() {
  # $1 = name, $2 = sinks|sources
  pactl list "$2" 2>/dev/null | awk -v t="$1" '
        /^\tName:/        { cur=$2 }
        /^\tDescription:/ && cur==t {
            sub(/^\tDescription: /,""); print; exit
        }' | cut -c1-26
}

# ── Rofi call ────────────────────────────────
rofi_pick() {
  # $1=prompt, rest=entries
  local prompt="$1"
  shift
  printf '%s\n' "$@" |
    rofi -dmenu -i -no-custom \
      -p "$prompt" \
      -theme "$RASI"
}

SEP="" # blank line as visual gap (non-actionable)

# ── Device submenus ──────────────────────────
pick_output() {
  local default_sink
  default_sink=$(pactl get-default-sink)
  local -a names descs
  while IFS=$'\t' read -r n d; do
    names+=("$n")
    descs+=("$d")
  done < <(pactl list sinks | awk '
        /^\tName:/        { name=$2 }
        /^\tDescription:/ { sub(/^\tDescription: /,""); print name"\t"$0 }')

  [[ ${#names[@]} -eq 0 ]] && return

  local -a entries
  for i in "${!descs[@]}"; do
    local dot="  ○ "
    [[ "${names[$i]}" == "$default_sink" ]] && dot="  ● "
    entries+=("${dot}${descs[$i]}")
  done

  local choice
  choice=$(rofi_pick "󰓃  output" "${entries[@]}")
  [[ -z "$choice" ]] && return

  local picked
  picked=$(echo "$choice" | sed 's/^  [●○] //')
  for i in "${!descs[@]}"; do
    if [[ "${descs[$i]}" == "$picked" ]]; then
      pactl set-default-sink "${names[$i]}"
      pactl list short sink-inputs | awk '{print $1}' |
        xargs -I{} pactl move-sink-input {} "${names[$i]}" 2>/dev/null
      notify_ "output" "→ ${descs[$i]}"
      break
    fi
  done
}

pick_input() {
  local default_src
  default_src=$(pactl get-default-source)
  local -a names descs
  while IFS=$'\t' read -r n d; do
    [[ "$n" == *".monitor"* ]] && continue
    names+=("$n")
    descs+=("$d")
  done < <(pactl list sources | awk '
        /^\tName:/        { name=$2 }
        /^\tDescription:/ { sub(/^\tDescription: /,""); print name"\t"$0 }')

  [[ ${#names[@]} -eq 0 ]] && return

  local -a entries
  for i in "${!descs[@]}"; do
    local dot="  ○ "
    [[ "${names[$i]}" == "$default_src" ]] && dot="  ● "
    entries+=("${dot}${descs[$i]}")
  done

  local choice
  choice=$(rofi_pick "󰍬  input" "${entries[@]}")
  [[ -z "$choice" ]] && return

  local picked
  picked=$(echo "$choice" | sed 's/^  [●○] //')
  for i in "${!descs[@]}"; do
    if [[ "${descs[$i]}" == "$picked" ]]; then
      pactl set-default-source "${names[$i]}"
      pactl list short source-outputs | awk '{print $1}' |
        xargs -I{} pactl move-source-output {} "${names[$i]}" 2>/dev/null
      notify_ "input" "→ ${descs[$i]}"
      break
    fi
  done
}

# ── Main loop ────────────────────────────────
while true; do
  vol=$(get_vol)
  bar=$(vol_bar "$vol")

  out=$(desc_of "$(pactl get-default-sink)" sinks)
  inp=$(desc_of "$(pactl get-default-source)" sources)
  [[ -z "$out" ]] && out=$(pactl get-default-sink | sed 's/.*\.//')
  [[ -z "$inp" ]] && inp=$(pactl get-default-source | sed 's/.*\.//')

  # prompt carries live status
  PROMPT=" Audio  ·  ${bar}"

  # Speaker row
  if sink_muted; then
    spk="$(col "  󰝟  speaker" "muted")"
  else
    spk="$(col "  󰕾  speaker" "${vol}%")"
  fi

  # Mic row
  if source_muted; then
    mic="$(col "  󰍭  microphone" "muted")"
  else
    mic="$(col "  󰍬  microphone" "")"
  fi

  out_row="$(col "  󰓃  output" "${out:0:22}  ›")"
  inp_row="$(col "  󰍬  input" "${inp:0:22}  ›")"
  vup="$(col "  ↑  volume up" "+5%")"
  vdn="$(col "  ↓  volume down" "−5%")"

  choice=$(
    rofi_pick "$PROMPT" \
      "$spk" \
      "$mic" \
      "$SEP" \
      "$out_row" \
      "$inp_row" \
      "$SEP" \
      "$vup" \
      "$vdn"
  )

  # Esc / close → exit
  [[ -z "$choice" ]] && break

  case "$choice" in
  *"speaker"*)
    pactl set-sink-mute @DEFAULT_SINK@ toggle
    sink_muted &&
      notify_ "󰝟 speaker" "muted" ||
      notify_ "󰕾 speaker" "unmuted · $(get_vol)%"
    ;;
  *"microphone"*)
    pactl set-source-mute @DEFAULT_SOURCE@ toggle
    source_muted &&
      notify_ "󰍭 mic" "muted" ||
      notify_ "󰍬 mic" "unmuted"
    ;;
  *"output"*)
    pick_output
    ;;
  *"input"*)
    pick_input
    ;;
  *"volume up"*)
    pactl set-sink-volume @DEFAULT_SINK@ +5%
    notify_ "󰕾 volume" "+5%  →  $(get_vol)%"
    ;;
  *"volume down"*)
    pactl set-sink-volume @DEFAULT_SINK@ -5%
    notify_ "󰕾 volume" "−5%  →  $(get_vol)%"
    ;;
  esac
  # loop → menu re-renders with fresh state
done
