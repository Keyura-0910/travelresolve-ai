import os
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = PROJECT_ROOT.parent / "travelresolve-ai-release.zip"

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

print(f"Packaging {PROJECT_ROOT} -> {OUTPUT_ZIP}")
file_count = 0
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            full_path = root_path / f
            if should_include(full_path, PROJECT_ROOT):
                rel_path = full_path.relative_to(PROJECT_ROOT)
                zf.write(full_path, arcname=str(rel_path))
                file_count += 1

size_kb = OUTPUT_ZIP.stat().st_size / 1024
print(f"Packaged {file_count} files into {OUTPUT_ZIP} ({size_kb:.1f} KB)")
