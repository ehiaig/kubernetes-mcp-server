# Kubernetes MCP Server

An MCP server for debugging and managing Kubernetes config using Natural Language

This MCP Server lets you:
1. Debug a kubernetes config yaml/yml file
2. Debug an entire kubernetes config folder that contains yaml/yml files
3. Connect and manage Kubernetes clusters
  
## Features
  - [x] Debug and analyze a kubernetes config yaml/yml file
  - [x] Debug an entire kubernetes config folder that contains yaml/yml files
  - [x] Pod management (list, get, logs, delete)
  - [ ] Deployment management (create, list, get, logs, delete)
  - [ ] Service management (Create, list, get, logs, delete)
  - [ ] Namespaces management (list, get, logs, delete)
  - [ ] Debug and Analyze Logs, Services, Seployment, Statefulset, Demonsets, Ingress, Node, Cluster
  - [ ] Portforward to a pod or service
  - [ ] Helm Chart installation and management


## Quickstart
1. Install Claude Desktop

3. Install this MCP server

- Using uv: `uv`

Run: `uv pip install git+https://github.com/ehiaig/kubernetes-mcp-server`

Or 

- Clone this repo:
`git clone https://github.com/ehiaig/kubernetes-mcp-server.git`

3. Open the Claude json file

  On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

  On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

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

Your `claude_desktop_config.json` file should look similar to this:

```
{
    "mcpServers": {
        "kubernetes-mcp-server": {
            "command": "/path/to/your/.local/bin/uv",
            "args": [
                "--directory",
                "/path/to/this/repo/kubernetes-mcp-server/src/k8s_manager",
                "run",
                "-m",
                "k8s_manager"
            ]
        }
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