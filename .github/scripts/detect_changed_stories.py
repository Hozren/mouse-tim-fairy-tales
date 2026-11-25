#!/usr/bin/env python3
"""Emit a GitHub Actions matrix for changed generated story directories."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath


ZERO_SHA = "0" * 40
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=not binary,
    )
    return result.stdout


def empty_tree() -> str:
    return str(git("hash-object", "-t", "tree", "/dev/null")).strip()


def commit_exists(revision: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0


def merge_base(base: str, head: str) -> str | None:
    result = subprocess.run(
        ["git", "merge-base", base, head],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def all_story_slugs(root: Path) -> set[str]:
    generated = root / "generated"
    if not generated.is_dir():
        return set()
    return {
        item.name
        for item in generated.iterdir()
        if item.is_dir() and SLUG_RE.fullmatch(item.name)
    }


def changed_story_slugs(root: Path, base: str, head: str) -> set[str]:
    raw_names = git(
        "diff",
        "--no-renames",
        "--name-only",
        "--diff-filter=ACDMRTUXB",
        "-z",
        base,
        head,
        "--",
        "generated/",
        binary=True,
    )
    names = bytes(raw_names).split(b"\0")
    slugs: set[str] = set()
    for raw_name in names:
        if not raw_name:
            continue
        name = raw_name.decode("utf-8", errors="surrogateescape")
        parts = PurePosixPath(name).parts
        if len(parts) < 3 or parts[0] != "generated":
            continue
        slug = parts[1]
        if SLUG_RE.fullmatch(slug) and (root / "generated" / slug).is_dir():
            slugs.add(slug)
    return slugs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=("push", "pull_request", "manual"), required=True)
    parser.add_argument("--base", default="", help="base Git revision")
    parser.add_argument("--head", default="HEAD", help="head Git revision")
    parser.add_argument("--default-branch", default="", help="repository default branch")
    parser.add_argument("--ref-name", default="", help="pushed branch name")
    parser.add_argument("--deleted", action="store_true", help="the pushed ref was deleted")
    parser.add_argument("--github-output", type=Path, help="append outputs to this file")
    args = parser.parse_args()

    root = Path.cwd().resolve()
    if args.event == "manual":
        slugs = all_story_slugs(root)
    elif args.event == "push" and (args.deleted or args.head == ZERO_SHA):
        slugs = set()
    else:
        if not commit_exists(args.head):
            raise SystemExit(f"error: head commit is unavailable: {args.head}")
        if args.event == "pull_request":
            if not commit_exists(args.base):
                raise SystemExit(f"error: pull request base commit is unavailable: {args.base}")
            base = merge_base(args.base, args.head)
            if not base:
                raise SystemExit("error: pull request base and head have no merge base")
        elif args.base and args.base != ZERO_SHA:
            if not commit_exists(args.base):
                raise SystemExit(f"error: push before commit is unavailable: {args.base}")
            base = args.base
        elif args.ref_name != args.default_branch and args.default_branch:
            default_ref = f"origin/{args.default_branch}"
            base = merge_base(default_ref, args.head) if commit_exists(default_ref) else None
            base = base or empty_tree()
        else:
            base = empty_tree()
        slugs = changed_story_slugs(root, base, args.head)
    include = [
        {"slug": slug, "path": f"generated/{slug}"}
        for slug in sorted(slugs)
    ]
    matrix = json.dumps({"include": include}, ensure_ascii=True, separators=(",", ":"))
    count = str(len(include))

    print(f"Detected {count} story directories")
    for item in include:
        print(f"  {item['path']}")

    output_path = args.github_output or (Path(os.environ["GITHUB_OUTPUT"]) if "GITHUB_OUTPUT" in os.environ else None)
    if output_path:
        with output_path.open("a", encoding="utf-8") as output:
            output.write(f"matrix={matrix}\n")
            output.write(f"count={count}\n")
    else:
        print(matrix)


if __name__ == "__main__":
    main()
