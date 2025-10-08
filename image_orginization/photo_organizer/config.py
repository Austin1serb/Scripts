"""Configuration constants for photo organization."""

from pathlib import Path

# Supported image extensions
SUPPORTED_EXTS = {
    ".jpg",
    ".JPG",
    ".JPEG",
    ".jpeg",
    ".PNG",
    ".WEBP",
    ".BMP",
    ".TIF",
    ".TIFF",
    ".HEIC",
    ".HEIF",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
}

# City GPS coordinates (lat, lon)
CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}

# Available classification labels
LABELS = [
    "stamped-concrete-patio",
    "concrete-patio",
    "concrete-walkway",
    "concrete-steps",
    "concrete-driveway",
    "exposed-aggregate",
    "retaining-wall",
    "concrete-slab",
    "concrete-repair",
    "decorative-concrete",
    "unknown",
]

# Surface type canonicalization: label -> (primary, surface)
SURFACE_CANON = {
    "stamped-concrete-patio": ("stamped-concrete-patio", "patio"),
    "concrete-patio": ("concrete-patio", "patio"),
    "decorative-concrete": ("decorative-concrete", "decorative"),
    "exposed-aggregate": ("exposed-aggregate-concrete", "exposed-aggregate"),
    "concrete-walkway": ("concrete-walkway", "walkway"),
    "concrete-steps": ("porch-concrete", "steps"),
    "concrete-driveway": ("concrete-driveway", "driveway"),
    "retaining-wall": ("retaining-wall-contractor", "retaining-wall"),
    "concrete-slab": ("concrete-contractor-residential", "slab"),
    "concrete-repair": ("concrete-repair", "repair"),
    "unknown": ("concrete-company", "project"),
}

# Default image directory
IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"

# Script directory
SCRIPT_DIR = Path(__file__).resolve().parent.parent
