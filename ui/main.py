# ui/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
import json
import os
from datetime import datetime
# UI FastAPI app
app = FastAPI(title="Agentic UI")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount templates + static files
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)


BACKEND_URL = "http://127.0.0.1:8080"  # adjust if backend runs elsewhere

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scan", response_class=HTMLResponse)
async def ui_scan(request: Request, repo_url: str = Form(...), branch: str = Form("main")):
    # Call backend /scan
    scan_response = requests.post(
        f"{BACKEND_URL}/scan",
        json={"repo_url": repo_url, "branch": branch}
    ).json()
    return templates.TemplateResponse("plan.html", {"request": request, "scan": scan_response})

@app.post("/plan", response_class=HTMLResponse)
async def ui_plan(request: Request, project_data: str = Form(...)):
    project_json = json.loads(project_data)
    plan_response = requests.post(
        f"{BACKEND_URL}/plan",
        json=project_json
    ).json()
    return templates.TemplateResponse("plan_results.html", {
        "request": request,
        "scan": project_json,
        "plan": plan_response
    })

@app.post("/execute", response_class=HTMLResponse)
async def ui_execute(request: Request, plan_data: str = Form(...)):
    plan_json = json.loads(plan_data)
    exec_response = requests.post(f"{BACKEND_URL}/execute", json=plan_json).json()
    return templates.TemplateResponse("execute.html", {
        "request": request,
        "plan": exec_response["execution_results"],
        "files": exec_response.get("files", [])
    })

@app.post("/download-execution-results")
async def download_execution_results(execution_data: str = Form(...), files_data: str = Form(...)):
    """Generate and serve a markdown file containing execution results"""
    try:
        execution_results = json.loads(execution_data)
        files = json.loads(files_data)
        
        # Generate markdown content
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"execution_results_{timestamp}.md"
        
        markdown_content = f"""# Execution Results Report

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Execution Summary

"""
        
        # Add execution results
        if execution_results:
            markdown_content += "### Execution Status\n\n"
            for result in execution_results:
                status_emoji = "✅" if result.get("status") == "success" else "❌" if result.get("status") == "failed" else "⚠️"
                markdown_content += f"- **{result.get('tool', 'Unknown')}**: {status_emoji} {result.get('status', 'unknown')}\n"
                if result.get("details"):
                    markdown_content += f"  - Details: {result.get('details')}\n"
                markdown_content += "\n"
        
        # Add generated files
        if files:
            markdown_content += "## Generated Files\n\n"
            for file in files:
                markdown_content += f"### {file.get('tool', 'Unknown Tool')} - {file.get('file_path', 'Unknown Path')}\n\n"
                markdown_content += f"**File Path:** `{file.get('file_path', 'Unknown')}`\n\n"
                markdown_content += "**Content:**\n\n"
                markdown_content += f"```\n{file.get('content', '')}\n```\n\n"
                markdown_content += "---\n\n"
        
        # Return the markdown file as a download
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/markdown; charset=utf-8"
            }
        )
        
    except Exception as e:
        return Response(
            content=f"Error generating markdown: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )

@app.post("/download-plan")
async def download_plan(plan_data: str = Form(...), scan_data: str = Form(...)):
    """Generate and serve a markdown file containing the execution plan"""
    try:
        plan = json.loads(plan_data)
        scan = json.loads(scan_data)
        
        # Generate markdown content
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"execution_plan_{timestamp}.md"
        
        markdown_content = f"""# Execution Plan Report

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Project Information

"""
        
        # Add scan information
        if scan:
            markdown_content += f"**Repository:** {scan.get('repo_url', 'Unknown')}\n"
            markdown_content += f"**Branch:** {scan.get('branch', 'Unknown')}\n"
            markdown_content += f"**Project Name:** {scan.get('project_name', 'Unknown')}\n\n"
            
            if scan.get('languages'):
                markdown_content += f"**Languages:** {', '.join(scan.get('languages', []))}\n"
            if scan.get('frameworks'):
                markdown_content += f"**Frameworks:** {', '.join(scan.get('frameworks', []))}\n"
            if scan.get('database'):
                markdown_content += f"**Database:** {scan.get('database')}\n"
            markdown_content += "\n"
        
        # Add plan steps
        if plan:
            markdown_content += "## Execution Plan Steps\n\n"
            for i, step in enumerate(plan, 1):
                markdown_content += f"### Step {i}: {step.get('tool', 'Unknown Tool')}\n\n"
                markdown_content += f"**File Path:** `{step.get('args', {}).get('file_path', 'N/A')}`\n\n"
                
                if step.get('args', {}).get('content'):
                    markdown_content += "**Generated Content:**\n\n"
                    markdown_content += f"```\n{step.get('args', {}).get('content', '')}\n```\n\n"
                
                if step.get('success_check'):
                    markdown_content += f"**Success Check:** {step.get('success_check')}\n\n"
                
                if step.get('on_fail'):
                    markdown_content += f"**On Failure:** {step.get('on_fail')}\n\n"
                
                markdown_content += "---\n\n"
        
        # Return the markdown file as a download
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "text/markdown; charset=utf-8"
            }
        )
        
    except Exception as e:
        return Response(
            content=f"Error generating markdown: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )