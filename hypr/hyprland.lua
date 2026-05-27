--  _   _                  _                 _
-- | | | |_   _ _ __  _ __| | __ _ _ __   __| |
-- | |_| | | | | '_ \| '__| |/ _` | '_ \ / _` |
-- |  _  | |_| | |_) | |  | | (_| | | | | (_| |
-- |_| |_|\__, | .__/|_|  |_|\__,_|_| |_|\__,_|
--        |___/|_|
--
-- Hyprland 0.55 — Lua config
-- github.com/rmustard · Nord theme · Fedora + Hyprland
--
-- Split config diload via require().
-- Setiap file ada di ~/.config/hypr/conf/

require("conf.monitors")
require("conf.env")
require("conf.general")
require("conf.decoration")
require("conf.animations")
require("conf.input")
require("conf.layouts")
require("conf.misc")
require("conf.rules")
require("conf.keybindings")
require("conf.autostart")
