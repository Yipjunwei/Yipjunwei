#!/usr/bin/env python3
"""
Build the full Jun Wei profile surface from source files.

This script is the single command for local updates. It checks timestamps and
only reruns stale steps unless --all is provided.

Usage:
    python scripts/build_profile.py
    python scripts/build_profile.py --all
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PYTHON = sys.executable


def mtime(path: Path) -> float:
    return path.stat().st_mtime


def exists(path: Path) -> bool:
    return path.exists()


def needs_run(output: Path, inputs: list[Path]) -> bool:
    if not exists(output):
        return True
    output_mtime = mtime(output)
    return any(not exists(inp) or mtime(inp) > output_mtime for inp in inputs)


def run_step(label: str, args: list[str]) -> None:
    print(f"[{label}] {' '.join(args)}")
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build all Jun Wei profile assets")
    parser.add_argument("--all", action="store_true", help="force every step to rerun")
    args = parser.parse_args()

    steps = [
        {
            "label": "ascii",
            "output": ROOT / "junwei-ascii.svg",
            "inputs": [ROOT / "junwei-photo.jpeg", HERE / "make_ascii_svg.py"],
            "command": [PYTHON, str(HERE / "make_ascii_svg.py")],
        },
        {
            "label": "info-card",
            "output": ROOT / "junwei-info-card.svg",
            "inputs": [HERE / "make_info_card.py"],
            "command": [PYTHON, str(HERE / "make_info_card.py")],
        },
        {
            "label": "contributions",
            "output": ROOT / "data" / "contributions.json",
            "inputs": [HERE / "fetch_contributions.py"],
            "command": [PYTHON, str(HERE / "fetch_contributions.py")],
        },
        {
            "label": "heatmap",
            "output": ROOT / "junwei-heatmap.svg",
            "inputs": [ROOT / "data" / "contributions.json", HERE / "render_heatmap_svg.py"],
            "command": [PYTHON, str(HERE / "render_heatmap_svg.py")],
        },
    ]

    for step in steps:
        if args.all or needs_run(step["output"], step["inputs"]):
            run_step(step["label"], step["command"])
        else:
            print(f"[{step['label']}] up to date")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
