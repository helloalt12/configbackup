return {
  -- Treesitter parser
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      vim.list_extend(opts.ensure_installed, { "luau" })
    end,
  },

  -- Install tools via Mason
  {
    "mason-org/mason.nvim",
    opts = function(_, opts)
      vim.list_extend(opts.ensure_installed, {
        "luau-lsp",
        "stylua",
        "selene",
      })
    end,
  },

  -- Disable lspconfig auto-start (kita handle manual lewat autocmd)
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        luau_lsp = { enabled = false },
      },
    },
  },

  -- LSP: manual start via autocmd
  {
    "neovim/nvim-lspconfig",
    init = function()
      vim.api.nvim_create_autocmd("FileType", {
        pattern = "luau",
        callback = function()
          local mason_bin = vim.fn.stdpath("data") .. "/mason/bin/luau-lsp"
          local defs = vim.fn.expand("~/.local/share/luau-lsp/globalTypes.d.luau")
          local docs = vim.fn.expand("~/.local/share/luau-lsp/api-docs.json")
          vim.lsp.start({
            name = "luau_lsp",
            cmd = { mason_bin, "lsp", "--definitions=" .. defs, "--docs=" .. docs },
            root_dir = vim.fs.root(0, { ".git", "*.project.json" }) or vim.fn.getcwd(),
            settings = {
              ["luau-lsp"] = {
                platform = { type = "roblox" },
                completion = { addParentheses = true },
              },
            },
          })
        end,
      })
    end,
  },

  -- Formatter
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        luau = { "stylua" },
      },
    },
  },

  -- Linter
  {
    "mfussenegger/nvim-lint",
    opts = {
      linters_by_ft = {
        luau = {},
      },
    },
  },
}
