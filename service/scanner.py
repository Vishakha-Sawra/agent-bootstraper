# service/scanner.py
import os
from typing import Dict, List
import fnmatch

# helper to read a bit of file safely
def read_head(path: str, max_chars: int = 2000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    except Exception:
        return ""

def list_files(base: str) -> List[str]:
    files = []
    for root, _, filenames in os.walk(base):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(root, fn), base)
            files.append(rel.replace("\\", "/"))
    return files

def detect_languages(files: List[str]) -> List[str]:
    langs = set()
    for f in files:
        if f.endswith(".py"):
            langs.add("python")
        if f.endswith(".js") or f.endswith(".ts"):
            langs.add("javascript")
        if f.endswith(".html"):
            langs.add("html")
        if f.endswith(".css"):
            langs.add("css")
        if fnmatch.fnmatch(f, "*.go"):
            langs.add("go")
    return sorted(list(langs))

def detect_frameworks(base: str, files: List[str]) -> List[str]:
    content = ""
    for f in files:
        if f.endswith((".py", ".txt", ".md", "requirements.txt", "pyproject.toml", "Pipfile")):
            content += read_head(os.path.join(base, f))
            content += "\n"
    frameworks = []
    c = content.lower()
    if "fastapi" in c:
        frameworks.append("fastapi")
    if "flask" in c:
        frameworks.append("flask")
    if "django" in c:
        frameworks.append("django")
    if "sqlalchemy" in c:
        frameworks.append("sqlalchemy")
    if "alembic" in c:
        frameworks.append("alembic")
    if "react" in c or "create-react-app" in c:
        frameworks.append("react")
    if "vue" in c:
        frameworks.append("vue")
    return frameworks

def detect_database(base: str, files: List[str]) -> str | None:
    content = ""
    for f in files:
        if f.endswith((".py", "requirements.txt", "pyproject.toml", "Pipfile")):
            content += read_head(os.path.join(base, f))
    c = content.lower()
    if "psycopg2" in c or "postgresql" in c:
        return "postgres"
    if "mysqlclient" in c or "pymysql" in c:
        return "mysql"
    if "sqlite3" in c or "sqlite" in c:
        return "sqlite"
    return None

def find_entrypoints(base: str, files: List[str]) -> List[str]:
    candidates = []
    # common entrypoints
    for f in files:
        if f.endswith("main.py") or f.endswith("app.py") or f.endswith("wsgi.py"):
            candidates.append(f)
    # fallback: top-level package with uvicorn/gunicorn mention
    for f in files:
        if f.endswith(".py"):
            head = read_head(os.path.join(base, f))
            if "uvicorn" in head or "gunicorn" in head:
                candidates.append(f)
    return sorted(list(dict.fromkeys(candidates)))  # preserve order unique

def detect_infra(files: List[str]) -> Dict:
    infra = {
        "dockerfile": any(f.lower().endswith("dockerfile") or f.lower().endswith("dockerfile.j2") for f in files),
        "docker_compose": any("docker-compose" in f.lower() or f.lower().endswith("compose.yaml") for f in files),
        "k8s_manifests": any(f.endswith((".yaml", ".yml")) and ("k8s" in f.lower() or "deployment" in f.lower() or "service" in f.lower()) for f in files),
        "ci": any(f.lower().startswith(".github/") or "gitlab-ci" in f.lower() or ".circleci" in f.lower() for f in files),
    }
    return infra

def scan_repo(path: str) -> Dict:
    files = list_files(path)
    languages = detect_languages(files)
    frameworks = detect_frameworks(path, files)
    db = detect_database(path, files)
    entrypoints = find_entrypoints(path, files)
    infra = detect_infra(files)
    has_tests = any(f.startswith("tests/") or f.endswith("_test.py") or f.endswith("test.py") for f in files)

    return {
        "project_name": os.path.basename(path.rstrip("/")),
        "languages": languages,
        "frameworks": frameworks,
        "database": db,
        "has_tests": has_tests,
        "entrypoints": entrypoints,
        "infrastructure": infra,
        "discovered_files": files
    }
