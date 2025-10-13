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
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_BATCH_SIZE = 12  # Images per API call
THUMBNAIL_SIZE = 512  # Thumbnail Size

# ? AI Rate Limiting
API_RATE_LIMIT_DELAY = 1.0  # Seconds to wait between API calls (0 = no delay)
MAX_RETRIES = 3  # Max retries for failed API calls
RETRY_DELAY = 5.0  # Seconds to wait before retrying after rate limit error

# ? AI Unified Matching (Singletons + hash_only Clusters)
DEFAULT_ASSIGN_SINGLETONS = True  # Enable unified matching for uncertain items
MAX_SINGLETONS_TO_ASSIGN = 199  # Max uncertain items to process (cost control)

# Unified matching treats singletons and hash_only clusters identically:
# both are "uncertain" items that need validation against confident clusters
ENABLE_UNIFIED_MATCHING = True  # Use unified matching (simpler than cascading)

CONFIDENT_STRATEGIES = [
    "gps_location",  # GPS-based clusters (high confidence)
    "time+filename+hash",  # Time + filename + visual match
    "filename+hash",  # Filename + visual match (medium-high confidence)
]

UNCERTAIN_STRATEGIES = [
    "hash_only",  # Visual similarity only (needs validation)
]
# Note: Singletons (count == 1) are ALWAYS treated as uncertain, regardless of strategy

# ? Collage-Based Classification (MASSIVE optimization!)
# Show 50+ clusters in a single collage image instead of individual batches
# Reduces API costs by 75-90% and allows comparing against unlimited clusters
ENABLE_COLLAGE_CLASSIFICATION = True  # Use collages for classification
COLLAGE_CLUSTERS_PER_IMAGE = 50  # Max clusters per collage (can go higher!)
COLLAGE_GRID_COLUMNS = 10  # Grid layout (10 columns = 10×5 for 50)
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
    "stamped-concrete",
    "concrete-repair",
    "porch-concrete",
    "stamped-concrete-patio",
    "concrete-driveway",
    "concrete-patio",
    "retaining-wall",
    "stamped-concrete-patios",
    "concrete-driveway-repair",
    "concrete-stamping",
    "exposed-aggregate-concrete",
    "residential-concrete",
    "retaining-wall-repair",
    "concrete-patio",
    "retaining-wall-builders",
    "concrete-driveway-companies",
    "concrete-patio-companies",
    "concrete-walkway",
    "patio-concrete",
    "stamped-concrete-patios",
    "stamped-concrete",
    "concrete-sidewalk",
    "concrete-steps-repair",
    "local-concrete",
    "concrete-slab",
    "exposed-aggregate-driveway",
    "exposed-aggregate-patio",
    "concrete",
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
    "concrete": [
        "concrete-contractor",
        "concrete-installation",
        "concrete-services",
        "licensed-concrete-contractor",
        "concrete-contractor-quotes",
        "concrete-contractor-prices",
        "best-concrete",
    ],
    "stamped-concrete": [
        "stamped-concrete-designs",
        "stamped-concrete-patterns",
        "stamped-concrete-colors",
        "stamped-concrete-cost",
        "stamped-concrete-maintenance",
        "stamped-concrete-sealer",
        "stamped-concrete-installation",
    ],
    "cement-driveway": [
        "cement-driveway-builder",
        "cement-driveway-installation",
        "cement-driveway-resurfacing",
        "cement-driveway-repair",
        "cement-driveway-cost",
        "cement-contractor-driveway",
        "cement-driveway-estimate",
    ],
    "concrete-repair": [
        "concrete-crack-repair",
        "spalling-concrete-repair",
        "concrete-slab-leveling",
        "concrete-resurfacing",
        "concrete-patching",
        "concrete-repair-epoxy",
        "concrete-repair-contractor",
    ],
    "porch-concrete": [
        "concrete-porch-repair",
        "concrete-porch-resurfacing",
        "concrete-porch-steps",
        "concrete-porch-ideas",
        "concrete-porch-cost",
        "concrete-porch-overlay",
        "concrete-porch-railing-base",
    ],
    "retaining-wall-contractor": [
        "retaining-wall-installation",
        "retaining-wall-engineering",
        "concrete-retaining-wall",
        "block-retaining-wall",
        "retaining-wall-cost",
        "retaining-wall-design",
        "retaining-wall-drainage",
    ],
    "stamped-concrete-patio": [
        "stamped-patio-ideas",
        "stamped-patio-cost",
        "stamped-patio-colors",
        "stamped-patio-patterns",
        "stamped-patio-sealer",
        "stamped-patio-installation",
        "stamped-patio-maintenance",
    ],
    "concrete-driveway": [
        "new-concrete-driveway",
        "stamped-concrete-driveway",
        "broom-finish-driveway",
        "exposed-aggregate-driveway",
        "decorative-concrete-driveway",
        "high-end-concrete-driveway",
        "concrete-driveway-control-joints",
        "heated-concrete-driveway",
        "concrete-driveway-curb-cut",
    ],
    "concrete-patio": [
        "patio-concrete-installers",
        "concrete-patio-builders",
        "concrete-patio-resurfacing",
        "concrete-patio-cost",
        "concrete-patio-designs",
        "concrete-patio-extensions",
        "patio-concrete-finishes",
    ],
    "retaining-wall": [
        "concrete-retaining-wall-builders",
        "concrete-retaining-wall-replacement",
        "tiered-retaining-walls",
        "retaining-wall-permit",
        "concrete-retaining-wall-foundation",
        "concrete-retaining-wall-repair-services",
        "concrete-retaining-wall-capstones",
    ],
    "stamped-concrete-patios": [
        "stamped-patio-designs",
        "stamped-patio-textures",
        "stamped-patio-stains",
        "stamped-patio-cleaning",
        "stamped-patio-restoration",
        "stamped-patio-joints",
        "decorative-concrete-patios",
    ],
    "concrete-driveway-repair": [
        "driveway-crack-filling",
        "driveway-lifting-and-leveling",
        "driveway-resurfacing",
        "driveway-pothole-repair",
        "driveway-edge-repair",
        "driveway-joint-sealant",
        "driveway-repair-contractor",
    ],
    "concrete-stamping": [
        "decorative-concrete-stamping",
        "concrete-stamp-mats",
        "ashlar-slate-stamp",
        "random-stone-stamp",
        "wood-plank-stamped-concrete",
        "concrete-release-agent",
        "integral-color-concrete",
    ],
    "exposed-aggregate-concrete": [
        "exposed-aggregate-finish",
        "exposed-aggregate-sealer",
        "exposed-aggregate-maintenance",
        "exposed-aggregate-cost",
        "exposed-aggregate-mix",
        "seeded-aggregate-concrete",
        "washed-aggregate-finish",
    ],
    "residential-concrete": [
        "home-concrete-services",
        "residential-foundation-concrete",
        "residential-driveway-concrete",
        "residential-patio-concrete",
        "residential-concrete-steps",
        "residential-concrete-repair",
        "residential-concrete-estimates",
    ],
    "retaining-wall-repair": [
        "leaning-retaining-wall-repair",
        "retaining-wall-tiebacks",
        "retaining-wall-reinforcement",
        "retaining-wall-waterproofing",
        "retaining-wall-drain-repair",
        "retaining-wall-rebuild",
        "retaining-wall-crack-repair",
    ],
    "concrete-patio": [
        "stamped-concrete-patio",
        "brushed-concrete-patio",
        "concrete-patio-drainage",
        "concrete-patio-cost",
        "covered-concrete-patio",
        "concrete-patio-firepit",
        "concrete-patio-sealer",
    ],
    "retaining-wall-builders": [
        "retaining-wall-construction",
        "landscape-retaining-walls",
        "concrete-block-walls",
        "gravity-retaining-walls",
        "segmental-retaining-walls",
        "retaining-wall-geogrid",
        "retaining-wall-footings",
    ],
    "concrete-driveway-companies": [
        "driveway-paving-companies",
        "driveway-installation-company",
        "driveway-replacement-company",
        "driveway-finishing-company",
        "concrete-driveway-specialists",
        "driveway-construction-company",
        "driveway-concrete-firms",
    ],
    "concrete-patio-companies": [
        "patio-installation-company",
        "patio-resurfacing-company",
        "decorative-concrete-company",
        "patio-extension-company",
        "patio-design-company",
        "outdoor-living-concrete",
        "hardscape-concrete-company",
    ],
    "concrete-walkway": [
        "concrete-pathway",
        "concrete-sidewalk-installers",
        "concrete-walkway-design",
        "concrete-walkway-repair",
        "curb-and-gutter-concrete",
        "concrete-garden-paths",
        "accessible-concrete-walkways",
    ],
    "patio-concrete": [
        "patio-foundation-concrete",
        "patio-concrete-pour",
        "patio-concrete-finishes",
        "patio-concrete-drainage",
        "patio-concrete-steps",
        "patio-concrete-cost",
        "patio-concrete-overlay",
    ],
    "stamped-concrete": [
        "decorative-concrete",
        "pattern-stamped-concrete",
        "colored-concrete",
        "stamped-concrete-installers",
        "stamped-concrete-specialists",
        "stamped-concrete-estimates",
        "stamped-concrete-restoration",
    ],
    "concrete-sidewalk": [
        "sidewalk-concrete-installers",
        "sidewalk-repair-contractor",
        "ada-sidewalk-compliance",
        "city-sidewalk-permit",
        "sidewalk-trip-hazard-repair",
        "curb-ramp-concrete",
        "sidewalk-expansion-joints",
    ],
    "concrete-steps-repair": [
        "crumbling-concrete-steps",
        "concrete-stair-repair",
        "concrete-step-resurfacing",
        "concrete-step-nosing-repair",
        "handrail-base-repair",
        "concrete-steps-patching",
        "concrete-steps-leveling",
    ],
    "local-concrete": [
        "trusted-concrete",
        "top-rated-concrete",
        "affordable-concrete",
        "licensed-and-insured-concrete",
        "concrete-contractor-reviews",
        "concrete-contractor-neighborhoods",
        "community-concrete-services",
    ],
    "concrete-slab": [
        "garage-slab",
        "shed-slab",
        "house-slab-foundation",
        "monolithic-slab-pour",
        "concrete-slab-reinforcement",
        "concrete-slab-leveling",
        "slab-on-grade-contractor",
    ],
    "exposed-aggregate-driveway": [
        "exposed-aggregate-driveway-cost",
        "exposed-aggregate-driveway-sealer",
        "exposed-aggregate-driveway-ideas",
        "exposed-aggregate-driveway-maintenance",
        "exposed-aggregate-borders",
        "exposed-aggregate-concrete-driveway",
        "decorative-aggregate-driveway",
    ],
    "exposed-aggregate-patio": [
        "exposed-aggregate-patio-ideas",
        "exposed-aggregate-patio-sealer",
        "exposed-aggregate-patio-cost",
        "exposed-aggregate-patio-maintenance",
        "exposed-aggregate-patio-edges",
        "exposed-aggregate-steps",
        "exposed-aggregate-seeded-patio",
    ],
    "concrete-tacoma": [
        "tacoma-concrete-company",
        "tacoma-concrete-services",
        "tacoma-concrete-driveways",
        "tacoma-concrete-patios",
        "tacoma-concrete-estimates",
        "tacoma-concrete-repair",
        "tacoma-residential-concrete",
    ],
    "stamped-concrete-tacoma": [
        "tacoma-stamped-concrete-patterns",
        "tacoma-stamped-concrete-cost",
        "tacoma-stamped-patio",
        "tacoma-decorative-concrete",
        "tacoma-stamped-concrete-colors",
        "tacoma-stamped-concrete-sealer",
        "tacoma-stamped-concrete-installers",
    ],
    "concrete-driveway-tacoma": [
        "tacoma-concrete-driveway",
        "tacoma-driveway-replacement",
        "tacoma-driveway-estimate",
        "tacoma-driveway-repair",
        "tacoma-driveway-concrete-company",
        "tacoma-driveway",
        "tacoma-driveway-finishes",
    ],
    "concrete-bellevue": [
        "bellevue-concrete-company",
        "bellevue-concrete-services",
        "bellevue-concrete-driveways",
        "bellevue-concrete-patios",
        "bellevue-concrete-estimates",
        "bellevue-concrete-repair",
        "bellevue-residential-concrete",
    ],
    "stamped-concrete-bellevue": [
        "bellevue-stamped-concrete-patterns",
        "bellevue-stamped-concrete-cost",
        "bellevue-stamped-patio",
        "bellevue-decorative-concrete",
        "bellevue-stamped-concrete-colors",
        "bellevue-stamped-concrete-sealer",
        "bellevue-stamped-concrete-installers",
    ],
    "concrete-driveway-bellevue": [
        "bellevue-concrete-driveway",
        "bellevue-driveway-replacement",
        "bellevue-driveway-estimate",
        "bellevue-driveway-repair",
        "bellevue-driveway-concrete-company",
        "bellevue-driveway",
        "bellevue-driveway-finishes",
    ],
    "concrete-driveway-visualizer": [
        "driveway-design-tool",
        "driveway-simulator",
        "driveway-mockup",
        "driveway-before-and-after",
        "concrete-driveway-planner",
        "driveway-style-preview",
        "driveway-render-tool",
    ],
    "concrete-patio-visualizer": [
        "patio-design-tool",
        "patio-simulator",
        "patio-mockup",
        "patio-before-and-after",
        "concrete-patio-planner",
        "patio-style-preview",
        "patio-render-tool",
    ],
    "driveway-visualizer": [
        "driveway-configurator",
        "driveway-3d-preview",
        "driveway-design-app",
        "driveway-material-selector",
        "driveway-layout-tool",
        "driveway-color-visualizer",
        "driveway-pattern-visualizer",
    ],
    "stamped-concrete-visualizer": [
        "stamped-concrete-design-tool",
        "stamped-concrete-simulator",
        "stamped-concrete-pattern-preview",
        "stamped-concrete-color-visualizer",
        "stamped-concrete-render",
        "decorative-concrete-visualizer",
        "stamped-concrete-mockup",
    ],
    "exposed-aggregate-visualizer": [
        "aggregate-finish-visualizer",
        "exposed-aggregate-preview",
        "exposed-aggregate-design-tool",
        "aggregate-color-visualizer",
        "aggregate-texture-visualizer",
        "exposed-aggregate-simulator",
        "aggregate-mockup",
    ],
    "patio-visualizer": [
        "outdoor-patio-visualizer",
        "patio-layout-tool",
        "patio-surface-preview",
        "patio-texture-visualizer",
        "patio-color-visualizer",
        "patio-design-app",
        "patio-render-preview",
    ],
}


# Filename format examples:
# Specific primary (no surface): stamped-concrete-driveway-bellevue-rc-concrete-01.jpg
# Generic primary + surface: decorative-concrete-steps-bellevue-rc-concrete-01.jpg
# Format: {primary-keyword}[-{surface}]-{city}-{brand}-{index}.jpg


MESSAGES = [
    {
        "role": "system",
        "content": (
            "You are an expert concrete construction photo classifier for a professional concrete contractor. "
            "Your role is to accurately identify and categorize concrete construction project photos for SEO optimization and project organization.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "- Output STRICT JSON only, UTF-8 encoding, no prose or explanations\n"
            "- Return ONLY the requested fields: id, label, confidence, descriptor\n"
            "- Focus on the PRIMARY concrete element visible in the photo\n"
            "- Consider the project TYPE and concrete FINISH when classifying\n\n"
            "CONFIDENCE GUIDELINES:\n"
            "- Take into account the lighting, weather conditions, specific concrete finish and context of the photo\n"
            "- High confidence (0.85-1.0): Clear view, unmistakable identification\n"
            "- Medium confidence (0.65-0.84): Likely correct, some ambiguity\n"
            "- Low confidence (<0.65): Uncertain, use 'unknown' label\n\n"
            "IMPORTANT DISTINCTIONS:\n"
            "- DRIVEWAYS: Vehicle access, typically residential or commercial parking areas\n"
            "- PATIOS: Outdoor living spaces, entertainment areas, adjacent to homes\n"
            "- WALKWAYS: Pedestrian paths connecting areas, narrower than driveways, sometimes called pathways/paths\n"
            "- SIDEWALKS: Public or property-edge pedestrian paths, typically along streets\n"
            "- STEPS: Elevation changes, staircases, porch steps\n"
            "- SLABS: Large flat surfaces (garage floors, shed foundations, house slabs)\n\n"
            "FINISH TYPES:\n"
            "- STAMPED: Textured patterns (stone, brick, wood grain impressions)\n"
            "- EXPOSED AGGREGATE: Visible decorative stones/pebbles in surface\n"
            "- BROOM FINISH: Textured with broom strokes for traction (common on driveways)\n"
            "- SMOOTH/TROWELED: Plain finished surface\n\n"
            "CLASSIFICATION PRIORITY:\n"
            "1. If stamped pattern visible → use 'stamped-concrete-[type]'\n"
            "2. If exposed aggregate visible → use 'exposed-aggregate-[type]'\n"
            "3. If broom finish visible → use 'broom-finish-[type]'\n"
            "4. Otherwise → use standard 'concrete-[type]'\n"
            "5. For repairs/resurfacing → look for patches, cracks, overlays\n\n"
            "When uncertain or photo shows multiple elements, choose the MOST PROMINENT or PRIMARY element."
        ),
    },
    {
        "role": "user",
        "content": (
            "TASK: Classify each concrete construction photo using ONLY the allowed labels below.\n\n"
            "ALLOWED LABELS (use exact strings, replace spaces with hyphens):\n"
            + ", ".join([label.replace("-", " ") for label in LABELS])
            + "\n\n"
            "OUTPUT FORMAT:\n"
            "Return a JSON array with one object per image:\n"
            "[\n"
            '  {"id": "exact_filename.jpg", "label": "concrete-driveway", "confidence": 0.92, "descriptor": "broom finish residential"},\n'
            '  {"id": "another_file.jpg", "label": "stamped-concrete-patio", "confidence": 0.88, "descriptor": "stone pattern entertainment area"}\n'
            "]\n\n"
            "FIELD REQUIREMENTS:\n"
            "- id: EXACT filename from the image (critical for mapping)\n"
            "- label: ONE of the allowed labels above, or 'unknown' if uncertain\n"
            "- confidence: Float between 0.0 and 1.0 (be honest about uncertainty)\n"
            "- descriptor: MAX 6 words describing concrete-specific details\n"
            "  Examples: 'broom finish driveway', 'decorative stamped stone pattern', 'aggregate exposed patio surface'\n\n"
            "CLASSIFICATION EXAMPLES:\n"
            "- Residential driveway with broom texture → 'broom-finish-driveway' (confidence: 0.90+)\n"
            "- Patio with stone-like stamped pattern → 'stamped-concrete-patio' (confidence: 0.85+)\n"
            "- Walkway with exposed stones/pebbles → 'exposed-aggregate-walkway' (confidence: 0.85+)\n"
            "- Front porch steps → 'concrete-steps' (confidence: 0.90+)\n"
            "- Driveway replacement in progress → 'driveway-replacement' (confidence: 0.80+)\n"
            "- Cracked concrete being repaired → 'concrete-repair' (confidence: 0.80+)\n"
            "- Garage floor slab → 'concrete-slab' (confidence: 0.85+)\n"
            "- Block wall for yard leveling → 'retaining-wall' (confidence: 0.90+)\n\n"
            "STRICT RULES:\n"
            "1. If confidence would be below 0.65 → use label 'unknown' and set confidence ≤ 0.5\n"
            "2. Do NOT include: city names, location info, suggested filenames, synonyms\n"
            "3. Do NOT add extra fields beyond: id, label, confidence, descriptor\n"
            "4. Do NOT include code fences, markdown, or explanatory text\n"
            "5. Return ONLY the raw JSON array\n\n"
            "ANALYZE EACH IMAGE CAREFULLY:\n"
            "- What is the PRIMARY concrete element? (driveway, patio, walkway, etc.)\n"
            "- What FINISH is visible? (stamped, exposed aggregate, broom, smooth)\n"
            "- What is the PROJECT TYPE? (new construction, repair, replacement, decorative)\n"
            "- How CONFIDENT are you in this classification? (be conservative)\n\n"
            "Begin classification now:"
        ),
    },
]
