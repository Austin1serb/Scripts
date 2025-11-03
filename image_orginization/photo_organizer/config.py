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
IMAGE_DIR = "/Users/austinserb/Desktop/rc-organized/driveway-star-bellevue"
SCRIPT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")

#
# 🏢 INDUSTRY & BRANDING
#
# Industry type - this is the SINGLE SOURCE OF TRUTH for business type
# Change this to adapt the entire script for different industries
INDUSTRY_TYPE = "concrete"  # Options: "concrete", "tint", "roofing", "landscaping", "painting", etc.
INDUSTRY_DESCRIPTOR = "concrete construction"  # Full description for AI prompts

# SEO naming examples (used in AI prompts for filename generation)
# Customize these examples to match your industry
SEO_FILENAME_EXAMPLES = [
    "stamped-concrete-driveway",
    "imprinted-concrete-patio",
    "decorative-concrete-steps",
    "custom-concrete-logo-stained-overlay",
    "exposed-aggregate-walkway-modern-design",
    "concrete-driveway-broom-finish-new-pour",
]

# Work classification instructions for AI (industry-specific guidance)
WORK_CLASSIFICATION_GUIDE = (
    "- Identify the concrete type (driveway, patio, walkway, steps, etc.)\n"
    "- Note the surface finish (stamped, exposed-aggregate, broom, smooth, etc.)\n"
    "- Mention unique features (curves, borders, patterns, logos, inlays, etc.)\n"
    "- Describe the style (modern, decorative, custom, residential, etc.)"
)

DEFAULT_BRAND = "RC Concrete"
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
    "concrete-driveway",
    "concrete-patio",
    "concrete-walkway",
    "concrete-sidewalk",
    "concrete-steps",
    "concrete-wall",
    "concrete-slab",
    "concrete-retaining-wall",
    "concrete-stamping",
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
            f"You classify {INDUSTRY_DESCRIPTOR} photos for a contractor. Your job is to assign ONE label from an "
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
]

# ============================================================================
# ROOFING INDUSTRY TEMPLATE
# ============================================================================
INDUSTRY_TYPE = "roofing"
INDUSTRY_DESCRIPTOR = "roofing services"
DEFAULT_BRAND = "Elite Roofing"

SEO_FILENAME_EXAMPLES = [
    "asphalt-shingle-roof-replacement",
    "metal-roofing-standing-seam",
    "tile-roof-repair-spanish-style",
    "flat-roof-tpo-membrane-installation",
    "emergency-storm-damage-repair",
    "skylight-installation-velux-residential",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the roof type (asphalt-shingle, metal, tile, flat, etc.)\n"
    "- Note the work performed (replacement, repair, installation, inspection, etc.)\n"
    "- Mention specific features (standing-seam, spanish-tile, tpo-membrane, etc.)\n"
    "- Describe the context (residential, commercial, emergency, storm-damage, etc.)"
)

LABELS = [
    "asphalt-shingle-roof", "metal-roofing", "tile-roofing",
    "flat-roof", "roof-repair", "roof-replacement",
    "gutter-installation", "skylight-installation",
    "roof-inspection", "emergency-roof-repair",
]

# ============================================================================
# LANDSCAPING INDUSTRY TEMPLATE
# ============================================================================
INDUSTRY_TYPE = "landscaping"
INDUSTRY_DESCRIPTOR = "landscaping services"
DEFAULT_BRAND = "Green Scapes"

SEO_FILENAME_EXAMPLES = [
    "paver-patio-herringbone-pattern",
    "retaining-wall-natural-stone",
    "irrigation-system-drip-line-installation",
    "landscape-design-modern-drought-tolerant",
    "outdoor-lighting-path-accent-lights",
    "sod-installation-fescue-lawn",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the work type (hardscaping, softscaping, maintenance, design, etc.)\n"
    "- Note specific elements (paver-patio, retaining-wall, garden-bed, etc.)\n"
    "- Mention materials (natural-stone, pavers, mulch, sod, etc.)\n"
    "- Describe the style (modern, traditional, drought-tolerant, native-plants, etc.)"
)

LABELS = [
    "lawn-maintenance", "landscape-design", "irrigation-system",
    "hardscaping", "retaining-wall", "paver-patio",
    "outdoor-lighting", "tree-trimming", "mulching",
    "sod-installation", "garden-bed", "landscape-renovation",
]

# ============================================================================
# PAINTING INDUSTRY TEMPLATE
# ============================================================================
INDUSTRY_TYPE = "painting"
INDUSTRY_DESCRIPTOR = "painting services"
DEFAULT_BRAND = "Pro Painters"

SEO_FILENAME_EXAMPLES = [
    "interior-painting-living-room-neutral",
    "exterior-house-painting-two-tone",
    "cabinet-painting-kitchen-white-shaker",
    "deck-staining-semi-transparent-cedar",
    "commercial-painting-office-space",
    "trim-painting-baseboards-doors-white",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the location (interior, exterior, commercial, residential, etc.)\n"
    "- Note what's being painted (walls, cabinets, deck, fence, trim, etc.)\n"
    "- Mention the finish (matte, satin, semi-gloss, stain, etc.)\n"
    "- Describe the space or context (living-room, kitchen, office, house-exterior, etc.)"
)

LABELS = [
    "interior-painting", "exterior-painting", "cabinet-painting",
    "deck-staining", "fence-painting", "pressure-washing",
    "drywall-repair", "texture-painting", "trim-painting",
    "commercial-painting", "residential-painting",
]
"""
