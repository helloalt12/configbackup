return {
  "akinsho/toggleterm.nvim",
  opts = {
    float_opts = {
      border = "rounded",
      width = function()
        return math.floor(vim.o.columns * 0.85)
      end,
      height = function()
        return math.floor(vim.o.lines * 0.80)
      end,
      winblend = 10,
    },
  },
  keys = {
    {
      "<F5>",
      function()
        local ft = vim.bo.filetype
        local file = vim.fn.expand("%:p")
        local out = "/tmp/" .. vim.fn.expand("%:t:r")

        vim.cmd("silent write")

        local compile_cmd
        if ft == "c" then
          compile_cmd = string.format("gcc -Wall '%s' -o '%s' -lm $(pkg-config --cflags --libs gtk+-3.0)", file, out)
        elseif ft == "cpp" then
          compile_cmd =
            string.format("g++ -std=c++17 -Wall '%s' -o '%s' $(pkg-config --cflags --libs gtkmm-3.0)", file, out)
        else
          vim.notify("Bukan file C/C++", vim.log.levels.WARN)
          return
        end

        local run_cmd = string.format(
          "%s && echo '' && '%s'; echo -e '\\n[exit: '\"$?\"'] — press enter to exit'; read",
          compile_cmd,
          out
        )

        local Terminal = require("toggleterm.terminal").Terminal
        Terminal:new({
          cmd = run_cmd,
          direction = "float",
          close_on_exit = false,
          on_open = function()
            vim.cmd("startinsert!")
          end,
        }):toggle()
      end,
      desc = "Compile & Run C/C++",
    },
  },
}
