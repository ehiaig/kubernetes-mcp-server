from mcp.server import NotificationOptions, Server
import logging
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.types import (
    TextContent,
    Tool,
    Prompt,
    PromptArgument,
    GetPromptResult,
    PromptMessage,
)
from k8s_manager.schemas import K8STools, K8sPrompts, GetDirectorySchema, GetFileSchema, GetPodSchema, PromptArgs, DeletePodSchema
from k8s_manager.prompt_templates import FILE_PATH_PROMPT_TEMPLATE, FOLDER_PATH_PROMPT_TEMPLATE, GET_NAMESPACE_PROMPT_TEMPLATE, DELETE_POD_PROMPT_TEMPLATE, DELETE_PODS_PROMPT_TEMPLATE
from k8s_manager.manager import K8SManager

logger = logging.getLogger(__name__)

GET_DIRECTORY_TOOL_DESCRIPTION = """
Load Kubernetes YAML configurations in the supplied folder. 
If a folder_path is not provided, the tool will display [].
"""

GET_FILE_TOOL_DESCRIPTION = """
Load Kubernetes YAML configurations in the supplied file path. If a file path is not provided, the tool will display "".
Do not modify existing YAML configurations, simply anaylyse and state where there are potential misconfigurations.
"""

### MCP Server Definition
async def main():
    runner = K8SManager()
    server = Server("k8s-manager-mcp")

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        logger.debug("Handling list_tools request")
        return [
            Tool(
                name = K8STools.GET_K8S_DIRECTORY,
                description = GET_DIRECTORY_TOOL_DESCRIPTION,
                inputSchema = GetDirectorySchema.model_json_schema(),
            ),
            Tool(
                name=K8STools.GET_K8S_FILE,
                description=GET_FILE_TOOL_DESCRIPTION,
                inputSchema=GetFileSchema.model_json_schema(),
            ),
            Tool(
                name=K8STools.GET_NAMESPACE_PODS,
                description="Get the list of pods in the given namespace.",
                inputSchema=GetPodSchema.model_json_schema(),
            ),
            Tool(
                name=K8STools.DELETE_NAMESPACE_POD,
                description="Delete the pod with the given name and namespace.",
                inputSchema=DeletePodSchema.model_json_schema(),
            ),
            Tool(
                name=K8STools.DELETE_NAMESPACE_PODS,
                description="Delete all pods in the given namespace.",
                inputSchema=GetPodSchema.model_json_schema(), #GetPodSchema because it's same schema
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ):
        logger.debug(f"Handling call_tool request for {name} with args {arguments}")
        match name:
            case K8STools.GET_K8S_FILE:
                full_file_path = arguments.get("full_file_path")
                return runner.read_k8s_yaml(full_file_path)
            case  K8STools.GET_K8S_DIRECTORY:
                folder_path = arguments.get("folder_path")
                return runner.get_files_in_directory(folder_path)
            case K8STools.GET_NAMESPACE_PODS:
                namespace = arguments.get("namespace")
                return runner.get_pods_by_namespace(namespace)
            case K8STools.DELETE_NAMESPACE_POD:
                namespace = arguments.get("namespace")
                return runner.delete_namespace_pod(name, namespace)
            case K8STools.DELETE_NAMESPACE_PODS:
                namespace = arguments.get("namespace")
                return runner.delete_namespace_pods(namespace)
            case _:
                raise logger.exception(f"Unknown tool: {name}")

    @server.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        logger.debug("Handling list_prompts request")
        return [
            Prompt(
                name=K8sPrompts.EXPLORE_FILE,
                description="A prompt to explore a k8s file as a devops engineer",
                arguments=[
                    PromptArgument(
                        name=PromptArgs.FULL_FILE_PATH,
                        description="The path to the k8 file",
                        required=False,
                    ),
                ],
            ),
            Prompt(
                name=K8sPrompts.EXPLORE_FOLDER,
                description="A prompt to explore a k8s folder as a devops engineer",
                arguments=[
                    PromptArgument(
                        name=PromptArgs.FOLDER_PATH,
                        description="The path to the k8 folder",
                        required=True,
                    ),
                ],
            ),
            Prompt(
                name=K8sPrompts.GET_PODS,
                description="A prompt to explore a k8s folder as a devops engineer",
                arguments=[
                    PromptArgument(
                        name=PromptArgs.NAMESPACE,
                        description="The path to the k8 folder",
                        required=True,
                    ),
                ],
            ),

        ]
    
    @server.get_prompt()
    async def handle_get_file(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != K8sPrompts.EXPLORE_FILE:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.FULL_FILE_PATH not in arguments:
            logger.error("Missing required arguments: full_file_path")
            raise ValueError("Missing required arguments: full_file_path")

        full_file_path = arguments[PromptArgs.FULL_FILE_PATH]
        prompt = FILE_PATH_PROMPT_TEMPLATE.format(full_file_path=full_file_path)

        logger.debug(f"Generated prompt template for file_path: {full_file_path}")
        return GetPromptResult(
            description=f"Kubernetes configuration exploration template for {full_file_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )
    
    @server.get_prompt()
    async def handle_get_folder(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != K8sPrompts.EXPLORE_FOLDER:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.FOLDER_PATH not in arguments:
            logger.error("Missing required argument: folder_path")
            raise ValueError("Missing required argument: folder_path")

        folder_path = arguments[PromptArgs.FOLDER_PATH]
        prompt = FOLDER_PATH_PROMPT_TEMPLATE.format(folder_path=folder_path)
        logger.debug(f"Generated prompt template for file_path: {folder_path}")
        return GetPromptResult(
            description=f"Kubernetes configuration exploration template for {folder_path}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )
    
    @server.get_prompt()
    async def handle_get_pods(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != K8sPrompts.GET_PODS:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.NAMESPACE not in arguments:
            logger.error("Missing required argument: namespace")
            raise ValueError("Missing required argument: namespace")

        namespace = arguments[PromptArgs.NAMESPACE]
        prompt = GET_NAMESPACE_PROMPT_TEMPLATE.format(namespace=namespace)
        logger.debug(f"Generated prompt template for pod namespace: {namespace}")
        return GetPromptResult(
            description=f"Retrieving pods in the namespace: {namespace}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )
    
    @server.get_prompt()
    async def handle_delete_pod(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != K8sPrompts.DELETE_POD:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.NAMESPACE not in arguments or PromptArgs.NAME not in arguments:
            logger.error("Missing required argument: namespace or pod name")
            raise ValueError("Missing required argument: namespace or pod name")

        namespace = arguments[PromptArgs.NAMESPACE]
        pod_name = arguments[PromptArgs.NAME]
        prompt = DELETE_POD_PROMPT_TEMPLATE.format(name=pod_name, namespace=namespace)
        logger.debug(f"Generated prompt template for deleting pod: {namespace}")
        return GetPromptResult(
            description=f"Delete pod with the given name: {pod_name}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )
    
    @server.get_prompt()
    async def handle_delete_pods(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
        logger.debug(f"Handling get_prompt request for {name} with args {arguments}")
        if name != K8sPrompts.DELETE_PODS:
            logger.error(f"Unknown prompt: {name}")
            raise ValueError(f"Unknown prompt: {name}")

        if not arguments or PromptArgs.NAMESPACE not in arguments:
            logger.error("Missing required argument: namespace")
            raise ValueError("Missing required argument: namespace")

        namespace = arguments[PromptArgs.NAMESPACE]
        prompt = DELETE_PODS_PROMPT_TEMPLATE.format(namespace=namespace)
        logger.debug(f"Generated prompt template for deleting pods in namespace: {namespace}")
        return GetPromptResult(
            description=f"Delete pods in the given namespace: {namespace}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt.strip()),
                )
            ],
        )
        
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.debug("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="data-exploration-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

