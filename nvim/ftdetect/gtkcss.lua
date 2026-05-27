-- ~/.config/nvim/ftdetect/gtkcss.lua
vim.api.nvim_create_autocmd({ "BufRead", "BufNewFile" }, {
  pattern = {
    "*/gtk-3.0/gtk.css",
    "*/gtk-4.0/gtk.css",
    "*/gtk*.css",
  },
  callback = function()
    vim.bo.filetype = "gtkcss"
  end,
})
