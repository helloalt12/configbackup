return {
  {
    "akinsho/toggleterm.nvim",
    version = "*",
    opts = {
      size = 15,
      open_mapping = [[<C-\>]],
      direction = "horizontal",
      shade_terminals = false,
      persist_size = true,
    },
    keys = {
      { "<C-\\>", desc = "Toggle Terminal" },
      { "<leader>tf", "<cmd>ToggleTerm direction=float<cr>", desc = "Float Terminal" },
      { "<leader>tv", "<cmd>ToggleTerm direction=vertical size=60<cr>", desc = "Vertical Terminal" },
      {
        "<leader>tg",
        function()
          local Terminal = require("toggleterm.terminal").Terminal
          Terminal:new({ cmd = "lazygit", hidden = true, direction = "float" }):toggle()
        end,
        desc = "LazyGit (term)",
      },
    },
  },
}
