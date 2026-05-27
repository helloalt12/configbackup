return {
  {
    "nvim-neo-tree/neo-tree.nvim",
    opts = {
      window = { width = 32 },
      filesystem = {
        filtered_items = {
          visible = true, -- tampilkan dotfiles (redup)
          hide_dotfiles = false,
          hide_gitignored = false,
        },
        follow_current_file = {
          enabled = true, -- auto focus file aktif
        },
      },
      default_component_configs = {
        git_status = {
          symbols = {
            added = "+",
            modified = "~",
            deleted = "-",
            renamed = "r",
            untracked = "?",
          },
        },
      },
    },
  },
}
