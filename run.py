from mcp.server import NotificationOptions, Server
import logging
from pathlib import Path
import os
from mcp.server.models import InitializationOptions
from typing import Optional, List
import mcp.server.stdio
from mcp.types import (
    TextContent,
    Tool,
    Resource,
    INTERNAL_ERROR,
    Prompt,
    PromptArgument,
    EmbeddedResource,
    GetPromptResult,
    PromptMessage,
)
from pydantic import BaseModel, AnyUrl
from enum import Enum
import yaml

logger = logging.getLogger(__name__)


class ScriptRunner:
    def __init__(self):
        self.data = {}
        self.notes: list[str] = []
        
    def get_file_content(self, file_path):
        file_content = Path(file_path).read_text()
        k8s_config = yaml.safe_load(file_content)
        return k8s_config if k8s_config else ""
        
    def read_k8s_yaml(self, file_path):
        """
        Reads a Kubernetes YAML file and returns its contents as a Python dictionary.
        
        :param file_path: Path to the Kubernetes YAML file.
        :return: Parsed YAML content as a dictionary.
        """
        try:

            file_name = file_path.split("/")[-1]
            k8s_config = self.get_file_content(file_path)
            return [
                TextContent(type="text", text=f"{file_name}:'{k8s_config}'")
            ]
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")

    def get_files_in_directory(self, directory):
        """
        Returns a list of files in the given directory.
        
        :param directory: Path to the directory.
        :return: List of file names in the directory.
        """
        expanded_path = os.path.expanduser(directory)
    
        # Normalize path (resolve '..' and '.' components)
        normalized_path = os.path.normpath(expanded_path)
        
        # Make path absolute if it's relative
        if not os.path.isabs(normalized_path):
            normalized_path = os.path.abspath(normalized_path)
        
        # Check if directory exists
        if not os.path.exists(normalized_path):
            raise FileNotFoundError(f"Directory not found: {normalized_path}")
        
        # Check if path is a directory
        if not os.path.isdir(normalized_path):
            raise NotADirectoryError(f"Path is not a directory: {normalized_path}")
    
        self.notes.append(f"Getting files in directory {normalized_path}")
        test_res = []
        for file in os.listdir(normalized_path):
            full_file_path = os.path.join(normalized_path, file)
            
            if os.path.isfile(full_file_path) and file.endswith(('.yaml', '.yml')):
                k8s_config = self.get_file_content(full_file_path)
                
                file_name = file.split("/")[-1]
                test_res.append(TextContent(type="text", text=f"{file_name}:'{k8s_config}'"))
        return test_res


class K8STools(str, Enum):
    GET_K8S_DIRECTORY = "get_files_in_directory"
    GET_K8S_FILE = "read_k8s_yaml"

class K8sPrompts(str, Enum):
    EXPLORE_FOLDER = "list-folder"
    EXPLORE_FILE = "get-file"

class GetDirectorySchema(BaseModel):
    folder_path: str

class GetFileSchema(BaseModel):
    full_file_path: str

class PromptArgs(str, Enum):
    FOLDER_PATH = "folder_path"
    FULL_FILE_PATH= "full_file_path"


GET_DIRECTORY_TOOL_DESCRIPTION = """
Load Kubernetes YAML configurations folder

Purpose:
Load Kubernetes YAML configurations folder for analysis.

Usage Notes:
	•	If a folder_path is not provided, the tool will display [].
"""

GET_FILE_TOOL_DESCRIPTION = """
Load Kubernetes YAML configurations file

Purpose:
Load Kubernetes YAML configurations file for analysis

Prohibited Actions
	1.	Overwriting Original kubernetes configuration file: Do not modify existing YAML configurations, simply.
"""


FILE_PATH_PROMPT_TEMPLATE = """
You are an expert Kubernetes configuration analyzer. Your task is to review YAML configurations for Kubernetes resources, identify misconfigurations, and provide fixes. You should ensure your responses are structured and actionable.

Load the given kubernetes .yaml or .yml file from the following path:

<full_file_path>
{full_file_path}
</full_file_path>


You have access to the following tools for your analysis:
1. read_k8s_yaml: Use this to load the kubernetes .yaml or .yml file.

Please follow these steps carefully:

1. Load the kubernetes .yaml or .yml file using the get_files_in_directory tool.

2. Analyze the provided Kubernetes configuration for misconfigurations and security issues. Specifically check for:
    - Missing required fields
    - Incorrect syntax, indentation, label or metadata
    - Invalid API versions
    - Security best practices violations (e.g., running as root, privileged containers)
    - Resource constraints missing
    - Network policy issues
    - Pod security context problems
    - Deprecated API usage

Remember to prioritize stability and manageability in your review. If at any point you encounter potential issues with file, adjust your approach accordingly.

Please begin your analysis by loading the kubernetes .yaml or .yml file file and providing an initial exploration of the file.
"""

FOLDER_PATH_PROMPT_TEMPLATE = """
You are an expert Kubernetes configuration analyzer. Your task is to review YAML configurations for Kubernetes resources, identify misconfigurations, and provide fixes. You should ensure your responses are structured and actionable.

Go through the folder at the directory:

<folder_path>
{folder_path}
</folder_path>


You have access to the following tools for your analysis:
1. get_files_in_directory: Use this to load each of the kubernetes .yaml or .yml file.

Please follow these steps carefully:

1. Load each kubernetes .yaml or .yml file using the get_files_in_directory tool.

2. For each file, analyze the provided Kubernetes configuration for misconfigurations and security issues. Specifically check for:
    - Missing required fields
    - Incorrect syntax, indentation, label or metadata
    - Invalid API versions
    - Security best practices violations (e.g., running as root, privileged containers)
    - Resource constraints missing
    - Network policy issues
    - Pod security context problems
    - Deprecated API usage

Remember to prioritize stability and manageability in your review. If at any point you encounter potential issues with file, adjust your approach accordingly.

Please begin your analysis by loading the kubernetes .yaml or .yml file file and providing an initial exploration of the file.
"""

### MCP Server Definition
async def main():
    script_runner = ScriptRunner()
    server = Server("k8s-mcp")

    # @server.list_resources()
    # async def handle_list_resources() -> list[Resource]:
    #     logger.debug("Handling list_resources request")
    #     return [
    #         Resource(
    #             uri="k8s-exploration://notes",
    #             name="Kubernetes Exploration Notes",
    #             description="Notes generated by the data exploration server",
    #             mimeType="text/plain",
    #         )
    #     ]

    # @server.read_resource()
    # async def handle_read_resource(uri: AnyUrl) -> str:
    #     logger.debug(f"Handling read_resource request for URI: {uri}")
    #     if uri == "k8s-exploration://notes":
    #         return "\n".join(script_runner.notes)
    #     else:
    #         raise ValueError(f"Unknown resource: {uri}")

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
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ):
        logger.debug(f"Handling call_tool request for {name} with args {arguments}")
        if name == K8STools.GET_K8S_FILE:
            full_file_path = arguments.get("full_file_path")
            return script_runner.read_k8s_yaml(full_file_path)
        elif name == K8STools.GET_K8S_DIRECTORY:
            folder_path = arguments.get("folder_path")
            return script_runner.get_files_in_directory(folder_path)
        else:
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

    

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())