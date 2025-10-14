#!/usr/bin/env python3
"""
Standalone entry script for Photo Organizer.

This script can be run directly without needing to use module syntax.

Usage:
    python main.py run --input /path/to/photos --output /path/to/organized

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
--name-only
--output '{(SCRIPT_DIR / 'organized').as_posix()}'
""".strip()

# Override defaults from config.py by uncommenting:


# DEFAULT_ARGS += " --classify"  # Enable AI ai_classification
# DEFAULT_ARGS += " --assign-singletons"  # Enable unified matching for uncertain items
DEFAULT_ARGS += " --brand 'RC Concrete'"  # Set brand name


# DEFAULT_ARGS += " --no-dry-run"          # Actually move files (not just simulate)
# DEFAULT_ARGS += " --no-rotate-cities"    # Don't rotate cities
# DEFAULT_ARGS += " --phash-only"  # TEST: Cluster by pHash only (visual similarity)

# ============================================================================

if __name__ == "__main__":
    # If no CLI args provided, use defaults
    if len(sys.argv) == 1:
        sys.argv.extend(shlex.split(DEFAULT_ARGS))
        print("=" * 60)
        print("Running with default arguments (edit default args in main.py)")
        print("=" * 60)

    main()
    print("Done")
