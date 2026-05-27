return {
  "neovim/nvim-lspconfig",
  opts = {
    servers = {
      clangd = {
        cmd = {
          "clangd",
          "--background-index",
          "--clang-tidy",
          "--completion-style=detailed",
          "--header-insertion=iwyu",
          "--fallback-style=llvm",
          "--query-driver=/usr/bin/gcc", -- tambah ini
        },
        filetypes = { "c", "cpp" }, -- eksplisit
      },
    },
  },
}
