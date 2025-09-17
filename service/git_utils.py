# service/git_utils.py
import tempfile
import os
import shutil
from typing import Optional, Tuple
from git import Repo, GitCommandError

def clone_repo(repo_url: str, branch: Optional[str] = None, github_token: Optional[str] = None, timeout: int = 60) -> Tuple[str, str]:
    """
    Clones repo into a fresh temp directory.
    Returns: (path_to_repo, note)
    - Supports private repos by embedding token into HTTPS URL.
      WARNING: token appears in process args if you use subprocess; GitPython hides it better.
    """
    tmpdir = tempfile.mkdtemp(prefix="repo_")
    sanitized_url = repo_url
    note = None

    if github_token:
        # Embed token in HTTPS url: https://<token>@github.com/owner/repo.git
        # Keep origin URL without token for response
        if repo_url.startswith("https://"):
            sanitized_url = repo_url.replace("https://", f"https://{github_token}@")
            note = "Cloned with provided github_token (private repo). Make sure token has minimal scopes (repo:read)."
        else:
            # For non-https urls, fallback to direct clone (may fail)
            sanitized_url = repo_url

    try:
        repo = Repo.clone_from(sanitized_url, tmpdir, no_single_branch=True)
        # checkout branch if provided
        if branch:
            try:
                repo.git.checkout(branch)
            except GitCommandError:
                # try fetching remote branch and checking out
                repo.git.fetch("origin", branch)
                repo.git.checkout(branch)
    except Exception as e:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise RuntimeError(f"git clone failed: {e}")

    return tmpdir, note or "Cloned successfully"
