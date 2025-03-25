# Kubernetes MCP Server

An MCP server for debugging and managing Kubernetes config using Natural Language

This MCP Server lets you:
1. Debug a kubernetes config yaml/yml file
2. Debug an entire kubernetes config folder that contains yaml/yml files
3. Connect and manage a Kubernetes cluster **(Coming soon)**


## Quickstart
1. Install Claude Desktop
2. Open the Claude json file

  On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

  On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

3. Install this MCP server

- Using uv: `uv`

Run: `uv pip install git+https://github.com/ehiaig/kubernetes-mcp-server`

Or 

- Clone this repo:
`git clone https://github.com/ehiaig/kubernetes-mcp-server.git`

And then add the following to your MCP servers file:

For Local testing with Claude Desktop
```
{
    "kubernetes-mcp-server": {
    "command": "/path/to/your/.local/bin/uv", // or "uv"
    "args": [
        "--directory",
        "/path/to/this/repo/kubernetes-mcp-server/src/k8s_manager",
        "run",
        "-m",
        "k8s_manager"
    ]
  }
}
```

For Published Servers

```
"mcpServers": {
  "kubernetes-mcp-server": {
    "command": "uvx",
    "args": [
      "k8s_manager"
    ]
  }
}
```

## 🚧 Disclaimers

Sensitive Data

DO NOT CONFIGURE CLUSTERS WITH SENSITIVE DATA. This includes secrets, passwords, etc.

Any sensitive data exchanged with the LLM is inherently compromised, unless the LLM is running 100% on your local machine.

If you are interested in securely passing secrets to CLUSTERS, file an issue on this repository with your use-case.