return {
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        javascript = { "prettier" },
        typescript = { "prettier" },
        javascriptreact = { "prettier" },
        typescriptreact = { "prettier" },
        css = { "prettier" },
        html = { "prettier" },
        json = { "prettier" },
        python = { "black", "isort" },
        php = { "php_cs_fixer" },
      },
      format_on_save = { timeout_ms = 500 },
    },
  },
}
