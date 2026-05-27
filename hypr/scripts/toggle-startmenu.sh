#!/usr/bin/env bash
SCRIPT="$HOME/.config/hypr/scripts/start-menu.py"
PIDFILE="/tmp/start-menu.pid"
GUARDFILE="/tmp/startmenu-guard"

# Guard: Super dipakai bareng mouse → skip
if [[ -f "$GUARDFILE" ]]; then
    rm -f "$GUARDFILE"; exit 0
fi

# Kill kalau sudah running
if [[ -f "$PIDFILE" ]]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID"; rm -f "$PIDFILE"; exit 0
    fi
    rm -f "$PIDFILE"
fi

# Launch — cari .so.0 dulu, fallback ke .so
LAYERSHELL=""
for p in /usr/lib64/libgtk4-layer-shell.so.0 \
          /usr/lib64/libgtk4-layer-shell.so \
          /usr/lib/libgtk4-layer-shell.so.0 \
          /usr/lib/libgtk4-layer-shell.so; do
    [[ -f "$p" ]] && { LAYERSHELL="$p"; break; }
done

if [[ -n "$LAYERSHELL" ]]; then
    LD_PRELOAD="$LAYERSHELL" python3 "$SCRIPT" &
else
    python3 "$SCRIPT" &
fi
echo $! > "$PIDFILE"
