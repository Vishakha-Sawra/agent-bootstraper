# service/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from service.schemas import ScanRequest, ScanResponse
from service.git_utils import clone_repo
from service.scanner import scan_repo
from service.planner import generate_plan
import shutil
import os
import traceback

app = FastAPI(title="Agent Bootstrapper - Repo Scanner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/scan", response_model=ScanResponse)
def scan_endpoint(req: ScanRequest):
    """
    Clone the repo (public or private if token supplied), run scanner, and return JSON summary.
    """
    repo_url = req.repo_url
    branch = req.branch
    token = req.github_token.get_secret_value() if req.github_token else None

    try:
        path, note = clone_repo(repo_url, branch=branch, github_token=token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repo: {e}")

    try:
        summary = scan_repo(path)
        summary["repo_url"] = str(repo_url)
        summary["branch"] = branch
        resp = {
            "project_name": summary.get("project_name"),
            "repo_url": summary.get("repo_url"),
            "branch": summary.get("branch"),
            "languages": summary.get("languages", []),
            "frameworks": summary.get("frameworks", []),
            "database": summary.get("database"),
            "has_tests": summary.get("has_tests", False),
            "entrypoints": summary.get("entrypoints", []),
            "infrastructure": summary.get("infrastructure", {}),
            "discovered_files": summary.get("discovered_files", [])[:1000],  # cap list
            "note": note
        }
        return resp
    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}\n{tb}")
    finally:
        # cleanup - keep option to persist for debugging by env var
        try:
            persist = os.getenv("AGENT_PERSIST_WORKSPACE", "0")
            if persist != "1":
                shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass


@app.post("/plan")
def plan_endpoint(scan_summary: dict = Body(...)):
    """
    Accepts scan summary JSON, calls Gemini to generate a structured plan.
    """
    try:
        plan_json = generate_plan(scan_summary)
        return plan_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planner failed: {e}")

@app.post("/execute")
def execute_plan(plan: list[dict] = Body(...)):
    import os
    from service.executor import normalize_args, create_dockerfile, write_docker_compose, setup_ci_pipeline, generate_k8s_manifests, deploy_to_cluster

    execution_results = []
    file_results = []  # collect generated files

    for step in plan:
        tool = step.get("tool")
        raw_args = step.get("args", {})
        args = normalize_args(tool, raw_args)
        success_check = step.get("success_check", "")
        on_fail = step.get("on_fail", "")
        result = {"tool": tool, "status": None, "details": ""}

        try:
            if tool == "create_dockerfile":
                create_dockerfile(args)
                file_path = raw_args.get("file_path", "Dockerfile")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                    file_results.append({"tool": tool, "file_path": file_path, "content": content})
            elif tool == "write_docker_compose":
                write_docker_compose(args)
                file_path = raw_args.get("file_path", "docker-compose.yml")
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                    file_results.append({"tool": tool, "file_path": file_path, "content": content})
            elif tool == "setup_ci_pipeline":
                setup_ci_pipeline(args)
                file_path = raw_args.get("file_path", os.path.join(".github", "workflows", "ci.yml"))
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        content = f.read()
                    file_results.append({"tool": tool, "file_path": file_path, "content": content})
            elif tool == "generate_k8s_manifests":
                generate_k8s_manifests(args)
                # Handle both single file and directory cases
                file_path = raw_args.get("file_path", "k8s/")
                if file_path.endswith('/') or os.path.isdir(file_path):
                    # Directory case - collect all files
                    if os.path.exists(file_path):
                        for filename in os.listdir(file_path):
                            full_path = os.path.join(file_path, filename)
                            if os.path.isfile(full_path):
                                with open(full_path, "r") as f:
                                    content = f.read()
                                file_results.append({"tool": tool, "file_path": full_path, "content": content})
                else:
                    # Single file case
                    if os.path.exists(file_path):
                        with open(file_path, "r") as f:
                            content = f.read()
                        file_results.append({"tool": tool, "file_path": file_path, "content": content})
            elif tool == "deploy_to_cluster":
                deploy_to_cluster(args)
                # deploy_to_cluster may not generate a file
            else:
                result["status"] = "skipped"
                result["details"] = f"Unknown tool: {tool}"
                execution_results.append(result)
                continue

            result["status"] = "success"
            result["details"] = success_check

        except Exception as e:
            result["status"] = "failed"
            result["details"] = f"{on_fail} | Error: {e}"
        execution_results.append(result)

    return {"execution_results": execution_results, "files": file_results}