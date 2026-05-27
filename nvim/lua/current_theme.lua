vim.schedule(function()
  vim.g.nord_disable_background = true
  vim.cmd.colorscheme("nord")

  vim.api.nvim_set_hl(0, "Normal", { bg = "NONE" })
  vim.api.nvim_set_hl(0, "NormalNC", { bg = "NONE" })
  vim.api.nvim_set_hl(0, "NeoTreeNormal", { bg = "NONE" })
  vim.api.nvim_set_hl(0, "NeoTreeNormalNC", { bg = "NONE" })
  vim.api.nvim_set_hl(0, "NeoTreeEndOfBuffer", { bg = "NONE" })
end)
