return {
  {
    "nvim-tree/nvim-web-devicons",
    opts = {
      override_by_extension = {
        luau = {
          icon = "󰢱",
          color = "#00A2FF",
          name = "Luau",
        },
      },
      override = {
        ["default.project.json"] = {
          icon = "",
          color = "#F1E05A",
          name = "RojoProject",
        },
      },
    },
  },
}
