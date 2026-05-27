-- ~/.config/nvim/lua/plugins/colorscheme.lua
return {
  {
    "EdenEast/nightfox.nvim",
    lazy = false,
    priority = 1000,
    opts = {
      options = {
        transparent = true, -- kalau pakai transparent terminal
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "nordfox",
    },
  },
}
