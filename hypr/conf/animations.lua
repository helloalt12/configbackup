--    _          _                 _   _
--  / \   _ __ (_)_ __ ___   __ _| |_(_) ___  _ __  ___
-- / _ \ | '_ \| | '_ ` _ \ / _` | __| |/ _ \| '_ \/ __|
--/ ___ \| | | | | | | | | | (_| | |_| | (_) | | | \__ \
--/_/   \_\_| |_|_|_| |_| |_|\__,_|\__|_|\___/|_| |_|___/

hl.config({ animations = { enabled = true } })

-- Bezier curves
hl.curve("smooth", { type = "bezier", points = { { 0.25, 0.1 }, { 0.25, 1 } } })
hl.curve("snappy", { type = "bezier", points = { { 0.2, 0.8 }, { 0.2, 1 } } })
hl.curve("pop", { type = "bezier", points = { { 0.1, 0.9 }, { 0.2, 1.05 } } })

-- Window masuk/keluar — feel "premium pop"
hl.animation({ leaf = "windowsIn", enabled = true, speed = 2, bezier = "smooth", style = "slide" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1, bezier = "smooth", style = "popin 90%" })

-- Movement — "liquid"
hl.animation({ leaf = "windowsMove", enabled = true, speed = 2, bezier = "snappy" })

-- Fade halus
hl.animation({ leaf = "fadeIn", enabled = true, speed = 2, bezier = "smooth" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 2, bezier = "smooth" })

-- Workspace switching — cepat tapi cinematic
hl.animation({ leaf = "workspaces", enabled = true, speed = 3, bezier = "snappy", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3, bezier = "snappy", style = "slide" })
