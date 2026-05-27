#!/bin/bash
killall -9 waybar
wait 0.1
nohup waybar &
