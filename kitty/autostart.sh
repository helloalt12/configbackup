#!/bin/bash
FIFO=$(mktemp -u /tmp/kitty-block-XXXXXX)
mkfifo "$FIFO"
trap "rm -f $FIFO" EXIT

clear
fastfetch
exec cat "$FIFO"
