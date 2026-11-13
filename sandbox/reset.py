#!/usr/bin/env python
"""Explicitly remove only the fixed sandbox data directory."""

import argparse
import shutil
from pathlib import Path


def reset_data(project_dir):
    data = project_dir / ".data"
    if data.is_symlink():
        raise ValueError("Refusing to reset a symlinked sandbox data directory")
    if data.exists():
        shutil.rmtree(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--yes", action="store_true", help="Confirm deleting sandbox data"
    )
    args = parser.parse_args()
    if not args.yes:
        parser.error(
            "Pass --yes to delete sandbox/.data; stop the sandbox server first"
        )
    reset_data(Path(__file__).resolve().parent)
    print("Removed sandbox/.data. Run make sandbox-setup to restore the examples.")
