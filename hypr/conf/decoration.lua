-- ____                           _   _
--|  _ \  ___  ___ ___  _ __ __ _| |_(_) ___  _ __
--| | | |/ _ \/ __/ _ \| '__/ _` | __| |/ _ \| '_ \
--| |_| |  __/ (_| (_) | | | (_| | |_| | (_) | | | |
--|____/ \___|\___\___/|_|  \__,_|\__|_|\___/|_| |_|

hl.config({
	decoration = {
		rounding = 10,
		active_opacity = 1.0,
		inactive_opacity = 1.0,

		shadow = {
			enabled = true,
			range = 20,
			color = "rgba(0b131a33)",
			offset = { 0, 4 },
		},

		blur = {
			enabled = true,
			size = 8,
			passes = 3,
			noise = 0.03,
			contrast = 0.95,
			brightness = 0.85,
			vibrancy = 0.10,
			new_optimizations = true,
		},
	},
})
