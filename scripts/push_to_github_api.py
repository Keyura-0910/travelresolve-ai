"""
Script to push all project files directly to GitHub using the GitHub REST API.
Does not require git or gh CLI to be installed on the machine.
Developed by Keyura Motegaonkar.
"""

import os
import sys
import json
import base64
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".pytest_cache",
    "__pycache__",
    "scratch",
    ".git",
    ".venv",
    "venv",
    "env",
}

EXCLUDE_FILES = {
    "travelresolve.db",
    ".DS_Store",
    "Thumbs.db",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
}

def should_include(full_path: Path, project_root: Path) -> bool:
    rel_path = full_path.relative_to(project_root)
    for part in rel_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    if rel_path.name in EXCLUDE_FILES:
        return False
    if rel_path.suffix in EXCLUDE_EXTENSIONS:
        return False
    return True

def api_request(url: str, method: str = "GET", data: dict = None, token: str = None) -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "TravelResolve-Uploader",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req_body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
    
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def push_project_to_github(owner: str, repo: str, token: str, commit_message: str = "Initial commit: TravelResolve AI operations platform"):
    print(f"Connecting to GitHub: {owner}/{repo}...")
    
    # 0. Check if repository is empty and bootstrap if necessary
    repo_info = api_request(f"https://api.github.com/repos/{owner}/{repo}", method="GET", token=token)
    default_branch = repo_info.get("default_branch", "main")
    
    parent_sha = None
    try:
        ref_res = api_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{default_branch}",
            method="GET",
            token=token
        )
        parent_sha = ref_res["object"]["sha"]
        print(f"Found existing {default_branch} commit: {parent_sha}")
    except Exception:
        # Repository is empty; bootstrap with README.md via Contents API
        print(f"Repository is empty. Bootstrapping {default_branch} branch via Contents API...")
        readme_file = PROJECT_ROOT / "README.md"
        readme_bytes = readme_file.read_bytes() if readme_file.exists() else b"# TravelResolve AI\n"
        b64_readme = base64.b64encode(readme_bytes).decode("ascii")
        
        boot_res = api_request(
            f"https://api.github.com/repos/{owner}/{repo}/contents/README.md",
            method="PUT",
            data={
                "message": "Initialize repository with README",
                "content": b64_readme
            },
            token=token
        )
        parent_sha = boot_res["commit"]["sha"]
        print(f"Bootstrapped {default_branch} branch: {parent_sha}")

    # 1. Collect all project files
    files_to_upload = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            full_path = Path(root) / f
            if should_include(full_path, PROJECT_ROOT):
                rel_path = full_path.relative_to(PROJECT_ROOT).as_posix()
                files_to_upload.append((rel_path, full_path))
                
    print(f"Found {len(files_to_upload)} files to push.")
    
    # 2. Upload Blobs
    tree_items = []
    for idx, (rel_path, full_path) in enumerate(files_to_upload, start=1):
        content = full_path.read_bytes()
        b64_content = base64.b64encode(content).decode("ascii")
        
        blob_res = api_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/blobs",
            method="POST",
            data={"content": b64_content, "encoding": "base64"},
            token=token
        )
        blob_sha = blob_res["sha"]
        tree_items.append({
            "path": rel_path,
            "mode": "100644",
            "type": "blob",
            "sha": blob_sha
        })
        if idx % 10 == 0 or idx == len(files_to_upload):
            print(f"Uploaded {idx}/{len(files_to_upload)} blobs...")
            
    # 3. Create Tree
    print("Creating Git Tree...")
    tree_res = api_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees",
        method="POST",
        data={"tree": tree_items},
        token=token
    )
    tree_sha = tree_res["sha"]
    print(f"Created Tree: {tree_sha}")
        
    # 4. Create Commit
    print("Creating Git Commit...")
    commit_payload = {
        "message": commit_message,
        "tree": tree_sha,
        "parents": [parent_sha] if parent_sha else []
    }
        
    commit_res = api_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/commits",
        method="POST",
        data=commit_payload,
        token=token
    )
    commit_sha = commit_res["sha"]
    print(f"Created Commit: {commit_sha}")
    
    # 5. Update Ref
    api_request(
        f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{default_branch}",
        method="PATCH",
        data={"sha": commit_sha, "force": True},
        token=token
    )
    print(f"Updated branch refs/heads/{default_branch}.")
        
    print(f"\n============================================================")
    print(f"SUCCESS! All files pushed to: https://github.com/{owner}/{repo}")
    print(f"============================================================")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            print("Usage: python push_to_github_api.py <GITHUB_PERSONAL_ACCESS_TOKEN>")
            sys.exit(1)
    else:
        token = sys.argv[1].strip()
        
    push_project_to_github(owner="Keyura-0910", repo="travelresolve-ai", token=token)
