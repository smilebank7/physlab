# physlab-mac-mcp

MCP server package for physlab simulation tools.

```bash
npx physlab-mac-mcp --help
npx physlab-mcp-server --help
```

The v0.1 package exposes JSON-RPC MCP tools for `task.list`, `sim.make`,
`sim.reset`, `sim.step`, and `sim.observe`. It expects Python physlab to be
available in the workspace where the server is launched.
