return {
  "akinsho/toggleterm.nvim",
  opts = function(_, opts)
    return opts
  end,
  keys = {
    {
      "<leader>r",
      function()
        local file = vim.fn.expand("%:p")
        local ft = vim.bo.filetype
        local cmd = ({
          lua = "lua " .. file,
          python = "python3 -u " .. file,
          sh = "bash " .. file,
          c = "cd " .. vim.fn.expand("%:p:h") .. " && gcc " .. file .. " -o /tmp/out && /tmp/out",
          cpp = "cd " .. vim.fn.expand("%:p:h") .. " && g++ " .. file .. " -o /tmp/out && /tmp/out",
        })[ft]

        if not cmd then
          vim.notify("Filetype '" .. ft .. "' not supported", vim.log.levels.WARN)
          return
        end

        require("toggleterm.terminal").Terminal
          :new({ cmd = cmd, close_on_exit = false, direction = "horizontal" })
          :toggle()
      end,
      desc = "Run Code",
    },
  },
}
