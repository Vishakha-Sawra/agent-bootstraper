# Agent Bootstrapper - Repo Scanner

## Run locally
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn service.main:app --reload --port 8080

## Example scan (public repo)
curl -X POST http://127.0.0.1:8080/scan \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/tiangolo/fastapi.git"}'

## Example scan (private repo)
curl -X POST http://127.0.0.1:8080/scan \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/yourorg/privaterepo.git", "github_token":"ghp_..."}'
