-- plugins/python.lua
return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        pyright = {
          handlers = {
            ["$/progress"] = function() end, -- suppress progress notif
          },
        },
      },
    },
  },
}
