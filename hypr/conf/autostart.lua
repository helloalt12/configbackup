-- ____  _             _
--/ ___|| |_ __ _ _ __| |_ _   _ _ __
--\___ \| __/ _` | '__| __| | | | '_ \
-- ___) | || (_| | |  | |_| |_| | |_) |
--|____/ \__\__,_|_|   \__|\\__,_| .__/
--                               |_|

hl.on("hyprland.start", function()
	hl.exec_cmd("waybar")
	hl.exec_cmd("hypridle")
	hl.exec_cmd("swaync")
	hl.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/wallpaper.sh")

	hl.dispatch(hl.dsp.focus({ workspace = 3 }))

	hl.exec_cmd("mpv --no-terminal " .. os.getenv("HOME") .. "/Music/Autostart/hala-madrid.mp3")

	hl.exec_cmd("flatpak run com.discordapp.Discord", { workspace = "4 silent" })
	hl.exec_cmd("flatpak run com.spotify.Client", { workspace = "5 silent" })

	hl.exec_cmd(
		"kitty --class kitty-autostart --config "
			.. os.getenv("HOME")
			.. "/.config/kitty/autostart.conf -e bash -c 'clear; fastfetch; exec tail -f /dev/null'"
	)
	hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP=hyprland")
	hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
end)
