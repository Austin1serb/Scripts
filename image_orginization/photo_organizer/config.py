"""Configuration constants for photo organization."""

from pathlib import Path

# =============================================================================
# PATHS & DIRECTORIES
# =============================================================================
IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"
# IMAGE_DIR = "/Users/austinserb/Desktop/serbyte/Scripts/image_orginization/"
SCRIPT_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CLI DEFAULT PARAMETERS
# =============================================================================
# Paths
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")
DEFAULT_BRAND = ""
# GPS Clustering
DEFAULT_SITE_DISTANCE_FEET = 900.0
# Fused Clustering (non-GPS photos)
DEFAULT_TIME_GAP_MINUTES = 60  # Max time gap (minutes)

#! sweet spot 14-16
DEFAULT_HASH_THRESHOLD = (
    14  # Max perceptual hash distance (0-64) - Try: 6 (strict), 12 (medium), 20 (loose)
)
DEFAULT_FUSE_THRESHOLD = 0.5  # Min similarity score (0.0-1.0)
DEFAULT_MAX_EDGES = 32  # Max connections per photo
# AI Classification
DEFAULT_MODEL = "o4-mini"
DEFAULT_BATCH_SIZE = 12
DEFAULT_CLASSIFY = False
# AI Singleton Assignment
DEFAULT_ASSIGN_SINGLETONS = (
    False  # Try to match singletons to existing clusters using AI
)
MAX_SINGLETONS_TO_ASSIGN = 20  # Max singletons to process (for testing/cost control)
SINGLETON_BATCH_SIZE = 5  # Process N singletons per API call
CLUSTER_SAMPLES_PER_CLUSTER = 2  # Show AI N sample images from each cluster
MAX_CLUSTERS_PER_CALL = 10  # Max clusters to compare against per API call
# Execution
DEFAULT_ROTATE_CITIES = True
DEFAULT_DRY_RUN = True

# =============================================================================
# FUSED CLUSTERING WEIGHTS
# =============================================================================
# Strategy 1: Both photos have datetime (HIGH CONFIDENCE) - weights sum to 1.0
# Filename weight increased since sequential numbers are highly predictive
WEIGHT_TIME_WITH_DATETIME = 0.45  # Time is still primary
WEIGHT_FILENAME_WITH_DATETIME = 0.40  # Increased (sequential filenames very reliable)
WEIGHT_HASH_WITH_DATETIME = 0.15  # Decreased (pHash is support signal only)
# Strategy 2: No datetime but strong filename (MEDIUM CONFIDENCE) - weights sum to 1.0
# Filename is now PRIMARY signal since sequential numbers are highly predictive
WEIGHT_FILENAME_NO_DATETIME = 0.75  # Increased (sequential filenames are very accurate)
WEIGHT_HASH_NO_DATETIME = 0.25  # Decreased (pHash alone is unreliable per testing)
FILENAME_STRONG_THRESHOLD = 0.3  # Minimum filename score to use this strategy
# Strategy 3: Weak filename, use hash only (LOW CONFIDENCE) - weight = 1.0

# =============================================================================
# IMAGE PROCESSING
# =============================================================================
SUPPORTED_EXTS = {
    ".jpg",
    ".JPG",
    ".JPEG",
    ".jpeg",
    ".PNG",
    ".png",
    ".WEBP",
    ".webp",
    ".BMP",
    ".bmp",
    ".TIF",
    ".TIFF",
    ".tif",
    ".tiff",
    ".HEIC",
    ".HEIF",
    ".heic",
    ".heif",
}

# =============================================================================
# LOCATION DATA
# =============================================================================
CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}

# =============================================================================
# CLASSIFICATION LABELS & MAPPING
# <primary-intent>-<specific-surface>-<city?>-<unique>.jpg
# Primary intent:
# - broom-finish-driveway
# - concrete-driveway
# - concrete-patio
# - concrete-repair
# - concrete-resurfacing

# =============================================================================
LABELS = [
    # Core services
    "broom-finish-driveway",
    "concrete-driveway",
    "concrete-patio",
    "concrete-repair",
    "concrete-resurfacing",
    "concrete-steps",
    "concrete-walkway",
    "decorative-concrete",
    "driveway-replacement",
    "exposed-aggregate-driveway",
    "exposed-aggregate-driveway",
    "exposed-aggregate-patio",
    "exposed-aggregate-patio",
    "foundation-slab",
    "resurfacing",
    "retaining-wall",
    "sidewalk",
    "sidewalk",
    "stamped-concrete-driveway",
    "stamped-concrete-driveway",
    "stamped-concrete-patio",
    "stamped-concrete-walkway",
    "stamped-concrete-walkway",
    # Fallback
    "unknown",
]


SURFACE_CANON = {
    "stamped-concrete-patio": ("stamped-concrete-patio", "patio"),
    "stamped-concrete-driveway": ("stamped-concrete-driveway", "driveway"),
    "stamped-concrete-walkway": ("stamped-concrete-walkway", "walkway"),
    "concrete-patio": ("concrete-patio", "patio"),
    "concrete-driveway": ("concrete-driveway", "driveway"),
    "concrete-walkway": ("concrete-walkway", "walkway"),
    "concrete-steps": ("porch-concrete", "steps"),
    "exposed-aggregate-driveway": ("exposed-aggregate-concrete", "driveway"),
    "exposed-aggregate-patio": ("exposed-aggregate-concrete", "patio"),
    "retaining-wall": ("retaining-wall-contractor", "retaining-wall"),
    "concrete-repair": ("concrete-repair", "repair"),
    "concrete-resurfacing": ("concrete-resurfacing", "resurfacing"),
    "decorative-concrete": ("decorative-concrete", "decorative"),
    "sidewalk": ("concrete-sidewalk", "sidewalk"),
    "stamped-concrete-driveway": ("stamped-concrete-driveway", "driveway"),
    "stamped-concrete-walkway": ("stamped-concrete-walkway", "walkway"),
    "exposed-aggregate-driveway": ("exposed-aggregate-concrete", "driveway"),
    "exposed-aggregate-patio": ("exposed-aggregate-concrete", "patio"),
    "driveway-replacement": ("concrete-driveway-replacement", "driveway"),
    "sidewalk": ("concrete-sidewalk", "sidewalk"),
    "foundation-slab": ("foundation-concrete-slab", "slab"),
    "resurfacing": ("concrete-resurfacing", "resurfacing"),
    "broom-finish-driveway": ("broom-finish-concrete-driveway", "driveway"),
    "unknown": ("concrete-company", "project"),
}


MESSAGES = [
    {
        "role": "system",
        "content": "You are an image classifier for concrete construction photos. Output STRICT JSON, UTF-8, no prose.Return only fields: id, label, confidence, descriptor. If uncertain, return label 'unknown' and confidence <= 0.5.",
    },
    {
        "role": "user",
        "content": (
            "Allowed labels (exact strings): "
            + ", ".join([label.replace("-", " ") for label in LABELS])
            + ".\n"
            "Output must be a STRICT JSON array, UTF-8, no prose, no code fences.\n"
            "Return one object per input image with fields: id, label, confidence, descriptor.\n"
            "Rules:\n"
            "- id: the exact filename we sent you for that image.\n"
            '- label: one of the allowed labels, or "unknown" if unsure.\n'
            "- confidence: a float between 0 and 1.\n"
            '- descriptor: max 6 words, concrete-specific detail (e.g., "broom finish", "saw-cut pattern").\n'
            'Abstain when unsure: if your confidence would be below 0.65, set label to "unknown" and confidence <= 0.5.\n'
            "Do not include city, filenames to use, synonyms, or any extra fields beyond id, label, confidence, descriptor.\n"
            "Return only the JSON array."
        ),
    },
]
