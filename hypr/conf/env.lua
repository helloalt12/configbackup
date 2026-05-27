-- _____            _                                      _
--|  ____|_ ____   _(_)_ __ ___  _ __  _ __ ___   ___ _ __ | |_
--|  _| | '_ \ \ / / | '__/ _ \| '_ \| '_ ` _ \ / _ \ '_ \| __|
--| |___| | | \ V /| | | | (_) | | | | | | | | |  __/ | | | |_
--|_____|_| |_|\_/ |_|_|  \___/|_| |_|_| |_| |_|\___|_| |_|\__|

-- Cursor
hl.env("XCURSOR_THEME", "Future-cyan-cursors")
hl.env("XCURSOR_SIZE", "24")

-- Graphics
hl.env("LIBVA_DRIVER_NAME", "iHD")
hl.env("WLR_RENDERER", "vulkan")
hl.env("ANV_QUEUE_THREAD_DISABLE", "1")

hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- GTK
hl.env("GTK_THEME", "Nordic")
hl.env("GTK_USE_PORTAL", "1")

-- Wayland
hl.env("MOZ_ENABLE_WAYLAND", "1")
