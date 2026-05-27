#!/bin/bash
SOCK="$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket.sock"
printf 'dispatch "workspace %s"' "$1" | socat - UNIX-CONNECT:$SOCK
