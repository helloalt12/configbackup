return {
  {
    "nvim-lualine/lualine.nvim",
    enabled = false,
  },
  {
    "shaunsingh/nord.nvim",
    lazy = false,
    priority = 1000,
    config = function()
      vim.g.nord_contrast = true
      vim.g.nord_borders = true
      vim.g.nord_disable_background = true
      vim.g.nord_italic = true
      vim.g.nord_bold = true

      vim.api.nvim_create_autocmd("ColorScheme", {
        pattern = "*",
        callback = function()
          -- transparent
          local transparent = {
            "Normal",
            "NormalNC",
            "NormalFloat",
            "NeoTreeNormal",
            "NeoTreeNormalNC",
            "NeoTreeEndOfBuffer",
            "SignColumn",
            "EndOfBuffer",
            "FloatBorder",
          }
          for _, group in ipairs(transparent) do
            vim.api.nvim_set_hl(0, group, { bg = "NONE" })
          end

          -- nord HTML treesitter colors
          vim.api.nvim_set_hl(0, "@tag", { fg = "#81a1c1" })
          vim.api.nvim_set_hl(0, "@tag.html", { fg = "#81a1c1" })
          vim.api.nvim_set_hl(0, "@tag.attribute", { fg = "#8fbcbb" })
          vim.api.nvim_set_hl(0, "@tag.delimiter", { fg = "#616e88" })
          vim.api.nvim_set_hl(0, "@string", { fg = "#a3be8c" })
        end,
      })

      vim.cmd.colorscheme("nord")
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "nord",
    },
  },
}
