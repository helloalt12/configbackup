-- bootstrap lazy.nvim, LazyVim and your plugins
require("config.lazy")
require("current_theme")

-- ~/.config/nvim/init.lua  (atau di file yang relevan)
require("theme").load()

-- di options.lua / init.lua
vim.opt.swapfile = false -- opsi 1: matiin swap file

-- atau opsi 2: auto handle tanpa prompt
vim.opt.shortmess:append("A") -- skip swap file warning

vim.keymap.set("i", "<CapsLock>", "<Esc>", { noremap = true })
vim.keymap.set("n", "<CapsLock>", "<Esc>", { noremap = true })

vim.opt.mouse = ""
