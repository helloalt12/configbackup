return {
  {
    "mfussenegger/nvim-dap",
    dependencies = {
      "rcarriga/nvim-dap-ui",
      "nvim-neotest/nvim-nio",
      "mxsdev/nvim-dap-vscode-js",
      "mfussenegger/nvim-dap-python",
    },
    config = function()
      local dap = require("dap")
      local dapui = require("dapui")

      dapui.setup()

      -- =========================
      -- JS / TS (Node Debugger)
      -- =========================
      require("dap-vscode-js").setup({
        debugger_path = vim.fn.stdpath("data") .. "/mason/packages/js-debug-adapter",
        adapters = { "pwa-node", "pwa-chrome" },
      })

      for _, lang in ipairs({ "javascript", "typescript" }) do
        dap.configurations[lang] = {
          {
            type = "pwa-node",
            request = "launch",
            name = "Launch current file",
            program = "${file}",
            cwd = "${workspaceFolder}",
            sourceMaps = true,
            skipFiles = { "<node_internals>/**" },
          },
        }
      end

      -- =========================
      -- Python Debugger
      -- =========================
      require("dap-python").setup("python3")

      dap.configurations.python = {
        {
          type = "python",
          request = "launch",
          name = "Launch current file",
          program = "${file}",
          pythonPath = function()
            return "python3"
          end,
        },
      }

      -- =========================
      -- Auto UI open/close
      -- =========================
      dap.listeners.after.event_initialized["dapui"] = function()
        dapui.open()
      end

      dap.listeners.before.event_terminated["dapui"] = function()
        dapui.close()
      end

      dap.listeners.before.event_exited["dapui"] = function()
        dapui.close()
      end
    end,

    keys = {
      { "<leader>db", "<cmd>DapToggleBreakpoint<cr>", desc = "Breakpoint" },
      { "<leader>dc", "<cmd>DapContinue<cr>", desc = "Continue" },
      { "<leader>di", "<cmd>DapStepInto<cr>", desc = "Step Into" },
      { "<leader>dn", "<cmd>DapStepOver<cr>", desc = "Step Over" },
      { "<leader>do", "<cmd>DapStepOut<cr>", desc = "Step Out" },

      {
        "<leader>du",
        function()
          require("dapui").toggle()
        end,
        desc = "Toggle DAP UI",
      },
    },
  },
}
