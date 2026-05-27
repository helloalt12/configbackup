-- ~/.config/nvim/lua/theme.lua
local M = {}

local state_file = vim.fn.expand("~/.config/theme-state")

function M.load()
  local f = io.open(state_file, "r")
  if not f then
    return
  end
  local state = f:read("*l"):gsub("%s+", "")
  f:close()

  if state == "light" then
    vim.opt.background = "light"
    vim.cmd.colorscheme("catppuccin-latte")
  else
    vim.opt.background = "dark"
    vim.cmd.colorscheme("nord")
  end
end

return M
