-- _  __          _     _           _ _
--| |/ /___ _   _| |__ (_)_ __   __| (_)_ __   __ _ ___
--| ' // _ \ | | | '_ \| | '_ \ / _` | | '_ \ / _` / __|
--| . \  __/ |_| | |_) | | | | | (_| | | | | | (_| \__ \
--|_|\_\___|\__, |_.__/|_|_| |_|\__,_|_|_| |_|\__, |___/
--          |___/                              |___/

local mainMod = "SUPER"
local terminal = "kitty"
local fileManager = "kitty -e yazi"
local browser = "firefox"

-- ── Apps ─────────────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + RETURN", hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + SHIFT + W", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/wallpaper.sh"))

-- ── Window Management ────────────────────────────────────────────────────────
hl.bind(mainMod .. " + Q", hl.dsp.window.kill())
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ type = 0 }))
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + SHIFT + ALT + J", hl.dsp.layout("togglesplit"))
hl.bind(mainMod .. " + SHIFT + ALT + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/hypr/scripts/reload_waybar.sh"))
hl.bind(
	mainMod .. " + Z",
	hl.dsp.exec_cmd("grim -g \"$(slurp)\" ~/Pictures/Screenshots/$(date +'%Y-%m-%d_%H-%M-%S').png")
)

-- Guard untuk Super+mouse (supaya startmenu tidak terbuka saat drag)
hl.bind(mainMod .. " + mouse:272", hl.dsp.exec_cmd("touch /tmp/startmenu-guard"))
hl.bind(mainMod .. " + mouse:273", hl.dsp.exec_cmd("touch /tmp/startmenu-guard"))

-- ── Nord-launch / Launcher ───────────────────────────────────────────────────
hl.bind(mainMod .. " + SPACE", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/nord-launch/nord-launch"))

-- ── Rofi ─────────────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/rofi/powermenu/powermenu.sh"))
hl.bind(mainMod .. " + N", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/rofi/wifi/wifi.sh"))
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.config/rofi/power-profile/profile.sh"))

-- ── Resize ───────────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + SHIFT + l", function()
	hl.dispatch(hl.dsp.window.resize({ x = 20, y = 0, relative = true }))
end, { repeating = true })

hl.bind(mainMod .. " + SHIFT + h", function()
	hl.dispatch(hl.dsp.window.resize({ x = -20, y = 0, relative = true }))
end, { repeating = true })

hl.bind(mainMod .. " + SHIFT + k", function()
	hl.dispatch(hl.dsp.window.resize({ x = 0, y = -20, relative = true }))
end, { repeating = true })

hl.bind(mainMod .. " + SHIFT + j", function()
	hl.dispatch(hl.dsp.window.resize({ x = 0, y = 20, relative = true }))
end, { repeating = true })

-- ── Swap Window ──────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + CTRL + l", hl.dsp.window.swap({ direction = "r" }))
hl.bind(mainMod .. " + CTRL + h", hl.dsp.window.swap({ direction = "l" }))
hl.bind(mainMod .. " + CTRL + k", hl.dsp.window.swap({ direction = "u" }))
hl.bind(mainMod .. " + CTRL + j", hl.dsp.window.swap({ direction = "d" }))

-- ── Focus ────────────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + h", hl.dsp.focus({ direction = "l" }))
hl.bind(mainMod .. " + l", hl.dsp.focus({ direction = "r" }))
hl.bind(mainMod .. " + k", hl.dsp.focus({ direction = "u" }))
hl.bind(mainMod .. " + j", hl.dsp.focus({ direction = "d" }))

-- ── Workspaces ───────────────────────────────────────────────────────────────
for i = 1, 9 do
	hl.bind(mainMod .. " + " .. i, hl.dsp.focus({ workspace = i }))
	hl.bind(mainMod .. " + SHIFT + " .. i, hl.dsp.window.move({ workspace = i }))
end

hl.bind(mainMod .. " + 0", hl.dsp.focus({ workspace = 10 }))
hl.bind(mainMod .. " + SHIFT + 0", hl.dsp.window.move({ workspace = 10 }))

-- ── Scratchpad ───────────────────────────────────────────────────────────────
hl.bind(mainMod .. " + S", hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- ── Mouse Workspace Scroll ───────────────────────────────────────────────────
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up", hl.dsp.focus({ workspace = "e-1" }))

-- ── Mouse Window Control ─────────────────────────────────────────────────────
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- ── Multimedia ───────────────────────────────────────────────────────────────
hl.bind(
	"XF86AudioRaiseVolume",
	hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 1%+"),
	{ locked = true, repeating = true }
)
hl.bind(
	"XF86AudioLowerVolume",
	hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%-"),
	{ locked = true, repeating = true }
)
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"), { locked = true, repeating = true })

hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true })
