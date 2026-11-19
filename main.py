"""Copy the pre-rendered image to make.fun's output directory."""
import os
from pathlib import Path
import shutil


def main():
    # Resolve relative to this file because the grader invokes us from another cwd.
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        raise FileNotFoundError(f"Pre-rendered entry image not found: {source}")
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    # The requested destination may not exist yet in the sandbox.
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output_dir / "entry.png")


if __name__ == "__main__":
    main()
