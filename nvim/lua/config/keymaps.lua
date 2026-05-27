-- Tambah di keymaps
vim.keymap.set("n", "<leader>lr", function()
  local file = vim.fn.expand("%:p")
  require("toggleterm.terminal").Terminal
    :new({ cmd = "lua " .. file, close_on_exit = false, direction = "horizontal" })
    :toggle()
end, { desc = "Run Lua file" })
