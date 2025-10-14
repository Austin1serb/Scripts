# Configuration Guide

## 🎯 Quick Start: Choose Your Mode

Edit `photo_organizer/config.py` and set **ONE** mode to `True`:

```python
DEFAULT_MODE_NAME_ONLY = False   # SEO-optimized AI naming (recommended)
DEFAULT_AI_CLASSIFY = True       # Standard AI classification (default)
DEFAULT_ASSIGN_SINGLETONS = False  # Advanced matching (experimental)
```

### Mode Comparison

| Mode | Best For | Cost | Output |
|------|----------|------|--------|
| **NAME_ONLY** | SEO optimization, unique filenames | ~$0.06 | Every image gets unique AI name |
| **AI_CLASSIFY** | General use, balanced approach | ~$1.44 | Images grouped by type with variants |
| **ASSIGN_SINGLETONS** | Consolidating singletons | Highest | Merges singletons into clusters |

*Cost estimates for 562 images

---

## 📋 Configuration Sections

### 1. Main Execution Modes (Top Priority)

```python
# Choose ONE primary mode
DEFAULT_MODE_NAME_ONLY = False
DEFAULT_AI_CLASSIFY = True
DEFAULT_ASSIGN_SINGLETONS = False
```

**When to use each:**
- **NAME_ONLY**: You want unique SEO filenames for every image
- **AI_CLASSIFY**: You want standard classification (default recommended)
- **ASSIGN_SINGLETONS**: You have many singletons to consolidate

### 2. Paths & Directories

```python
IMAGE_DIR = "/path/to/your/photos"
DEFAULT_OUTPUT_DIR = "organized"
```

### 3. Branding & Location

```python
DEFAULT_BRAND = "RC Concrete"
DEFAULT_ROTATE_CITIES = True  # Use different cities if no GPS

CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}
```

Add your cities with GPS coordinates (lat, lon).

### 4. AI Configuration

```python
DEFAULT_MODEL = "gpt-4.1"
DEFAULT_BATCH_SIZE = 12  # Images per API call
API_RATE_LIMIT_DELAY = 1.0  # Seconds between calls
```

### 5. Clustering Parameters

```python
DEFAULT_SITE_DISTANCE_FEET = 900.0  # GPS radius
DEFAULT_TIME_GAP_MINUTES = 180      # Max time between photos
DEFAULT_HASH_THRESHOLD = 14         # Visual similarity (14-16 recommended)
```

### 6. SEO & Keywords

```python
USE_SEMANTIC_KEYWORDS = True  # Rotate keyword variants

LABELS = [
    "concrete-driveway",
    "concrete-patio",
    # ... your target keywords
]
```

---

## 🚀 Common Configurations

### Production (SEO-Optimized)

```python
DEFAULT_MODE_NAME_ONLY = True    # ✅ Enable name-only mode
DEFAULT_AI_CLASSIFY = False
DEFAULT_ASSIGN_SINGLETONS = False

DEFAULT_BRAND = "Your-Company"
DEFAULT_ROTATE_CITIES = True
USE_SEMANTIC_KEYWORDS = False  # Name-only doesn't use semantic rotation
```

**Run:**
```bash
python main.py run --input photos --output organized --brand your-company
```

### Standard Classification

```python
DEFAULT_MODE_NAME_ONLY = False
DEFAULT_AI_CLASSIFY = True     # ✅ Standard mode
DEFAULT_ASSIGN_SINGLETONS = False

USE_SEMANTIC_KEYWORDS = True   # Enable semantic variants
```

**Run:**
```bash
python main.py run --input photos --output organized --classify
```

### Advanced (Singleton Consolidation)

```python
DEFAULT_MODE_NAME_ONLY = False
DEFAULT_AI_CLASSIFY = True
DEFAULT_ASSIGN_SINGLETONS = True  # ✅ Enable matching

ENABLE_UNIFIED_MATCHING = True
MIN_MATCH_CONFIDENCE = 0.65
```

**Run:**
```bash
python main.py run --input photos --output organized --classify --assign-singletons
```

---

## 🔧 Advanced Tuning

### Clustering Accuracy

**Tighter GPS clustering** (smaller radius):
```python
DEFAULT_SITE_DISTANCE_FEET = 500.0  # Stricter location matching
```

**Looser time grouping** (more photos per cluster):
```python
DEFAULT_TIME_GAP_MINUTES = 360  # 6 hours instead of 3
```

**Stricter visual similarity**:
```python
DEFAULT_HASH_THRESHOLD = 12  # Lower = more similar required
```

### API Cost Control

**Slower but safer**:
```python
API_RATE_LIMIT_DELAY = 2.0  # More delay between calls
MAX_RETRIES = 5             # More retry attempts
```

**Smaller batches** (more API calls but more reliable):
```python
DEFAULT_BATCH_SIZE = 6  # Smaller batches
```

### SEO Optimization

**More keyword variants**:
```python
USE_SEMANTIC_KEYWORDS = True

SEMANTIC_KEYWORDS = {
    "concrete-driveway": [
        "new-concrete-driveway",
        "stamped-concrete-driveway",
        "broom-finish-driveway",
        # ... add more variants
    ],
}
```

---

## 📊 What Each Mode Does

### NAME_ONLY Mode

**Process:**
1. Flatten ALL images from ALL clusters
2. Create collages (50 images per collage)
3. AI generates unique SEO filename for each
4. Add location/brand to filename
5. Organize into folders

**Output Example:**
```
name-only-photos/
├── cluster-1-bellevue/
│   ├── custom-concrete-logo-stained-bellevue-rc-concrete.jpg
│   ├── stamped-patio-curves-bellevue-rc-concrete.jpg
│   └── decorative-walkway-modern-bellevue-rc-concrete.jpg
└── misc-concrete-puyallup/
    └── exposed-aggregate-finish-puyallup-rc-concrete.jpg
```

### AI_CLASSIFY Mode

**Process:**
1. Select best example from each cluster
2. AI classifies cluster examples
3. Apply label to all images in cluster
4. Rotate semantic keywords for variety
5. Organize into folders

**Output Example:**
```
organized_photos/
├── stamped-concrete-driveway-bellevue/
│   ├── stamped-concrete-driveway-bellevue-rc-concrete-01.jpg
│   ├── imprinted-concrete-driveway-bellevue-rc-concrete-02.jpg  # variant
│   └── decorative-concrete-driveway-bellevue-rc-concrete-03.jpg  # variant
```

### ASSIGN_SINGLETONS Mode

**Process:**
1. Separate confident vs uncertain clusters
2. Classify confident clusters first
3. Match uncertain items (singletons + hash-only) against confident
4. Merge if confidence > threshold
5. Classify remaining unmatched
6. Organize into folders

**Output Example:**
```
organized_photos/
├── concrete-patio-seattle/
│   ├── concrete-patio-seattle-rc-concrete-01.jpg
│   ├── concrete-patio-seattle-rc-concrete-02.jpg  # was singleton, now merged
│   └── concrete-patio-seattle-rc-concrete-03.jpg
```

---

## 🛠️ CLI Arguments (Override Config)

All config defaults can be overridden via CLI:

```bash
# Mode selection (overrides config)
--name-only              # Force name-only mode
--classify               # Force standard classification
--assign-singletons      # Enable singleton matching

# Clustering
--site-distance-feet 500
--time-gap-min 240
--hash-threshold 16

# AI
--model gpt-4.1
--batch-size 10

# Organization
--brand "your-company"
--rotate-cities          # Enable city rotation
--no-rotate-cities       # Disable city rotation
--semantic-keywords      # Enable keyword variants
--no-semantic-keywords   # Disable keyword variants

# Execution
--dry-run               # Test without copying files
--no-dry-run            # Actually copy files
```

---

## 🎯 Decision Tree

```
What's your priority?
│
├─ SEO & Unique Filenames?
│  └─ Use: DEFAULT_MODE_NAME_ONLY = True
│     Cost: Lowest (~$0.06 for 500 images)
│     Output: Every image gets unique SEO name
│
├─ Balanced Approach?
│  └─ Use: DEFAULT_AI_CLASSIFY = True
│     Cost: Medium (~$1.44 for 500 images)
│     Output: Groups with semantic variants
│
└─ Many Singletons to Consolidate?
   └─ Use: DEFAULT_ASSIGN_SINGLETONS = True
      Cost: Highest (classification + matching)
      Output: Merged clusters, fewer folders
```

---

## 📝 Removed/Deprecated Options

The following were removed from config for simplicity:

- ~~`DEFAULT_WORK_TYPE`~~ - Not used
- ~~`COLLAGE_*` options~~ - Moved to advanced section
- ~~Duplicate `LABELS` entries~~ - Cleaned up
- ~~Unused `SEMANTIC_KEYWORDS`~~ - Trimmed to essentials
- ~~`SURFACE_MAP`~~ - Populated at runtime

All clustering weight options moved to "Advanced" section since they rarely need tuning.

---

## 🔍 Troubleshooting

### "Too many API calls"
→ Set `DEFAULT_MODE_NAME_ONLY = True` (most efficient)

### "Clusters are too small"
→ Increase `DEFAULT_TIME_GAP_MINUTES` and `DEFAULT_SITE_DISTANCE_FEET`

### "Clusters are too large (mixed projects)"
→ Decrease `DEFAULT_SITE_DISTANCE_FEET` to 500-600

### "Poor classification accuracy"
→ Adjust `LABELS` to match your actual project types

### "Not enough keyword variety"
→ Add more variants to `SEMANTIC_KEYWORDS`

### "Duplicate filenames"
→ Name-only mode handles this automatically (adds -02, -03, etc.)

---

## 📚 Further Reading

- **NAME_ONLY_MODE.md** - Complete name-only mode documentation
- **CLASSIFICATION_MODES.md** - Comparison of all three modes
- **README.md** - General usage and examples
