return {
  -- 1. Mason: installer UI
  {
    "mason-org/mason.nvim",
    build = ":MasonUpdate",
    opts = {},
  },

  -- 2. Bridge: Mason <-> lspconfig
  {
    "mason-org/mason-lspconfig.nvim",
    dependencies = {
      "mason-org/mason.nvim",
      "neovim/nvim-lspconfig",
    },
    config = function()
      require("mason-lspconfig").setup({
        -- Pakai lspconfig server names (bukan Mason package names)
        ensure_installed = {
          "ts_ls", -- typescript-language-server
          "eslint",
          "html",
          "cssls",
          "emmet_ls",
          "tailwindcss",
          "pyright",
          "intelephense",
        },
        automatic_installation = true,
      })
    end,
  },

  -- 3. Install non-LSP tools (formatter, linter)
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = { "mason-org/mason.nvim" },
    opts = {
      ensure_installed = {
        "prettier",
        "black",
        "ruff",
        "php-cs-fixer",
      },
    },
  },

  -- 4. lspconfig: setup server configs
  {
    "neovim/nvim-lspconfig",
    dependencies = { "mason-org/mason-lspconfig.nvim" },
    config = function()
      local lspconfig = require("lspconfig")

      -- Ambil capabilities dari nvim-cmp jika ada
      local capabilities = vim.lsp.protocol.make_client_capabilities()

      local ok, cmp = pcall(require, "cmp_nvim_lsp")
      if ok then
        capabilities = cmp.default_capabilities(capabilities)
      end

      -- FIX PENTING: samakan encoding semua LSP
      capabilities.offsetEncoding = { "utf-8" }

      local on_attach = function(_, bufnr)
        local map = function(keys, func, desc)
          vim.keymap.set("n", keys, func, { buffer = bufnr, desc = desc })
        end
        map("gd", vim.lsp.buf.definition, "Go to Definition")
        map("gr", vim.lsp.buf.references, "References")
        map("<leader>rn", vim.lsp.buf.rename, "Rename")
        map("<leader>ca", vim.lsp.buf.code_action, "Code Action")
        map("<leader>k", vim.lsp.buf.hover, "Hover Docs")
        map("<leader>d", vim.diagnostic.open_float, "Diagnostics")
      end

      -- Default config untuk semua server
      local default = { on_attach = on_attach, capabilities = capabilities }

      -- Server configs
      local servers = {
        ts_ls = {},
        eslint = {},
        html = {},
        cssls = {
          filetypes = { "css", "scss", "less" },
        },
        emmet_ls = {
          filetypes = { "html", "css", "scss", "javascriptreact", "typescriptreact" },
        },
        tailwindcss = {},
        pyright = {
          handlers = {
            ["$/progress"] = function() end, -- suppress notifikasi centang
          },
          settings = {
            python = {
              analysis = { typeCheckingMode = "basic" },
            },
          },
        },
        intelephense = {},
      }

      for server, config in pairs(servers) do
        lspconfig[server].setup(vim.tbl_deep_extend("force", default, config))
      end
    end,
  },
}
