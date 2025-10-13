"""Configuration constants for photo organization."""

from pathlib import Path

# =============================================================================
# PATHS & DIRECTORIES
# =============================================================================
IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"
# IMAGE_DIR = "/Users/austinserb/Desktop/serbyte/Scripts/image_orginization/"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")
# =============================================================================
# EXECUTION
# =============================================================================
DEFAULT_BRAND = "RC Concrete"
DEFAULT_ROTATE_CITIES = True
DEFAULT_DRY_RUN = False

# SEO Optimization
USE_SEMANTIC_KEYWORDS = True  # Enable semantic keyword rotation for filenames
# =============================================================================
# CLUSTERING
# =============================================================================
DEFAULT_SITE_DISTANCE_FEET = 900.0  # GPS Clustering (in feet)
DEFAULT_TIME_GAP_MINUTES = 180  # Max time gap photo in same cluster

# sweet spot 14-16
DEFAULT_HASH_THRESHOLD = (
    14  # Max perceptual hash distance (0-64) (used for fused clustering)
)
DEFAULT_FUSE_THRESHOLD = 0.5  # Min similarity score (0.0-1.0)
DEFAULT_MAX_EDGES = 32  # Max connections per photo

# ? AI Classification
DEFAULT_AI_CLASSIFY = False
DEFAULT_MODEL = "o4-mini"
DEFAULT_BATCH_SIZE = 12  # Images per API call
THUMBNAIL_SIZE = 512  # Thumbnail Size

# ? AI Rate Limiting
API_RATE_LIMIT_DELAY = 1.0  # Seconds to wait between API calls (0 = no delay)
MAX_RETRIES = 3  # Max retries for failed API calls
RETRY_DELAY = 5.0  # Seconds to wait before retrying after rate limit error

# ? AI Singleton Assignment
DEFAULT_ASSIGN_SINGLETONS = False  # match singletons to clusters using AI
MAX_SINGLETONS_TO_ASSIGN = 20  # Max singletons to process
SINGLETON_BATCH_SIZE = 5  # Process N singletons per API call
CLUSTER_SAMPLES_PER_CLUSTER = 2  # Show AI N sample images from each cluster
MAX_CLUSTERS_PER_CALL = 10  # Max clusters to compare against per API call

# ? Cascading Classification (NEW)
# Classify high-confidence clusters first, then use their labels to filter
# singleton matching against unlimited clusters (not just first 10)
ENABLE_CASCADING_CLASSIFICATION = True  # Use label-guided singleton assignment
HIGH_CONFIDENCE_STRATEGIES = [
    "gps_location",  # GPS-based clusters (most reliable)
    "time+filename+hash",  # Strong temporal + filename + visual match
]
LOW_CONFIDENCE_STRATEGIES = [
    "filename+hash",  # Filename + visual only (medium confidence)
    "hash_only",  # Visual similarity only (lowest confidence)
]

# ? Collage-Based Classification (NEW - MASSIVE optimization!)
# Show 50+ clusters in a single collage image instead of individual batches
# Bypasses MAX_CLUSTERS_PER_CALL limitation and reduces API costs by 75-90%
ENABLE_COLLAGE_CLASSIFICATION = True  # Use collages for cluster classification
COLLAGE_CLUSTERS_PER_IMAGE = 50  # Max clusters per collage (can go higher!)
COLLAGE_GRID_COLUMNS = 10  # Grid layout (10 columns = 10×5 for 50 clusters)
COLLAGE_THUMBNAIL_SIZE = 256  # Size of each thumbnail in collage (pixels)


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
# ? CLASSIFICATION LABELS & MAPPING
# <primary-keyword>-<specific-surface>-<city?>-<unique>.jpg
# Primary keyword:
# - broom-finish-driveway
# - concrete-driveway
# - concrete-patio
# - concrete-repair
# - concrete-resurfacing

# =============================================================================
# Canonical labels for classification and filename slugs
LABELS = [
    # Driveways
    "concrete-driveway",
    "driveway-replacement",
    "broom-finish-driveway",
    "stamped-concrete-driveway",
    "exposed-aggregate-driveway",
    # Patios
    "concrete-patio",
    "stamped-concrete-patio",
    "exposed-aggregate-patio",
    "fire-pit-surround",
    "seat-wall-bench",
    # Walkways & sidewalks
    "concrete-walkway",
    "stamped-concrete-walkway",
    "exposed-aggregate-walkway",
    "sidewalk",
    # Steps, walls, slabs
    "concrete-steps",
    "retaining-wall",
    "concrete-slab",
    # Repairs & treatments
    "concrete-repair",
    "concrete-resurfacing",
    # Broad style bucket
    "decorative-concrete",
    # Fallback
    "concrete-project",
    "unknown",
]

# Smart disambiguation: only add a surface noun when primary is generic
GENERIC_PRIMARIES = {
    "decorative-concrete",
    "concrete-repair",
    "concrete-resurfacing",
    "concrete-project",
    "unknown",
}

# Allowed surface nouns (single token). Use only if NOT already present in primary.
SURFACE_NOUNS = {
    "driveway",
    "patio",
    "walkway",
    "sidewalk",
    "steps",
    "wall",
    "repair",
    "resurfacing",
    "stamped",
    "exposed",
    "broom",
    "colored",
    "stamping",
    "overlay",
    "decorative",
    "slab",
}

# Surface mapping for generic primaries (populate at runtime from descriptors if available)
SURFACE_MAP = {
    # e.g. "decorative-concrete": "steps"
}

# Semantic keyword expansions per label (no "near me"; use page-level geo)
SEMANTIC_KEYWORDS = {
    # Head terms that map well to /services and internal linking
    "concrete-driveway": [
        "concrete-driveway",
        "concrete-driveway-contractors",
        "driveway-concreters",  # purposefully for SEO ranking
        "cement-driveway-contractors",
        "driveway-concrete-companies",
    ],
    "driveway-replacement": [
        "driveway-replacement",
        "replace-concrete-driveway",
        "old-driveway-removal-and-replacement",
    ],
    "broom-finish-driveway": [
        "broom-finish-driveway",
        "brushed-concrete-driveway",
        "non-slip-concrete-driveway-finish",
    ],
    "stamped-concrete-driveway": [
        "stamped-concrete-driveway",
        "imprinted-concrete-driveway",
        "decorative-driveway-concrete",
    ],
    "exposed-aggregate-driveway": [
        "exposed-aggregate-driveway",
        "aggregate-concrete-driveway",
        "decorative-stone-driveway",
    ],
    "concrete-patio": [
        "concrete-patio",
        "patio-concrete-contractors",
        "concrete-patio-companies",
    ],
    "stamped-concrete-patio": [
        "stamped-concrete-patio",
        "stamped-concrete-patios",
        "concrete-stamping-for-patios",
    ],
    "exposed-aggregate-patio": [
        "exposed-aggregate-patio",
        "aggregate-concrete-patio",
        "decorative-patio-concrete",
    ],
    "fire-pit-surround": [
        "concrete-fire-pit-surround",
        "patio-fire-pit-seating",
        "seat-wall-fire-pit",
    ],
    "seat-wall-bench": [
        "concrete-seat-wall",
        "concrete-bench-seating",
        "patio-seating-wall",
    ],
    "concrete-walkway": [
        "concrete-walkway",
        "concrete-walkway-contractors",
        "concrete-sidewalk-walkway",
    ],
    "stamped-concrete-walkway": [
        "stamped-concrete-walkway",
        "decorative-concrete-walkway",
        "imprinted-walkway-concrete",
    ],
    "exposed-aggregate-walkway": [
        "exposed-aggregate-walkway",
        "aggregate-concrete-path",
        "decorative-stone-walkway",
    ],
    "sidewalk": [
        "concrete-sidewalk",
        "concrete-sidewalk-contractors",
        "sidewalk-concrete-companies",
    ],
    "concrete-steps": [
        "concrete-steps",
        "porch-concrete-steps",
        "front-porch-concrete",
    ],
    "retaining-wall": [
        "retaining-wall-contractor",
        "concrete-retaining-wall",
        "retaining-wall-builders",
        "retaining-wall-repair",
    ],
    "concrete-slab": [
        "concrete-slab",
        "concrete-garage-slab",
        "concrete-house-slab",
        "concrete-basement-slab",
    ],
    "concrete-repair": [
        "concrete-repair",
        "concrete-crack-repair",
        "driveway-concrete-repair",
        "sidewalk-concrete-repair",
    ],
    "concrete-resurfacing": [
        "concrete-resurfacing",
        "concrete-overlay",
        "resurfacing-concrete-patio",
        "resurface-concrete-driveway",
    ],
    "decorative-concrete": [
        "decorative-concrete",
        "stamped-concrete",
        "colored-concrete",
        "concrete-stamping",
    ],
    # Broad catch-all for galleries or mixed shoots
    "concrete-project": [
        "concrete-contractor-residential",
        "concrete-companies",
        "local-concrete-contractors",
        "concrete-installers",
        "concrete-company",
    ],
    "unknown": [],
}

# Filename format examples:
# Specific primary (no surface): stamped-concrete-driveway-bellevue-rc-concrete-01.jpg
# Generic primary + surface: decorative-concrete-steps-bellevue-rc-concrete-01.jpg
# Format: {primary-keyword}[-{surface}]-{city}-{brand}-{index}.jpg


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
