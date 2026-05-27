-- ___                   _
--|_ _|_ __  _ __  _   _| |_
-- | || '_ \| '_ \| | | | __|
-- | || | | | |_) | |_| | |_
--|___|_| |_| .__/ \__,_|\__|
--          |_|
hl.config({
	input = {
		kb_layout = "us",
		kb_variant = "altgr-intl", -- tambah ini
		kb_options = "caps:escape", -- hapus compose:ralt
		follow_mouse = 1,
		sensitivity = 0,
		touchpad = {
			natural_scroll = true,
		},
	},
})
-- 3-finger horizontal swipe → switch workspace
hl.gesture({
	fingers = 3,
	direction = "horizontal",
	action = "workspace",
})
-- Per-device config
hl.device({
	name = "epic-mouse-v1",
	sensitivity = -0.5,
})
