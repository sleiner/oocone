import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent


def release(
    new_version: str,
    *,
    dry_run: bool = False,
    commit: bool = True,
) -> None:
    print(f"Bump version to: {new_version}")
    if dry_run:
        subprocess.check_call(["towncrier", "build", "--version", new_version, "--draft"])
    else:
        subprocess.check_call(["towncrier", "build", "--yes", "--version", new_version])
        subprocess.check_call(["git", "add", "."])
        if commit:
            subprocess.check_call(["git", "commit", "-m", f"Release {new_version}"])
            subprocess.check_call(["git", "tag", "-a", new_version, "-m", f"v{new_version}"])
            subprocess.check_call(["git", "push"])
            subprocess.check_call(["git", "push", "--tags"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument(
        "--no-commit",
        action="store_false",
        dest="commit",
        default=True,
        help="Do not commit to Git",
    )
    parser.add_argument("version", help="Version number according to PEP 440")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    release(args.version, dry_run=args.dry_run, commit=args.commit)
