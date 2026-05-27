-- ~/.config/nvim/lua/plugins/treesitter.lua
return {
  {
    "nvim-treesitter/nvim-treesitter",
    tag = "v0.9.3", -- versi terakhir yang support nvim 0.11
    opts = {
      ensure_installed = {
        "html",
        "css",
        "javascript",
        "typescript",
        "tsx",
        "json",
        "lua",
        "python",
        "php",
        "markdown",
        "markdown_inline",
        "bash",
        "regex",
      },
    },
  },
}
