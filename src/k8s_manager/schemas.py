from enum import Enum
from pydantic import BaseModel
from typing import Optional

class K8STools(str, Enum):
    GET_K8S_DIRECTORY = "get_files_in_directory"
    GET_K8S_FILE = "read_k8s_yaml"
    GET_NAMESPACE_PODS = "get_pods_by_namespace"
    DELETE_NAMESPACE_POD = "delete_namespace_pod"
    DELETE_NAMESPACE_PODS = "delete_namespace_pods"

class K8sPrompts(str, Enum):
    EXPLORE_FOLDER = "list-folder"
    EXPLORE_FILE = "get-file"
    GET_PODS = "get-pods"
    DELETE_POD = "delete-pod"
    DELETE_PODS = "delete-pods"

class GetDirectorySchema(BaseModel):
    folder_path: str

class GetFileSchema(BaseModel):
    full_file_path: str

class GetPodSchema(BaseModel):
    namespace: str

class DeletePodSchema(BaseModel):
    name: str
    namespace: str


class PromptArgs(str, Enum):
    FOLDER_PATH = "folder_path"
    FULL_FILE_PATH = "full_file_path"
    NAMESPACE = "namespace"
    NAME = "name"