--  ____        _
-- |  _ \ _   _| | ___  ___
-- | |_) | | | | |/ _ \/ __|
-- |  _ <| |_| | |  __/\__ \
-- |_| \_\\__,_|_|\___||___/

-- ── Kitty ────────────────────────────────────────────────────────────────────
hl.window_rule({
	match = { class = "kitty" },
	opacity = "0.88 override 0.80 override",
	no_blur = true,
})

hl.window_rule({
	match = { class = "kitty-autostart" },
	float = true,
	center = true,
	workspace = "3",
})

-- ── Discord ──────────────────────────────────────────────────────────────────
hl.window_rule({
	match = { class = "^(discord)$" },
	workspace = "4 silent",
})

-- ── Spotify ──────────────────────────────────────────────────────────────────
hl.window_rule({
	match = { class = "^(spotify)$" },
	workspace = "5 silent",
})

-- ── Rofi ─────────────────────────────────────────────────────────────────────
hl.window_rule({
	match = { class = "^(rofi)$" },
	float = true,
	opacity = "1.0 override",
})
