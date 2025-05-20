from __future__ import annotations


import argparse
import datetime as _dt
import subprocess
import tempfile
from pathlib import Path
from tqdm import tqdm


def count_lines_in_file(path: Path) -> tuple[int, int]:
    """Return total and code lines for a single file."""
    total = 0
    code = 0
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total += 1
                if line.strip():
                    code += 1
    except (UnicodeDecodeError, OSError):
        return 0, 0
    return total, code


def calc_lines(directory: Path) -> tuple[int, int]:
    """Walk a directory tree and return total and code line counts."""
    total = 0
    code = 0

    # First count total files
    files = [p for p in directory.rglob("*") if p.is_file() and ".git" not in p.parts]

    # Process files with progress bar
    for path in tqdm(files, desc="Counting lines", unit="file"):
        t, c = count_lines_in_file(path)
        total += t
        code += c
    return total, code


__all__ = ["count_lines_in_file", "calc_lines", "main"]


def main() -> None:
    """Calculate lines of code in a remote git repository.

    Usage:
        python calc_repo_lines.py <repository_url> [--branch <branch_name>]

    Arguments:
        repository_url    URL of the git repository to analyze (e.g., https://github.com/user/repo)
        --branch         Optional branch name to analyze (defaults to repository's default branch)

    Example:
        python calc_repo_lines.py https://github.com/user/repo --branch main
    """
    parser = argparse.ArgumentParser(
        description="Calculate lines of a remote repository"
    )
    parser.add_argument("repo", help="URL of the git repository")
    parser.add_argument(
        "--branch", help="Branch to checkout; defaults to repo default branch"
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        clone_cmd = ["git", "clone", "--depth", "1"]
        if args.branch:
            clone_cmd += ["--branch", args.branch]
        clone_cmd += [args.repo, tmp]
        subprocess.run(clone_cmd, check=True)
        total, code = calc_lines(Path(tmp))

    print(f"# lines: {total}")
    print(f"# code lines: {code}")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    results_file = data_dir / "results.txt"
    now = (
        _dt.datetime.now(_dt.UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    line = f"Repo: {args.repo} | # lines: {total} | # code lines: {code} | Datetime: {now}\n"
    with results_file.open("a", encoding="utf-8") as f:
        f.write(line)


if __name__ == "__main__":
    main()
