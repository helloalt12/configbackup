#!/bin/bash
echo "$(date) called with: $1" >> /tmp/waybar-ws.log
hyprctl dispatch "hl.dsp.focus({workspace=$1})"
echo "$(date) exit: $?" >> /tmp/waybar-ws.log
