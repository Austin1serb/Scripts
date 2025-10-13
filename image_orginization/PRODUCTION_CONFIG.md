# Production Configuration Recommendations

## Overview

Your `config.py` has many variables that were useful during development but can be simplified for production use. Here's what to keep, remove, or hard-code.

---

## 🎯 **KEEP AS CLI ARGUMENTS** (User might change)

These should stay as CLI arguments because users will want to change them:

```python
# CLI Arguments to KEEP
--input         # Input photo directory (required)
--output        # Output directory
--brand         # Brand name for filenames
--classify      # Enable AI classification
--model         # AI model to use
--dry-run       # Test mode
```

**Why?** These change per run or per user.

---

## 🔒 **HARD-CODE IN config.py** (Rarely changes)

These can stay in `config.py` but **don't need CLI arguments**:

### **AI Settings (Good Defaults)**
```python
# Already optimized - no need for user to change
DEFAULT_TIME_GAP_MINUTES = 180          # ✅ Keep (tuned for construction)
DEFAULT_HASH_THRESHOLD = 14             # ✅ Keep (tuned for your photos)
DEFAULT_SITE_DISTANCE_FEET = 900.0      # ✅ Keep (good GPS radius)

API_RATE_LIMIT_DELAY = 1.0              # ✅ Keep (prevents rate limits)
MAX_RETRIES = 3                         # ✅ Keep
RETRY_DELAY = 5.0                       # ✅ Keep

THUMBNAIL_SIZE = 512                    # ✅ Keep (cost-optimized)
```

### **Collage Settings (Production-Ready)**
```python
# Your brilliant optimization - defaults are perfect
ENABLE_COLLAGE_CLASSIFICATION = True    # ✅ Keep enabled
COLLAGE_CLUSTERS_PER_IMAGE = 50         # ✅ Keep
COLLAGE_GRID_COLUMNS = 10               # ✅ Keep
COLLAGE_THUMBNAIL_SIZE = 256            # ✅ Keep
```

### **Cascading Classification (Production-Ready)**
```python
ENABLE_CASCADING_CLASSIFICATION = True  # ✅ Keep enabled
DEFAULT_ASSIGN_SINGLETONS = True        # ✅ Keep enabled
MAX_SINGLETONS_TO_ASSIGN = 100          # ✅ Keep (good limit)
```

---

## ❌ **REMOVE FROM CLI** (Use config.py defaults only)

These CLI arguments can be **removed** because users won't need to change them:

### **Remove These CLI Arguments:**

1. **`--time-gap-min`** ❌
   - Current: CLI argument
   - Change to: Hard-coded in config (180 minutes is optimal)
   - Why: This was tuned for construction photos, users shouldn't change it

2. **`--hash-threshold`** ❌
   - Current: CLI argument  
   - Change to: Hard-coded in config (14 is optimal)
   - Why: Requires expertise to tune, default is excellent

3. **`--site-distance-feet`** ❌
   - Current: CLI argument
   - Change to: Hard-coded in config (900 feet is good)
   - Why: Most users won't know what value to use

4. **`--batch-size`** ❌
   - Current: CLI argument
   - Change to: Hard-coded in config (12 is optimal)
   - Why: With collage mode, this barely matters now

5. **`--rotate-cities` / `--no-rotate-cities`** ❌
   - Current: CLI arguments
   - Change to: Hard-coded `True` in config
   - Why: Always beneficial for SEO

6. **`--semantic-keywords` / `--no-semantic-keywords`** ❌
   - Current: CLI arguments
   - Change to: Hard-coded `True` in config
   - Why: Always beneficial for SEO

7. **`--phash-only`** ❌
   - Current: CLI argument (test mode)
   - Change to: Remove entirely
   - Why: This was only for testing/comparison

---

## 🗑️ **REMOVE ENTIRELY** (No longer needed)

These variables are **unused or obsolete**:

```python
# Remove these from config.py:
DEFAULT_FUSE_THRESHOLD = 0.5            # ❌ Remove (not used anywhere)
DEFAULT_MAX_EDGES = 32                  # ❌ Remove (internal, not configurable)
DEFAULT_BATCH_SIZE = 12                 # ❌ Remove (collage makes this irrelevant)

# Clustering weights - keep but move to constants section
# These were tuned and shouldn't be changed by users
WEIGHT_TIME_WITH_DATETIME = 0.45        # ✅ Keep (but make it clear: DON'T MODIFY)
WEIGHT_FILENAME_WITH_DATETIME = 0.40    # ✅ Keep
WEIGHT_HASH_WITH_DATETIME = 0.15        # ✅ Keep
# ... etc
```

---

## 📝 **SIMPLIFIED config.py Structure**

Here's the recommended production structure:

### **Section 1: USER CONFIGURATION** (things users SHOULD change)
```python
# =============================================================================
# USER CONFIGURATION - Modify these for your setup
# =============================================================================

# Paths
IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"
DEFAULT_OUTPUT_DIR = str(SCRIPT_DIR / "organized")

# Branding
DEFAULT_BRAND = "RC Concrete"

# Cities for GPS fallback
CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}

# AI Model
DEFAULT_MODEL = "gpt-4o"  # or "gpt-4o-mini" for cheaper
```

### **Section 2: ADVANCED SETTINGS** (tuned defaults - rarely change)
```python
# =============================================================================
# ADVANCED SETTINGS - Optimized defaults (modify only if needed)
# =============================================================================

# Clustering Parameters (tuned for construction photos)
DEFAULT_TIME_GAP_MINUTES = 180          # Max minutes between photos in same project
DEFAULT_HASH_THRESHOLD = 14             # Visual similarity threshold (0-64)
DEFAULT_SITE_DISTANCE_FEET = 900.0      # GPS clustering radius (feet)

# AI Classification
ENABLE_COLLAGE_CLASSIFICATION = True    # Use collage mode (75-90% cost savings)
COLLAGE_CLUSTERS_PER_IMAGE = 50         # Clusters per collage
ENABLE_CASCADING_CLASSIFICATION = True  # Label-guided singleton matching
MAX_SINGLETONS_TO_ASSIGN = 100          # Max singletons to process

# SEO Optimization
USE_SEMANTIC_KEYWORDS = True            # Rotate keywords for better SEO
DEFAULT_ROTATE_CITIES = True            # Use city names in filenames

# API Rate Limiting
API_RATE_LIMIT_DELAY = 1.0              # Seconds between API calls
MAX_RETRIES = 3                         # Retry attempts for failed calls
```

### **Section 3: CONSTANTS** (never change these)
```python
# =============================================================================
# CONSTANTS - Do not modify (optimized for accuracy)
# =============================================================================

# Clustering weights (tuned from testing)
WEIGHT_TIME_WITH_DATETIME = 0.45
WEIGHT_FILENAME_WITH_DATETIME = 0.40
# ... etc

# Image processing
THUMBNAIL_SIZE = 512                    # Optimized for GPT-4 Vision cost
COLLAGE_THUMBNAIL_SIZE = 256            # Optimized for collage readability
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".heic", ...}

# Classification labels
LABELS = ["concrete-driveway", "concrete-patio", ...]
```

---

## 🚀 **SIMPLIFIED CLI** (Production)

**Before (Complex):**
```bash
python main.py run \
  --input "/photos" \
  --output "/organized" \
  --brand "RC Concrete" \
  --time-gap-min 180 \
  --hash-threshold 14 \
  --site-distance-feet 900 \
  --classify \
  --assign-singletons \
  --model gpt-4o \
  --batch-size 12 \
  --rotate-cities \
  --semantic-keywords \
  --dry-run
```

**After (Simple):**
```bash
# All the tuned settings are now defaults!
python main.py run \
  --input "/photos" \
  --classify \
  --model gpt-4o
```

**Or even simpler (use all defaults):**
```bash
# Edit IMAGE_DIR in config.py once, then just:
python main.py run --classify
```

---

## 🎯 **Recommended Changes**

### **Step 1: Update config.py**

Move tuned settings into a "DON'T MODIFY" section:

```python
# =============================================================================
# OPTIMIZED DEFAULTS - DO NOT MODIFY UNLESS YOU KNOW WHAT YOU'RE DOING
# =============================================================================
# These values were tuned through extensive testing and provide optimal results
# for construction photo organization. Changing them may reduce accuracy.
# =============================================================================

DEFAULT_TIME_GAP_MINUTES = 180  # Accounts for lunch breaks, setup time
DEFAULT_HASH_THRESHOLD = 14     # Sweet spot for construction photo similarity  
DEFAULT_SITE_DISTANCE_FEET = 900.0  # Covers typical residential lot + nearby projects
```

### **Step 2: Simplify CLI arguments**

Remove these from `cli.py`:
```python
# DELETE these argument definitions:
ap.add_argument("--time-gap-min", ...)      # ❌ Remove
ap.add_argument("--hash-threshold", ...)    # ❌ Remove  
ap.add_argument("--site-distance-feet", ...) # ❌ Remove
ap.add_argument("--batch-size", ...)        # ❌ Remove
ap.add_argument("--rotate-cities", ...)     # ❌ Remove (use config default)
ap.add_argument("--semantic-keywords", ...) # ❌ Remove (use config default)
ap.add_argument("--phash-only", ...)        # ❌ Remove (test mode only)
```

**Keep only these essential arguments:**
```python
# KEEP these (users need them):
ap.add_argument("--input", required=True)   # ✅ Keep
ap.add_argument("--output", ...)            # ✅ Keep
ap.add_argument("--brand", ...)             # ✅ Keep
ap.add_argument("--classify", ...)          # ✅ Keep
ap.add_argument("--model", ...)             # ✅ Keep
ap.add_argument("--dry-run", ...)           # ✅ Keep
ap.add_argument("--assign-singletons", ...) # ✅ Keep (advanced users)
```

### **Step 3: Update main.py defaults**

```python
# Simplified main.py
if len(sys.argv) == 1:
    sys.argv.extend(
        shlex.split(
            f"run --input '{IMAGE_DIR}' --classify"
            # That's it! All other settings use optimized defaults
        )
    )
```

---

## 💡 **Benefits of Simplification**

### **For Users:**
✅ Fewer decisions to make  
✅ Less chance of misconfiguration  
✅ Faster setup  
✅ "Just works" out of the box  

### **For You:**
✅ Easier to support  
✅ Fewer "why isn't it working?" questions  
✅ Clearer documentation  
✅ Users can't accidentally break tuned settings  

---

## 📌 **Production Checklist**

- [ ] Move clustering weights to "CONSTANTS" section with warning
- [ ] Remove CLI arguments: `--time-gap-min`, `--hash-threshold`, `--site-distance-feet`, `--batch-size`
- [ ] Remove `--rotate-cities` / `--semantic-keywords` flags (always enabled)
- [ ] Remove `--phash-only` test mode
- [ ] Update `DEFAULT_ASSIGN_SINGLETONS = True` (enable by default)
- [ ] Update `ENABLE_COLLAGE_CLASSIFICATION = True` (enable by default)
- [ ] Simplify main.py defaults
- [ ] Update README with simplified examples
- [ ] Add big "OPTIMIZED DEFAULTS" warning in config.py

---

## 🎓 **For Advanced Users**

If someone really needs to tweak clustering parameters, they can:

1. **Edit config.py directly** (clearly documented)
2. **Set environment variables** (advanced)
3. **Fork and customize** (developers)

But 99% of users should just use the optimized defaults!

---

## **Summary**

**Current:** 15+ CLI arguments (overwhelming)  
**Recommended:** 6 essential CLI arguments (clear & simple)  

**Current:** Users must know optimal values  
**Recommended:** Optimized defaults "just work"  

**Current:** Easy to misconfigure  
**Recommended:** Hard to break, easy to use  

This makes your tool **production-ready** and **user-friendly**! 🚀
