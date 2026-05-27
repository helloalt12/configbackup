return {
  {
    "barrett-ruth/live-server.nvim",
    build = "npm install -g live-server",
    cmd = { "LiveServerStart", "LiveServerStop" },
    config = true,
    keys = {
      { "<leader>lp", "<cmd>LiveServerStart<cr>", desc = "Live Server Start" },
      { "<leader>lP", "<cmd>LiveServerStop<cr>", desc = "Live Server Stop" },
    },
  },
}
