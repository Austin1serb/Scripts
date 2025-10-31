# Industry Switch Guide

This guide explains how to quickly adapt the photo organizer for different industries.

## Single Source of Truth

All industry-specific settings are controlled by **four variables** at the top of `config.py`:

```python
INDUSTRY_TYPE = "concrete"              # Short identifier (used in folder names)
INDUSTRY_DESCRIPTOR = "concrete construction"  # Full description (used in AI prompts)

SEO_FILENAME_EXAMPLES = [               # Examples shown to AI for filename generation
    "stamped-concrete-driveway",
    "exposed-aggregate-walkway-modern-design",
    # ...
]

WORK_CLASSIFICATION_GUIDE = (          # Industry-specific guidance for AI
    "- Identify the concrete type (driveway, patio, etc.)\n"
    "- Note the surface finish (stamped, broom, etc.)\n"
    # ...
)
```

## Quick Switch Instructions

### Method 1: Edit Config Directly

1. Open `photo_organizer/config.py`
2. Change `INDUSTRY_TYPE` and `INDUSTRY_DESCRIPTOR` at the top
3. Update `SEO_FILENAME_EXAMPLES` with industry-specific examples
4. Update `WORK_CLASSIFICATION_GUIDE` with industry-specific guidance
5. Update `DEFAULT_BRAND` to match your company
6. Update `LABELS` list with industry-specific keywords
7. (Optional) Update `SEMANTIC_KEYWORDS` for advanced SEO

### Method 2: Use Templates

At the bottom of `config.py`, you'll find ready-to-use templates for common industries:

- **Concrete** (default)
- **Window Tinting**
- **Roofing**
- **Landscaping**
- **Painting**

**To use a template:**
1. Copy the entire template section (INDUSTRY_TYPE, INDUSTRY_DESCRIPTOR, SEO_FILENAME_EXAMPLES, WORK_CLASSIFICATION_GUIDE, DEFAULT_BRAND, LABELS)
2. Replace the corresponding values at the top of `config.py`
3. Save and run

## What Gets Updated Automatically

When you change these variables, the following are automatically updated throughout the codebase:

### Folder Names (uses `INDUSTRY_TYPE`)
- `misc-{INDUSTRY_TYPE}-{city}` (e.g., `misc-concrete-seattle`, `misc-tint-bellevue`)

### AI Prompts (uses `INDUSTRY_DESCRIPTOR`)
- Classification prompts: "You classify {INDUSTRY_DESCRIPTOR} photos..."
- SEO naming: "You optimize {INDUSTRY_DESCRIPTOR} photos for local search..."
- Singleton matching: "You are an expert at matching {INDUSTRY_DESCRIPTOR} photos..."

### SEO Naming Guidance (uses `SEO_FILENAME_EXAMPLES` and `WORK_CLASSIFICATION_GUIDE`)
- AI receives industry-specific examples of good filenames
- AI follows industry-specific classification instructions
- Examples: "stamped-concrete-driveway" vs "ceramic-automotive-tint"

### Output Messages
- Console output includes dynamic industry references

## Examples

### Window Tinting Shop

```python
INDUSTRY_TYPE = "tint"
INDUSTRY_DESCRIPTOR = "window tinting"
DEFAULT_BRAND = "Pro Tint Seattle"

SEO_FILENAME_EXAMPLES = [
    "ceramic-automotive-tint-front-windshield",
    "carbon-tint-sedan-full-car",
    "residential-window-film-privacy-frost",
    "commercial-building-heat-rejection-tint",
]

WORK_CLASSIFICATION_GUIDE = (
    "- Identify the tint type (automotive, residential, commercial)\n"
    "- Note the film material (ceramic, carbon, dyed, metallic, etc.)\n"
    "- Mention the purpose (privacy, heat-rejection, UV-protection, etc.)\n"
    "- Describe the application (windshield, side-windows, full-car, etc.)"
)

LABELS = [
    "automotive-window-tint",
    "residential-window-tint",
    "ceramic-tint",
    "carbon-tint",
    "privacy-tint",
    "heat-rejection-tint",
    "uv-protection-tint",
]
```

**Result:**
- Folders: `misc-tint-seattle/`
- AI: "You classify window tinting photos..."
- Filenames: `ceramic-automotive-tint-front-windshield-seattle-pro-tint.jpg`

### Roofing Company

```python
INDUSTRY_TYPE = "roofing"
INDUSTRY_DESCRIPTOR = "roofing services"
DEFAULT_BRAND = "Elite Roofing"

LABELS = [
    "asphalt-shingle-roof",
    "metal-roofing",
    "tile-roofing",
    "flat-roof",
    "roof-repair",
    "roof-replacement",
    "gutter-installation",
    "skylight-installation",
    "roof-inspection",
    "emergency-roof-repair",
]
```

**Result:**
- Folders: `misc-roofing-tacoma/`
- AI: "You classify roofing services photos..."
- Filenames: `asphalt-shingle-roof-replacement-tacoma-elite-roofing.jpg`

## Testing Your Setup

After switching industries, test with a small batch:

```bash
python main.py \
    --source ~/Desktop/test-images \
    --output ~/Desktop/test-output \
    --brand "Your Company" \
    --name-only \
    --dry-run
```

Review the dry-run output to ensure labels and folder names are correct before processing your full image library.

## Adding a New Industry

If your industry isn't in the templates:

1. Choose a short `INDUSTRY_TYPE` (lowercase, no spaces)
2. Write a clear `INDUSTRY_DESCRIPTOR` (2-3 words)
3. Brainstorm 10-20 relevant `LABELS` (SEO keywords your customers search for)
4. Add your template to the bottom of `config.py` for future use

**Example for Auto Detailing:**

```python
INDUSTRY_TYPE = "detailing"
INDUSTRY_DESCRIPTOR = "auto detailing"
DEFAULT_BRAND = "Shine Auto Detailing"

LABELS = [
    "full-car-detail",
    "interior-detailing",
    "exterior-detailing",
    "paint-correction",
    "ceramic-coating",
    "headlight-restoration",
    "engine-bay-cleaning",
    "leather-conditioning",
    "odor-removal",
    "scratch-removal",
]
```

## Tips for Success

1. **Keep INDUSTRY_TYPE short** - it appears in every misc folder name
2. **Make LABELS customer-focused** - use terms people search for on Google
3. **Test small first** - use `--dry-run` to preview without copying files
4. **Update CITIES** - add your service area cities with GPS coordinates
5. **Brand consistency** - match `DEFAULT_BRAND` to your actual business name

## Need Help?

If you're unsure about labels for your industry, try:
- Google Keyword Planner
- Google "your service + near me" and see autocomplete suggestions
- Check competitors' websites for terminology
- Use ChatGPT: "Give me 15 SEO keywords for [your industry] services"
