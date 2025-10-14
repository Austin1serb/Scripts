"""Configuration constants for photo organization."""

from pathlib import Path

#
# 🎯 MAIN EXECUTION MODES
#
# Choose ONE primary mode (set only ONE to True):

DEFAULT_MODE_NAME_ONLY = False  # SEO-optimized AI naming (most efficient)
DEFAULT_AI_CLASSIFY = True  # Standard AI classification (balanced)
DEFAULT_ASSIGN_SINGLETONS = False  # Advanced mode with AI matching (experimental)

# Mode descriptions:
# - NAME_ONLY: Flattens all images, creates collages, AI names each uniquely
# Output: Every image gets unique SEO filename
# Cost: ~$0.06 for 562 images (12 API calls)
# Use: When you want SEO names and trust clustering
#
# - AI_CLASSIFY: Standard classification by cluster
# Output: Images grouped by type with semantic variations
# Cost: ~$1.44 for 562 images (287 API calls)
# Use: Default recommended mode
#
# - ASSIGN_SINGLETONS: Advanced matching of uncertain items
# Output: Merges singletons into confident clusters
# Cost: Higher (classification + matching)
# Use: When you have many singletons to consolidate

#
# 📁 PATHS & DIRECTORIES
#
IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")

#
# 🏢 BRANDING & LOCATION
#
DEFAULT_BRAND = "RC Concrete"
DEFAULT_WORK_TYPE = "residential concrete"
DEFAULT_ROTATE_CITIES = True  # Rotate city names if no GPS data

CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}

#
# 🤖 AI CONFIGURATION
#
DEFAULT_MODEL = "gpt-4.1"
DEFAULT_BATCH_SIZE = 12  # Images per API call (for standard classification)

# Rate limiting
API_RATE_LIMIT_DELAY = 1.0  # Seconds between API calls (0 = no delay)
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # Seconds before retry after rate limit

#
# 📸 CLUSTERING PARAMETERS
#
# GPS clustering
DEFAULT_SITE_DISTANCE_FEET = 900.0  # Radius for same physical location

# Temporal clustering
DEFAULT_TIME_GAP_MINUTES = 180  # Max minutes between photos in same cluster

# Visual similarity (perceptual hash)
DEFAULT_HASH_THRESHOLD = 14  # Max pHash distance (0-64), sweet spot: 14-16

# Fused clustering (combines time + filename + hash)
DEFAULT_FUSE_THRESHOLD = 0.5  # Min similarity score (0.0-1.0)
DEFAULT_MAX_EDGES = 32  # Max connections per photo

# Clustering strategy weights
# Strategy 1: Both photos have datetime (HIGH CONFIDENCE)
WEIGHT_TIME_WITH_DATETIME = 0.45
WEIGHT_FILENAME_WITH_DATETIME = 0.40
WEIGHT_HASH_WITH_DATETIME = 0.15

# Strategy 2: No datetime but strong filename (MEDIUM CONFIDENCE)
WEIGHT_FILENAME_NO_DATETIME = 0.75
WEIGHT_HASH_NO_DATETIME = 0.25
FILENAME_STRONG_THRESHOLD = 0.3

#
# 🎨 SEO & FILENAME GENERATION
#
USE_SEMANTIC_KEYWORDS = True  # Rotate semantic variants for SEO diversity
# ? CLASSIFICATION LABELS & MAPPING
# <primary-keyword/work>-<specific-surface/extra identifiers>.jpg
# Canonical labels for AI classification and SEO keywords
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
        "stamped-concrete-sealer",
        "stamped-concrete-installation",
    ],
    "cement-driveway": [
        "cement-driveway-build",
        "cement-driveway-installation",
        "cement-driveway-resurfacing",
        "cement-driveway-repair",
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
        "concrete-porch-overlay",
        "concrete-porch-railing-base",
    ],
    "retaining-wall-contractor": [
        "retaining-wall-installation",
        "retaining-wall-engineering",
        "concrete-retaining-wall",
        "block-retaining-wall",
        "retaining-wall-design",
        "retaining-wall-drainage",
    ],
    "stamped-concrete-patio": [
        "stamped-patio-ideas",
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
        "concrete-patio-design",
        "concrete-patio-extensions",
        "patio-concrete-finishes",
    ],
    "retaining-wall": [
        "concrete-retaining-wall-replacement",
        "tiered-retaining-walls",
        "retaining-wall-permit",
        "concrete-retaining-wall-foundation",
        "concrete-retaining-wall-capstones",
        "concrete-retaining-wall-repair",
        "concrete-weight-bearing-retaining-wall",
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
        "residential-concrete-resurfacing",
        "residential-concrete-overlay",
        "residential-concrete-leveling",
        "high-end-residential-concrete",
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
        "covered-concrete-patio",
        "concrete-patio-firepit",
        "concrete-patio-sealer",
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
        "high-end-patio-concrete",
        "patio-concrete-overlay",
    ],
}

# Smart disambiguation for generic labels
GENERIC_PRIMARIES = {
    "decorative-concrete",
    "concrete-repair",
    "concrete-resurfacing",
    "concrete-project",
    "unknown",
}

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

SURFACE_MAP = {}  # Populated at runtime from descriptors

#
# 🔧 ADVANCED OPTIONS (Usually don't need to change)
#

# Image processing
THUMBNAIL_SIZE = 512
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

# Execution defaults
DEFAULT_DRY_RUN = False

# Advanced: Unified matching (only used if DEFAULT_ASSIGN_SINGLETONS = True)
ENABLE_UNIFIED_MATCHING = False
MIN_MATCH_CONFIDENCE = 0.65
MAX_SINGLETONS_TO_ASSIGN = 199

CONFIDENT_STRATEGIES = [
    "gps_location",
    "time+filename+hash",
    "filename+hash",
]

UNCERTAIN_STRATEGIES = [
    "hash_only",
]

# Advanced: Collage-based classification (experimental)
ENABLE_COLLAGE_CLASSIFICATION = True
COLLAGE_CLUSTERS_PER_IMAGE = 50
COLLAGE_GRID_COLUMNS = 10
COLLAGE_THUMBNAIL_SIZE = 256

#
# 📝 AI CLASSIFICATION PROMPT (Standard Classification Mode Only)
#
MESSAGES = [
    {
        "role": "system",
        "content": (
            "You classify concrete-construction photos for a contractor. Your job is to assign ONE label from an "
            "allowed list and a short descriptor to each image for SEO grouping.\n\n"
            "HARD OUTPUT CONTRACT:\n"
            "- Output STRICT JSON only, UTF-8, no prose, no code fences\n"
            "- Return ONLY: id, label, confidence, descriptor\n"
            "- confidence is a float 0.0-1.0 with 2 decimals\n"
            "- descriptor is max 6 words using the Descriptor Vocabulary below\n\n"
            "PRIMARY DECISION: Identify the single most PROMINENT concrete element in-frame.\n"
            "If multiple elements exist, choose the one occupying the largest area, centered, and in best focus.\n\n"
            "VISUAL HEURISTICS:\n"
            "- DRIVEWAY cues: garage doors, curb cut, apron, vehicles, street edge, wide slab to garage\n"
            "- PATIO cues: backyard furniture, sliding door, grilling area, house facade adjacent without curb\n"
            "- WALKWAY cues: narrow path to entry, garden borders, stepping pattern, connects spaces\n"
            "- SIDEWALK cues: street, curb and gutter, public frontage, control joints at regular street intervals\n"
            "- STEPS cues: risers and treads, nosing line, handrails, porch transitions\n"
            "- SLAB cues: large flat interior or pad, sawcuts in grids, walls or forms around perimeter\n"
            "- RETAINING WALL cues: soil retention, tiered blocks, drainage weeps, geogrid or backfill visible\n"
            "- REPAIR/RESURFACING cues: crack routing, patch color contrast, grinder, overlay feather edges, leveling pumps\n"
            "- FINISH cues: stamped (imprinted patterns), exposed aggregate (visible pebbles), broom (linear grooves), smooth trowel\n\n"
            "CLASSIFICATION PRIORITY (apply in order):\n"
            "1) If stamped pattern is clearly visible, choose the stamped variant label for that element if present in ALLOWED LABELS\n"
            "2) Else if exposed aggregate clearly visible, choose the exposed-aggregate variant label if present\n"
            "3) Else if broom finish clearly visible, choose the broom-finish variant label if present\n"
            "4) Else choose the standard label for that element from ALLOWED LABELS\n"
            "5) If the photo depicts work-in-progress focused on fixing or replacing, and a repair label exists in ALLOWED LABELS, choose that\n\n"
            "CONFIDENCE POLICY:\n"
            "- High 0.85-1.00: strong cues, minimal occlusion, pattern or context unmistakable\n"
            "- Medium 0.65-0.84: probable type, some ambiguity or occlusion\n"
            "- Low <0.65: use label 'unknown' and set confidence ≤0.50\n"
            "- Penalize confidence for: night shots, motion blur, heavy shadows, water glare, construction clutter, extreme zoom\n\n"
            "STRICT RULES:\n"
            "1) Label MUST be exactly one of ALLOWED LABELS or 'unknown'. If a finish-variant is not present in ALLOWED LABELS, fallback to the closest base element label instead of inventing one.\n"
            "2) Never output city names, locations, brand names, tools, people, vehicles, or suggestions.\n"
            "3) No extra fields. No markdown. JSON array only.\n"
            "4) If text overlays or watermarks conflict with visuals, ignore text and trust the pixels.\n"
            "5) If the frame is mostly equipment, materials, or rebar with no clear element, output 'unknown'.\n\n"
            "TIE-BREAKERS WHEN TWO TYPES COMPETE:\n"
            "- Area dominance > Centered subject > Depth of field > Finish clarity\n"
            "- If driveway vs patio is unclear: garage-door or curb implies driveway\n"
            "- If sidewalk vs walkway is unclear: presence of street curb implies sidewalk\n\n"
            "DESCRIPTOR VOCABULARY (use only these words, up to 6 total):\n"
            "['broom-finish','stamped','exposed-aggregate','smooth','new-pour','replacement','repair','resurfaced',"
            "'sawcuts','control-joints','apron','curb-cut','garage-front','backyard','front-entry','steps','ramp',"
            "'decorative-border','integral-color','release-powder','sealer','stone-pattern','wood-plank','ashlar',"
            "'flagstone','cobblestone','random-stone','washed','seeded','formwork','demo','leveling','overlay']\n\n"
            "QUALITY GUARDS:\n"
            "- Check edges for curb/gutter vs lawn borders\n"
            "- Scan surface for finish texture patterns\n"
            "- Look for adjacent structures: garage, porch, street\n"
            "- Detect repairs by color/texture mismatch and tool marks\n"
            "- If in doubt after checks, choose 'unknown' conservatively\n"
        ),
    },
    {
        "role": "user",
        "content": (
            "TASK: Classify each image using ONLY these allowed labels:\n"
            + ", ".join([label.replace("-", " ") for label in LABELS])
            + "\n\n"
            "OUTPUT FORMAT:\n"
            "[\n"
            '  {"id": "exact_filename.jpg", "label": "concrete-driveway", "confidence": 0.92, "descriptor": "broom-finish garage-front sawcuts"},\n'
            '  {"id": "another.jpg", "label": "stamped-concrete-patio", "confidence": 0.88, "descriptor": "stamped stone-pattern backyard sealer"}\n'
            "]\n\n"
            "FIELD RULES:\n"
            "- id: exact filename\n"
            "- label: one of the allowed labels or 'unknown'\n"
            "- confidence: 0.00-1.00, 2 decimals\n"
            "- descriptor: up to 6 words, only from the Descriptor Vocabulary\n\n"
            "EXAMPLES OF MAPPING:\n"
            "- Visible imprinted stone pattern on a backyard slab → 'stamped-concrete-patio'\n"
            "- Large slab leading to garage with curb cut → 'concrete-driveway'\n"
            "- Narrow path to front door with garden edging → 'concrete-walkway'\n"
            "- Street-adjacent pedestrian path with curb/gutter → 'concrete-sidewalk'\n"
            "- Multistep porch transition with risers → 'concrete-steps'\n"
            "- Color-mismatched patches and routed cracks → 'concrete-repair'\n"
            "- Pebble-rich surface texture throughout → exposed-aggregate variant if present; otherwise base element label\n\n"
            "STRICT THRESHOLD:\n"
            "- If best guess <0.65 confidence → label 'unknown' and confidence ≤0.50\n\n"
            "Begin. Return ONLY the JSON array."
        ),
    },
]
