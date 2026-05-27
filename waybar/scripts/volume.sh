#!/bin/bash
get_volume() {
  vol=$(pamixer --get-volume)
  muted=$(pamixer --get-mute)
  if [ "$muted" = "true" ] || [ "$vol" -eq 0 ]; then
    class="muted"
  elif [ "$vol" -le 33 ]; then
    class="low"
  elif [ "$vol" -le 66 ]; then
    class="mid"
  else
    class="high"
  fi
  echo "{\"text\": \"${vol}%\", \"class\": \"$class\", \"tooltip\": \"${vol}%\"}"
}

get_volume

pactl subscribe | grep --line-buffered "sink" | while read -r _; do
  get_volume
done
