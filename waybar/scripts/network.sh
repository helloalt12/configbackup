#!/bin/bash
iface="wlo1"
state=$(cat /sys/class/net/"$iface"/operstate 2>/dev/null)

if [ "$state" != "up" ]; then
  echo '{"text": "offline", "class": "disconnected", "tooltip": "Disconnected"}'
  exit 0
fi

iw_out=$(iw dev "$iface" link 2>/dev/null)
essid=$(echo "$iw_out" | awk '/SSID/{print $2}')
signal=$(echo "$iw_out" | awk '/signal/{print $2}')

if [ -z "$signal" ]; then
  strength=0
else
  strength=$(((signal + 100) * 2))
  [ "$strength" -gt 100 ] && strength=100
  [ "$strength" -lt 0 ] && strength=0
fi

if [ "$strength" -ge 75 ]; then
  class="excellent"
elif [ "$strength" -ge 50 ]; then
  class="good"
elif [ "$strength" -ge 25 ]; then
  class="weak"
else
  class="poor"
fi

echo "{\"text\": \"$essid\", \"class\": \"$class\", \"tooltip\": \"$essid  ${signal} dBm (${strength}%)\"}"
