# service/schemas.py
from pydantic import BaseModel, HttpUrl, Field, SecretStr
from typing import Optional

class ScanRequest(BaseModel):
    repo_url: HttpUrl = Field(..., description="HTTPS url to the GitHub repository (https://github.com/org/repo.git)")
    branch: Optional[str] = Field(None, description="Optional branch or ref to checkout")
    github_token: Optional[SecretStr] = Field(None, description="Optional personal access token to clone private repos (sent securely)")

class ScanResponse(BaseModel):
    project_name: str
    repo_url: str
    branch: Optional[str]
    languages: list[str]
    frameworks: list[str]
    database: Optional[str] = None
    has_tests: bool
    entrypoints: list[str]
    infrastructure: dict
    discovered_files: list[str]
    note: Optional[str] = None
