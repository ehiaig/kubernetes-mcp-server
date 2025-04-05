from kubernetes import client, config
from pathlib import Path
import os
import yaml
from mcp.types import TextContent

config.load_kube_config()
v1 = client.CoreV1Api()


class K8SManager:
    def __init__(self):
        ...
        
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
        
        result = []
        for file in os.listdir(normalized_path):
            full_file_path = os.path.join(normalized_path, file)
            
            if os.path.isfile(full_file_path) and file.endswith(('.yaml', '.yml')):
                k8s_config = self.get_file_content(full_file_path)
                
                file_name = file.split("/")[-1]
                result.append(TextContent(type="text", text=f"{file_name}:'{k8s_config}'"))
        return result

    def get_pods_by_namespace(self, namespace):
        ret = v1.list_namespaced_pod(namespace=namespace)
        result = []
        for i in ret.items:
            result.append(
                TextContent(type="text", text=f"{i.metadata.name}{i.metadata.namespace}{i.status.pod_ip}")
            )
        return result

    def delete_namespace_pod(self, name, namespace):
        res = v1.delete_namespaced_pod(name=name, namespace=namespace)
        return [TextContent(type="text", text=f"Successfully deleted pod: {name} with response: {res}")]

    def delete_namespace_pods(self, namespace):
        ret = v1.list_namespaced_pod(namespace=namespace)
        for i in ret.items:
            v1.delete_namespaced_pod(name=i.metadata.name, namespace=namespace)
        return [TextContent(type="text", text=f"Successfully deleted pods in namespace: {namespace}")]
