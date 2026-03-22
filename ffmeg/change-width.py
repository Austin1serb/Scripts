#!/usr/bin/env python3
"""
Pad ALL images in ./image_input so the OUTPUT aspect ratio is 16:9,
adding only transparent background (no crop, no scale).
Outputs go to ./optimized_output with the same filenames.

Requires: ImageMagick installed (`magick` or `convert` in PATH)
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

# ====== SETTINGS ======
ASPECT_W, ASPECT_H = 16, 9
GRAVITY = "center"  # center, west, east, north, south, northeast, etc.
EXTENSIONS = {".png", ".webp", ".jpg", ".jpeg", ".tif", ".tiff"}
# ======================


def magick_cmd() -> list[str]:
    if shutil.which("magick"):
        return ["magick"]
    if shutil.which("convert"):
        return ["convert"]
    raise RuntimeError("ImageMagick not found. Expected `magick` or `convert` in PATH.")


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\n{p.stderr.strip()}")
    return p.stdout.strip()


def get_size(src: Path) -> tuple[int, int]:
    # %w %h = width height
    out = run(magick_cmd() + [str(src), "-format", "%w %h", "info:"])
    w_str, h_str = out.split()
    return int(w_str), int(h_str)


def smallest_16_9_canvas(w: int, h: int) -> tuple[int, int]:
    """
    Smallest (W,H) with W/H = 16/9 and W>=w and H>=h.
    """
    r = ASPECT_W / ASPECT_H

    # Option A: keep width, expand height to match 16:9
    h_from_w = math.ceil(w / r)
    if h_from_w >= h:
        return w, h_from_w

    # Option B: keep height, expand width to match 16:9
    w_from_h = math.ceil(h * r)
    return w_from_h, h


def expand_canvas_to_aspect(src: Path, dst: Path) -> None:
    w, h = get_size(src)
    out_w, out_h = smallest_16_9_canvas(w, h)

    cmd = magick_cmd() + [
        str(src),
        "-background",
        "none",
        "-gravity",
        GRAVITY,
        "-extent",
        f"{out_w}x{out_h}",
        str(dst),
    ]
    run(cmd)


def main() -> None:
    root = Path(__file__).resolve().parent
    in_dir = root / "image_input"
    out_dir = root / "optimized_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        raise FileNotFoundError(f"Missing folder: {in_dir}")

    files = sorted(
        [p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS]
    )
    if not files:
        print(f"No matching files found in: {in_dir}")
        return

    print(f"Found {len(files)} file(s) in {in_dir}")
    for src in files:
        dst = out_dir / src.name
        expand_canvas_to_aspect(src, dst)
        print(f"Wrote: {dst}")

    print("Done.")


if __name__ == "__main__":
    main()
