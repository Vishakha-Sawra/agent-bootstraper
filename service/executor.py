# service/executor.py
import os
import yaml
from typing import List, Dict

BASE_DIR = os.getcwd()
K8S_DIR = os.path.join(BASE_DIR, "k8s")

os.makedirs(K8S_DIR, exist_ok=True)


def normalize_args(tool: str, args: dict) -> dict:
    """
    Map Gemini's raw args into what our executor functions expect.
    Preserve the 'content' and 'file_path' fields that are needed by all tools.
    """
    # Always preserve these critical fields
    normalized = {
        "file_path": args.get("file_path"),
        "content": args.get("content")
    }
    
    if tool == "create_dockerfile":
        # Use run_command if provided, otherwise fallback from entrypoint_file
        run_cmd = args.get("run_command", f"python {args.get('entrypoint_file', 'main.py')}")
        normalized.update({
            # Set a default Python version; ignore extra 'language' key
            "python_version": "python:3.9",
            "requirements_file": args.get("requirements_file", "requirements.txt"),
            "port": args.get("port", 8000),
            "run_command": run_cmd,
            "entrypoint_file": args.get("entrypoint_file", "main.py")
        })

    elif tool == "write_docker_compose":
        normalized.update({
            "service_name": args.get("service_name"),
            "build_context": args.get("build_context"),
            "port_mapping": args.get("port_mapping"),
            "volumes": args.get("volumes", []),
            "environment": args.get("environment", {})
        })

    elif tool == "setup_ci_pipeline":
        normalized.update({
            "language": args.get("language", "python"),
            "test_command": args.get("test_command", "pytest")
        })

    elif tool == "generate_k8s_manifests":
        normalized.update({
            "app_name": args.get("app_name"),
            "image_name": args.get("image_name"),
            "port": args.get("port", 8000),
            "replicas": args.get("replicas", 1),
            "env_variables": args.get("env_variables", {})
        })

    elif tool == "deploy_to_cluster":
        normalized.update({
            "manifest_path": args.get("manifest_path"),
            "cluster_context": args.get("cluster_context", "default")
        })

    return normalized
# ---------------- Tool implementations ----------------
# Replace the implementations with the following:

def create_dockerfile(args: dict) -> str:
    """
    Write out the Dockerfile using the tailored content provided by Gemini.
    """
    file_path = args.get("file_path", "Dockerfile")
    content = args.get("content")
    if not content:
        raise ValueError("No Dockerfile content provided in plan JSON.")
    with open(file_path, "w") as f:
        f.write(content)
    return f"Dockerfile created successfully at {file_path}."


def write_docker_compose(args: dict) -> str:
    """
    Write out the docker-compose file using the provided content.
    """
    file_path = args.get("file_path", "docker-compose.yml")
    content = args.get("content")
    if not content:
        raise ValueError("No docker-compose content provided in plan JSON.")
    with open(file_path, "w") as f:
        f.write(content)
    return f"docker-compose.yml created successfully at {file_path}."


def setup_ci_pipeline(args: dict) -> str:
    """
    Write out the CI/CD pipeline file using the provided content.
    """
    file_path = args.get("file_path", os.path.join(".github", "workflows", "ci.yml"))
    content = args.get("content")
    if not content:
        raise ValueError("No CI pipeline content provided in plan JSON.")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    return f"CI pipeline configuration created successfully at {file_path}."


def generate_k8s_manifests(args: dict) -> str:
    """
    Write out the Kubernetes manifest file(s) using the provided content.
    Can handle both single file content (string) or multiple files (dict).
    """
    file_path = args.get("file_path", K8S_DIR)
    content = args.get("content")
    if not content:
        raise ValueError("No Kubernetes manifest content provided in plan JSON.")
    
    # Ensure the k8s directory exists
    os.makedirs(file_path if os.path.isdir(file_path) or file_path.endswith('/') else os.path.dirname(file_path), exist_ok=True)
    
    created_files = []
    
    if isinstance(content, dict):
        # Multiple files case
        for filename, file_content in content.items():
            full_path = os.path.join(file_path, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(file_content)
            created_files.append(full_path)
        return f"Kubernetes manifests created successfully: {', '.join(created_files)}"
    else:
        # Single file case
        if file_path.endswith('/') or os.path.isdir(file_path):
            full_path = os.path.join(file_path, "deployment.yml")
        else:
            full_path = file_path
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        return f"Kubernetes manifest created successfully at {full_path}"


def deploy_to_cluster(args: dict) -> str:
    """
    Simulate deployment to a cluster. This step might not produce a file.
    """
    return f"Application deployed to Kubernetes cluster (simulated) using manifest at {args.get('manifest_path')}"

# ---------------- Executor ----------------
def execute_plan(plan: List[Dict]) -> List[Dict]:
    results = []

    for step in plan:
        tool = step.get("tool")
        raw_args = step.get("args", {})
        args = normalize_args(tool, raw_args)

        try:
            if tool == "create_dockerfile":
                details = create_dockerfile(args)
            elif tool == "write_docker_compose":
                details = write_docker_compose(args)
            elif tool == "setup_ci_pipeline":
                details = setup_ci_pipeline(args)
            elif tool == "generate_k8s_manifests":
                details = generate_k8s_manifests(args)
            elif tool == "deploy_to_cluster":
                details = deploy_to_cluster(args)
            else:
                details = f"Unknown tool: {tool}"

            results.append({"tool": tool, "status": "success", "details": details})

        except Exception as e:
            results.append({
                "tool": tool,
                "status": "failed",
                "details": f"{step.get('on_fail', 'Step failed.')} | Error: {e}"
            })

    return results
