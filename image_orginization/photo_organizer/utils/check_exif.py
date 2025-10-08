#!/usr/bin/env python3

"""
Simple EXIF data reader - prints all EXIF metadata for images in a directory.

Requirements:
  - macOS or Linux recommended.
  - exiftool must be installed and available in PATH.
      - macOS:  brew install exiftool
  - Python 3.9+

Usage:
  python3 cluster_photos.py [directory_path]

Notes:
  - Scans directory recursively for supported image formats
  - Prints all EXIF data in JSON format for each image
  - Supports HEIC, JPG, PNG, DNG and common RAW formats
"""

# =============================================================================
# CONFIGURATION - Edit these values to customize your default settings
# =============================================================================

# Default root directory to scan (can be overridden by command line)
DEFAULT_ROOT_DIR = "/Users/austinserb/Desktop/RC Photos"

# Debug mode - set to True to show all EXIF data, False to show only specific fields
DEBUG_MODE = True

# Maximum number of images to process (0 = no limit)
MAX_IMAGES = 100

# =============================================================================

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

SUPPORTED_EXT = {
    ".jpg",
    ".jpeg",
    ".png",
    ".heic",
    ".HEIC",
    ".heif",
    ".dng",
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".raf",
    ".rw2",
    ".tif",
    ".tiff",
}


def run_exiftool(root: Path, debug: bool = DEBUG_MODE) -> List[Dict[str, Any]]:
    # Recursively extract JSON metadata
    if debug:
        # Get ALL EXIF data for debugging
        # -a : allow duplicate tags (show all)
        # -G0 : show group names (helps identify tag sources)
        # -e : extract embedded data
        # No -n flag in debug mode to see both text and numeric values
        cmd = [
            "exiftool",
            "-api",
            "largefilesupport=1",
            "-j",
            "-a",  # Show duplicate tags
            "-G0",  # Show group names
            "-e",  # Extract embedded data
            "-r",  # Recursive
            str(root),
        ]
    else:
        # Get only specific fields we need
        cmd = [
            "exiftool",
            "-api",
            "largefilesupport=1",
            "-j",
            "-n",
            "-r",
            "-FileName",
            "-Directory",
            "-FilePath",
            "-DateTimeOriginal",
            "-EXIF:CreateDate",
            "-CreateDate",
            "-GPSLatitude",
            "-GPSLongitude",
            str(root),
        ]

    try:
        # Capture stderr separately to avoid mixing with JSON output
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("exiftool error:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(2)
        raw_output = result.stdout
    except Exception as e:
        print(f"Error running exiftool: {e}", file=sys.stderr)
        sys.exit(2)

    # Clean the output to remove invalid control characters and progress messages
    import re

    # Remove control characters that break JSON parsing
    cleaned_output = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", raw_output)

    # Remove exiftool progress messages that can appear in the output
    # These messages start with digits and contain "directories scanned" or "files read"
    cleaned_output = re.sub(r"\n\s*\d+\s+directories scanned\n", "\n", cleaned_output)
    cleaned_output = re.sub(r"\n\s*\d+\s+image files read\n", "\n", cleaned_output)
    cleaned_output = re.sub(r"\n\s*\d+\s+files read\n", "\n", cleaned_output)

    try:
        data = json.loads(cleaned_output)
    except json.JSONDecodeError as e:
        print("Failed to parse exiftool JSON output.", file=sys.stderr)
        print(f"JSON decode error: {e}", file=sys.stderr)
        print(f"Error type: {type(e)}", file=sys.stderr)
        print(f"Error message: {e.msg}", file=sys.stderr)
        print(f"Error position: line {e.lineno}, column {e.colno}", file=sys.stderr)
        print(f"Error character position: {e.pos}", file=sys.stderr)

        # Show the problematic area around the error
        if e.pos is not None and e.pos < len(cleaned_output):
            start = max(0, e.pos - 100)
            end = min(len(cleaned_output), e.pos + 100)
            print(f"\nProblematic area around position {e.pos}:", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            print(repr(cleaned_output[start:end]), file=sys.stderr)
            print("=" * 50, file=sys.stderr)

        print("\nRaw exiftool output (first 2000 chars):", file=sys.stderr)
        print(raw_output[:2000], file=sys.stderr)

        # Check if it's just an empty array or no output
        if not raw_output.strip() or raw_output.strip() == "[]":
            print("No images found in the specified directory.", file=sys.stderr)
            sys.exit(1)

        sys.exit(2)

    # Filter to images we care about and print EXIF data
    filtered = []
    for rec in data:
        p = Path(rec.get("SourceFile") or rec.get("FilePath") or "")
        if p.suffix.lower() in SUPPORTED_EXT:
            # normalize keys
            rec["SourceFile"] = str(p)
            print(f"\n=== EXIF DATA FOR: {p.name} ===")
            # Sort keys alphabetically for easier reading
            sorted_rec = dict(sorted(rec.items()))
            print(json.dumps(sorted_rec, indent=2, default=str))
            print("=" * 50)
            filtered.append(rec)

            # Stop if we've reached the maximum number of images
            if MAX_IMAGES > 0 and len(filtered) >= MAX_IMAGES:
                print(f"\n*** STOPPED: Reached maximum of {MAX_IMAGES} images ***")
                break

    return filtered


def main():
    ap = argparse.ArgumentParser(
        description="Read and print all EXIF data for images in a directory."
    )
    ap.add_argument(
        "root",
        type=str,
        nargs="?",
        default=DEFAULT_ROOT_DIR,
        help="Root folder to scan recursively for images",
    )
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        sys.exit(1)

    # exiftool presence check
    try:
        subprocess.check_output(["exiftool", "-ver"])
    except Exception:
        print(
            "exiftool not found. Install with: brew install exiftool", file=sys.stderr
        )
        sys.exit(1)

    print(f"Scanning directory: {root}")
    print("=" * 60)

    records = run_exiftool(root, debug=DEBUG_MODE)

    if not records:
        print("No supported images found.", file=sys.stderr)
        sys.exit(1)

    print(f"\nFound {len(records)} images total.")
    print("Done.")


if __name__ == "__main__":
    main()
