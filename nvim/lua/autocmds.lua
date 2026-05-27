-- ~/.config/nvim/lua/autocmds.lua (atau langsung di init.lua)
vim.api.nvim_create_autocmd({ "BufRead", "BufNewFile" }, {
  pattern = {
    "*/gtk-3.0/*.css",
    "*/gtk-4.0/*.css",
    "*/.config/gtk*/*.css",
  },
  callback = function()
    vim.bo.filetype = "css" -- ganti ke "scss" kalau mau, atau filetype custom
  end,
})
