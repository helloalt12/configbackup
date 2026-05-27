#!/bin/bash

capacity=$(cat /sys/class/power_supply/BAT0/capacity)
status=$(cat /sys/class/power_supply/BAT0/status)

if [ "$status" = "Charging" ]; then
  class="charging"
elif [ "$capacity" -le 20 ]; then
  class="bat20"
elif [ "$capacity" -le 30 ]; then
  class="bat30"
elif [ "$capacity" -le 40 ]; then
  class="bat40"
elif [ "$capacity" -le 50 ]; then
  class="bat50"
elif [ "$capacity" -le 60 ]; then
  class="bat60"
elif [ "$capacity" -le 70 ]; then
  class="bat70"
elif [ "$capacity" -le 80 ]; then
  class="bat80"
elif [ "$capacity" -le 90 ]; then
  class="bat90"
else
  class="bat100"
fi

echo "{\"text\": \"${capacity}%\", \"class\": \"$class\", \"tooltip\": \"${status} ${capacity}%\"}"
