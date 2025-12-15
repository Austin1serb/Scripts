"""Configuration constants for photo organization."""

from pathlib import Path

#
# 🎯 MAIN EXECUTION MODES
#
# Choose ONE primary mode (set only ONE to True):

DEFAULT_MODE_NAME_ONLY = False  # SEO-optimized AI naming only (most efficient)
DEFAULT_AI_CLASSIFY = True  # Standard AI classification (balanced)
DEFAULT_ASSIGN_SINGLETONS = True  # Advanced mode with AI matching (experimental)

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
IMAGE_DIR = "/Users/austinserb/Desktop/gallery-downloads"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")

#
# 🏢 INDUSTRY & BRANDING
#
# Industry type - this is the SINGLE SOURCE OF TRUTH for business type
# Change this to adapt the entire script for different industries
INDUSTRY_TYPE = "window-tinting"  # Options: "concrete", "tint", "roofing", "landscaping", "painting", etc.
INDUSTRY_DESCRIPTOR = (
    "automotive window tinting, and car wrap"  # Full description for AI prompts
)

# SEO naming examples (used in AI prompts for filename generation)
# Customize these examples to match your industry
SEO_FILENAME_EXAMPLES = [
    "ceramic-window-tint-full-car-tesla-model-y",
    "windshield-uv-strip-ceramic-tint-toyota-camry",
    "satin-black-color-change-wrap-ford-f150",
    "clear-paint-protection-film-full-front-ppf-honda-accord",
]

# Work classification instructions for AI (industry-specific guidance)
WORK_CLASSIFICATION_GUIDE = (
    "- Identify the job type (window tinting, car wrap, paint protection film, etc.)\n"
    "- Note the film material (ceramic, carbon, dyed, metallic, etc.)\n"
    "- Mention unique features (curves, borders, patterns, logos, inlays, etc.)\n"
    "- Describe the style (modern, decorative, custom, residential, etc.)"
)

DEFAULT_BRAND = "Bespoke Tint & PPF"
DEFAULT_ROTATE_CITIES = True  # Rotate city names if no GPS data

CITIES = {
    "bellevue": (47.6101, -122.2015),
    "seattle": (47.6062, -122.3321),
    "kirkland": (47.6816, -122.2086),
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
    "automotive-window-tint",
    "ceramic-tint",
    "carbon-tint",
    "dyed-tint",
    "full-car-tint",
    "front-window-tint",
    "rear-window-tint",
    "windshield-tint",
    "sunroof-tint",
    "paint-protection-film",
    "full-front-ppf",
    "partial-ppf",
    "vehicle-wrap",
    "color-change-wrap",
    "partial-wrap",
    "chrome-delete",
    "headlight-taillight-tint",
]

# Smart disambiguation: only add a surface noun when primary is generic
GENERIC_PRIMARIES = {
    "automotive-window-tint",
    "paint-protection-film",
    "vehicle-wrap",
    "color-change-wrap",
}

# Allowed surface nouns (single token). Use only if NOT already present in primary.
SURFACE_NOUNS = {
    "windshield",
    "front-windows",
    "rear-windows",
    "sunroof",
    "full-car",
    "partial",
    "coupe",
    "sedan",
    "suv",
    "truck",
    "hatchback",
    "quarter-glass",
    "back-glass",
    "chrome-delete",
    "hood",
    "fenders",
    "bumper",
    "roof",
    "doors",
    "mirrors",
    "handles",
    "headlights",
    "taillights",
}

# Surface mapping for generic primaries (populate at runtime from descriptors if available)
SURFACE_MAP = {
    # e.g. "automotive-window-tint": "front-windows"
}

# Semantic keyword expansions per label (no "near me"; use page-level geo)
SEMANTIC_KEYWORDS = {
    "automotive-window-tint": [
        "auto-window-tinting",
        "privacy-window-tint",
        "heat-rejection-tint",
        "uv-protection-tint",
        "car-window-film",
        "tint-shades-legal",
    ],
    "ceramic-tint": [
        "ceramic-window-film",
        "infrared-rejection-tint",
        "premium-ceramic-tint",
        "ceramic-heat-blocking",
    ],
    "carbon-tint": [
        "carbon-window-film",
        "color-stable-tint",
        "carbon-heat-rejection",
    ],
    "dyed-tint": [
        "dyed-window-film",
        "entry-level-tint",
        "dyed-privacy-film",
    ],
    "full-car-tint": [
        "full-vehicle-tint",
        "all-windows-tinted",
        "complete-car-tint",
    ],
    "front-window-tint": [
        "front-door-tint",
        "driver-passenger-tint",
        "matching-factory-privacy",
    ],
    "rear-window-tint": [
        "rear-privacy-tint",
        "back-glass-tint",
        "rear-cabin-shade",
    ],
    "windshield-tint": [
        "windshield-uv-strip",
        "full-windshield-ceramic",
        "heat-blocking-windshield",
    ],
    "sunroof-tint": [
        "panoramic-roof-tint",
        "moonroof-ceramic-film",
        "sunroof-heat-reduction",
    ],
    "paint-protection-film": [
        "ppf-installation",
        "clear-bra",
        "rock-chip-protection",
        "self-healing-ppf",
    ],
    "full-front-ppf": [
        "bumper-hood-fenders-ppf",
        "full-front-clear-bra",
        "high-impact-ppf",
    ],
    "partial-ppf": [
        "partial-hood-ppf",
        "door-edge-ppf",
        "rocker-panel-ppf",
    ],
    "vehicle-wrap": [
        "vehicle-wrap-installation",
        "fleet-graphics",
        "logo-wrap",
        "commercial-wrap",
    ],
    "color-change-wrap": [
        "color-change-vehicle-wrap",
        "satin-wrap",
        "matte-wrap",
        "gloss-wrap",
    ],
    "partial-wrap": [
        "roof-wrap",
        "hood-wrap",
        "accent-wrap",
    ],
    "chrome-delete": [
        "blackout-trim",
        "window-trim-wrap",
        "emblem-blackout",
        "mirror-cap-wrap",
    ],
    "headlight-taillight-tint": [
        "headlight-tint",
        "taillight-smoke-film",
        "light-tinting",
    ],
}

# Smart disambiguation for generic labels
GENERIC_PRIMARIES = {
    "automotive-window-tint",
    "paint-protection-film",
    "vehicle-wrap",
    "color-change-wrap",
}

SURFACE_NOUNS = {
    "windshield",
    "front-windows",
    "rear-windows",
    "sunroof",
    "full-car",
    "partial",
    "coupe",
    "sedan",
    "suv",
    "truck",
    "hatchback",
    "quarter-glass",
    "back-glass",
    "chrome-delete",
    "hood",
    "fenders",
    "bumper",
    "roof",
    "doors",
    "mirrors",
    "handles",
    "headlights",
    "taillights",
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
            f"You classify {INDUSTRY_DESCRIPTOR} photos for a contractor in the Bellevue, WA area. Your job is to assign ONE label from an "
            "allowed list and a short descriptor to each image for SEO grouping.\n\n"
            "HARD OUTPUT CONTRACT:\n"
            "- Output STRICT JSON only, UTF-8, no prose, no code fences\n"
            "- Return ONLY: id, label, confidence, descriptor\n"
            "- confidence is a float 0.0-1.0 with 2 decimals\n"
            "- descriptor is max 6 words using the Descriptor Vocabulary below\n\n"
            "PRIMARY DECISION: Identify the primary service shown: tint film on glass, paint protection film (PPF), vehicle wrap, chrome delete, or light tint.\n"
            "If multiple services are present, choose the one occupying the largest area and in best focus.\n\n"
            "VISUAL HEURISTICS:\n"
            "- Window tint cues: visible film edge on glass, shade difference vs factory privacy, slip solution, squeegee strokes, liner peel.\n"
            "- Front-window tint: typically driver/passenger glass only; mirrors/door frames visible; other glass lighter.\n"
            "- Full-car tint: all side and rear glass show matching shade; often includes windshield strip.\n"
            "- Windshield tint: banner/visor strip across top or full windshield clarity/blue hue; wipers/dash in frame.\n"
            "- Sunroof tint: panoramic glass panel on roof with film hue; may be open/tilted.\n"
            "- PPF cues: clear film edges around hood/fenders/bumper/mirrors, stretch marks, slip solution, wrapped edges, door-cup kits.\n"
            "- Wrap cues: panel seams covered in new color/finish, inlays, relief cuts, door jamb contrast; color-change vs OEM paint.\n"
            "- Chrome delete: window trim, badges, handles or mirror caps blacked out with vinyl.\n"
            "- Headlight/taillight tint: smoked film over lenses; if only lights are shown, prefer 'headlight-taillight-tint'.\n\n"
            "CLASSIFICATION PRIORITY (apply in order):\n"
            "1) If lights are the focus → 'headlight-taillight-tint'.\n"
            "2) If wrap/color change dominates → choose 'color-change-wrap' or 'vehicle-wrap'; use 'partial-wrap' for single panels/roof/hood.\n"
            "3) If trim/emblems blacked → 'chrome-delete'.\n"
            "4) If clear film on paint → 'full-front-ppf' when bumper+hood+fenders covered; else 'partial-ppf' for smaller kits; else 'paint-protection-film'.\n"
            "5) For glass film: use the most specific tint label visible (windshield, sunroof, front-window, rear-window). If entire cabin glass matches, use 'full-car-tint'. If material is evident, pick 'ceramic-tint' or 'carbon-tint'; otherwise 'automotive-window-tint'.\n\n"
            "CONFIDENCE POLICY:\n"
            "- High 0.85-1.00: strong cues, minimal occlusion, pattern or context unmistakable\n"
            "- Medium 0.65-0.84: probable type, some ambiguity or occlusion\n"
            "- Low <0.65: use label 'unknown' and set confidence ≤0.50\n"
            "- Penalize confidence for: night shots, motion blur, heavy reflections, heavy tint mismatch, partial panels unseen\n\n"
            "STRICT RULES:\n"
            "1) Label MUST be exactly one of ALLOWED LABELS or 'unknown'. If a finish-variant is not present in ALLOWED LABELS, fallback to the closest base element label instead of inventing one.\n"
            "2) Never output city names, locations, brand names, tools, people, vehicles, or suggestions.\n"
            "3) No extra fields. No markdown. JSON array only.\n"
            "4) If text overlays or watermarks conflict with visuals, ignore text and trust the pixels.\n"
            "5) If the frame is mostly equipment or shop interior without clear film on glass/paint, output 'unknown'.\n\n"
            "TIE-BREAKERS WHEN TWO TYPES COMPETE:\n"
            "- Area dominance > Centered subject > Surface coverage > Material cues\n"
            "- If tint vs PPF is unclear, check for film edges on paint vs glass; glass edges imply tint, paint panels imply PPF/wrap.\n"
            "- If front-only tint vs full-car tint is unclear, look for rear glass shade matching front.\n\n"
            "DESCRIPTOR VOCABULARY (use only these words, up to 6 total):\n"
            "['ceramic','carbon','dyed','full-car','front-windows','rear-windows','windshield-strip','windshield',"
            "'sunroof','privacy','heat-rejection','uv-blocking','color-change','chrome-delete','satin','matte','gloss',"
            "'full-front-ppf','partial-ppf','bumper','hood','fenders','rocker-panels','mirrors','door-cups','handles',"
            "'accent','logo-wrap','fleet','headlights','taillights','smoked','visor']\n\n"
            "QUALITY GUARDS:\n"
            "- Verify film edges or shade differences to confirm tint vs bare glass.\n"
            "- For PPF, look for seams at hood/bumper/fender edges and gloss shift.\n"
            "- For wraps, check panel gaps, door jamb color, and finish consistency.\n"
            "- If unsure after checks, choose 'unknown' conservatively.\n"
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
            '  {"id": "exact_filename.jpg", "label": "full-car-tint", "confidence": 0.92, "descriptor": "ceramic full-car privacy heat-rejection"},\n'
            '  {"id": "another.jpg", "label": "full-front-ppf", "confidence": 0.88, "descriptor": "full-front-ppf bumper hood fenders"}\n'
            "]\n\n"
            "FIELD RULES:\n"
            "- id: exact filename\n"
            "- label: one of the allowed labels or 'unknown'\n"
            "- confidence: 0.00-1.00, 2 decimals\n"
            "- descriptor: up to 6 words, only from the Descriptor Vocabulary\n\n"
            "EXAMPLES OF MAPPING:\n"
            "- Visible film on driver/passenger glass only → 'front-window-tint'\n"
            "- All glass including rear matches shade → 'full-car-tint'\n"
            "- Clear film edges on bumper/hood/fenders → 'full-front-ppf'\n"
            "- Roof or hood only wrapped in new color → 'partial-wrap'\n"
            "- Smoked film on headlights or taillights → 'headlight-taillight-tint'\n"
            "- Trim/handles blacked out while paint unchanged → 'chrome-delete'\n\n"
            "STRICT THRESHOLD:\n"
            "- If best guess <0.65 confidence → label 'unknown' and confidence ≤0.50\n\n"
            "Begin. Return ONLY the JSON array."
        ),
    },
]

#
# 🏭 INDUSTRY-SPECIFIC TEMPLATES
#
# Quick-switch templates for different industries
# Copy the relevant template to the top of this file to switch industries

"""
# ============================================================================
# CONCRETE INDUSTRY TEMPLATE
# ============================================================================
INDUSTRY_TYPE = "concrete"
INDUSTRY_DESCRIPTOR = "concrete construction"
DEFAULT_BRAND = "RC Concrete"

SEO_FILENAME_EXAMPLES = [
    "stamped-concrete-driveway",
    "imprinted-concrete-patio",
    "decorative-concrete-steps",
    "custom-concrete-logo-stained-overlay",
    "exposed-aggregate-walkway-modern-design",
    "concrete-driveway-broom-finish-new-pour",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the concrete type (driveway, patio, walkway, steps, etc.)\n"
    "- Note the surface finish (stamped, exposed-aggregate, broom, smooth, etc.)\n"
    "- Mention unique features (curves, borders, patterns, logos, inlays, etc.)\n"
    "- Describe the style (modern, decorative, custom, residential, etc.)"
)

LABELS = [
    "stamped-concrete", "concrete-driveway", "concrete-patio",
    "concrete-walkway", "concrete-sidewalk", "concrete-repair",
    "retaining-wall", "exposed-aggregate-concrete",
    "stamped-concrete-patio", "concrete-driveway-repair",
]

# ============================================================================
# WINDOW TINT INDUSTRY TEMPLATE
# ============================================================================
INDUSTRY_TYPE = "tint"
INDUSTRY_DESCRIPTOR = "window tinting"
DEFAULT_BRAND = "Pro Tint"

SEO_FILENAME_EXAMPLES = [
    "ceramic-automotive-tint-front-windshield",
    "carbon-tint-sedan-full-car",
    "residential-window-film-privacy-frost",
    "commercial-building-heat-rejection-tint",
    "decorative-etched-glass-film-lobby",
    "security-film-storefront-shatter-resistant",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the tint type (automotive, residential, commercial)\n"
    "- Note the film material (ceramic, carbon, dyed, metallic, etc.)\n"
    "- Mention the purpose (privacy, heat-rejection, UV-protection, security, etc.)\n"
    "- Describe the application (windshield, side-windows, full-car, building, etc.)"
)

LABELS = [
    "automotive-window-tint", "residential-window-tint",
    "commercial-window-tint", "ceramic-tint", "carbon-tint",
    "dyed-tint", "windshield-tint", "privacy-tint",
    "heat-rejection-tint", "uv-protection-tint",
    "decorative-window-film", "security-film",
]"""
