-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

vim.opt.number = true -- nomer baris
vim.opt.relativenumber = false -- relatif dari cursor (opsional, enak buat motion)
vim.opt.laststatus = 0

vim.diagnostic.config({
  virtual_text = false,
  underline = true,
  signs = false,
  update_in_insert = false,
})
