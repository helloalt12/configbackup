#!/bin/bash

# aktifkan submap close
hyprctl dispatch submap close

# tunggu 3 detik
sleep 3

# keluar otomatis kalau tidak dipakai
hyprctl dispatch submap reset
