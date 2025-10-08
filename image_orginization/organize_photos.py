#!/usr/bin/env python3
"""
Standalone entry script for Photo Organizer.

This script can be run directly without needing to use module syntax.

Usage:
    python organize_photos.py run --input /path/to/photos --output /path/to/organized

This is equivalent to:
    python -m photo_organizer.cli run --input /path/to/photos --output /path/to/organized

Configure default arguments below in the DEFAULT_ARGS section when no CLI args are provided.
"""
import sys
import shlex
from pathlib import Path

# Add package to path so we can import it
sys.path.insert(0, str(Path(__file__).parent))

from photo_organizer.config import IMAGE_DIR, SCRIPT_DIR
from photo_organizer.cli import main

# ============================================================================
# DEFAULT ARGUMENTS (used when running without CLI args, e.g., IDE "play" button)
# ============================================================================
# Edit these to set your preferred defaults. Comment out lines you don't want.
# These only apply when running the script with no arguments.

DEFAULT_ARGS = f"""
run
--input '{IMAGE_DIR}'
--output '{(SCRIPT_DIR / 'organized').as_posix()}'
--rotate-cities
--time-gap-min 600
--batch-size 12
--hash-threshold 8
--model gpt-4o
--dry-run
""".strip()

# Uncomment to enable classification by default:
# DEFAULT_ARGS += " --classify"

# Uncomment to set a brand name:
# DEFAULT_ARGS += " --brand 'your-company-name'"

# ============================================================================

if __name__ == "__main__":
    # If no CLI args provided, use defaults
    if len(sys.argv) == 1:
        sys.argv.extend(shlex.split(DEFAULT_ARGS))
        print("=" * 60)
        print("Running with default arguments (edit in organize_photos.py)")
        print("=" * 60)

    main()
