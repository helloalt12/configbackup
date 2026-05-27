return {
  -- LazyGit TUI full-featured git
  {
    "kdheepak/lazygit.nvim",
    cmd = "LazyGit",
    dependencies = { "nvim-lua/plenary.nvim" },
    keys = {
      { "<leader>gg", "<cmd>LazyGit<cr>", desc = "LazyGit" },
    },
  },
  -- Visual diff viewer + file history
  {
    "sindrets/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewFileHistory" },
    keys = {
      { "<leader>gD", "<cmd>DiffviewOpen<cr>", desc = "Diff View" },
      { "<leader>gH", "<cmd>DiffviewFileHistory %<cr>", desc = "File History" },
    },
  },
  -- Git blame virtual text inline
  {
    "f-person/git-blame.nvim",
    event = "BufReadPost",
    opts = { enabled = false }, -- toggle: <leader>gB
    keys = {
      { "<leader>gB", "<cmd>GitBlameToggle<cr>", desc = "Toggle Git Blame" },
    },
  },
}
