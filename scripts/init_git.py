import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
git_dir = PROJECT_ROOT / ".git"

if not git_dir.exists():
    git_dir.mkdir(parents=True, exist_ok=True)
    (git_dir / "objects").mkdir(exist_ok=True)
    (git_dir / "objects" / "info").mkdir(exist_ok=True)
    (git_dir / "objects" / "pack").mkdir(exist_ok=True)
    (git_dir / "refs").mkdir(exist_ok=True)
    (git_dir / "refs" / "heads").mkdir(exist_ok=True)
    (git_dir / "refs" / "tags").mkdir(exist_ok=True)
    (git_dir / "hooks").mkdir(exist_ok=True)
    (git_dir / "info").mkdir(exist_ok=True)

    # HEAD points to main branch
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    # Config file
    config_content = """[core]
\trepositoryformatversion = 0
\tfilemode = false
\tbare = false
\tlogallrefupdates = true
\tsymlinks = false
\tignorecase = true
"""
    (git_dir / "config").write_text(config_content, encoding="utf-8")
    (git_dir / "description").write_text("TravelResolve AI - Booking-Aware Multi-Agent Support Automation\n", encoding="utf-8")
    print(f"Initialized Git repository structure at: {git_dir}")
else:
    print(f"Git repository already exists at: {git_dir}")
