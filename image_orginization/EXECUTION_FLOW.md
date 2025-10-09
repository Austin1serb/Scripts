# Photo Organizer - Execution Flow

Complete execution flow showing the 4-step pipeline with optimized clustering algorithms.

---

## Configuration

**All default parameters are centralized in:** `photo_organizer/config.py`
- Clustering thresholds and weights
- Model settings (OpenAI)
- File paths and extensions
- GPS distance parameters

---

## Pipeline Overview

**Entry Point:** `main.py` → `cli.main()` (`photo_organizer/cli.py`)

1. **Ingestion** - Extract metadata from all images
2. **Clustering** - Group related photos (hierarchical strategy)
3. **Classification** - Identify surface types (optional)
4. **Organization** - Rename and organize files

---

## STEP 1: INGESTION
**Extract metadata from all images (EXIF, thumbnails, hashes)**

**Main Function:** `ingest(input_dir, work_dir)` - `photo_organizer/ingestion.py`

### Operations (All Concurrent):

**1. Register HEIF Support**
- `register_heif()` - `utils/image.py`
- Enables HEIC/HEIF format handling

**2. Create Thumbnails** (CPU-bound, multiprocessing)
- `create_thumbnails_batch(files, thumbs_dir, max_px=768)` - `utils/image.py`
- Uses `ProcessPoolExecutor` with CPU count workers
- Creates 768px thumbnails at 50% JPEG quality
- **Returns:** `{source_path: thumbnail_path}` mapping

**3. Extract EXIF Data** (I/O-bound, threading)
- `read_exif_batch(files, max_workers=8)` - `utils/exif.py`
- Uses `ThreadPoolExecutor` with 8 workers
- Calls `read_exif_combined(path)` for each image:
  - Runs `exiftool` subprocess
  - Extracts datetime (SubSecDateTimeOriginal, DateTimeOriginal, CreateDate, ModifyDate)
  - Extracts GPS (Composite:GPSLatitude/Longitude with hemisphere corrections)
- **Returns:** `{path: {'dt': datetime, 'gps': (lat, lon)}}`

**4. Compute Perceptual Hashes** (CPU-bound, multiprocessing)
- `compute_phashes_batch(thumbnails, hash_size=8)` - `utils/image.py`
- Uses `ProcessPoolExecutor` with CPU count workers
- Calls `phash(image, hash_size=8)` - DCT-based perceptual hash
- **Returns:** `{thumbnail_path: ImageHash}`

**5. Build Item Objects**
- Combines all metadata into `Item` dataclass
- `Item(id, path, thumb, dt, gps, h)`

**Output:** List of `Item` objects  
**Saved to:** `_work/ingest.json`

---

## STEP 2: CLUSTERING
**Group related photos using hierarchical strategy (GPS → Datetime → Filename → Hash)**

### A. Extract Filename Features
- `name_features(path)` - `utils/filename.py`
- Parses patterns like IMG_1234, DSC_5678, Photo_567
- Normalizes prefixes (IMG, IMAGE, DSC → 'img')
- **Returns:** `NameFeat(prefix, num, suffix, raw)`

### B. Hierarchical Clustering Strategy

**PRIORITY 1: GPS-Based Clustering** (Most Reliable)
- **Function:** `cluster_gps_only(items, max_meters)` - `clustering/gps.py`
- Groups photos within distance threshold (default: 900 feet)
- Uses haversine formula for accurate Earth-surface distance
- **Rationale:** Same location = same project site

**PRIORITY 2: Fused Clustering** (For non-GPS photos)
- **Function:** `fused_cluster(items, name_map, fuse_threshold)` - `clustering/fused.py`
- **Optimization:** Pre-sorted sliding window (37x faster than old O(n²) approach)
  - Sort photos ONCE by filename number
  - Check only ±64 neighbors in sorted list
  - Sequential files (IMG_55→IMG_56) are adjacent = instant match

**Fused Clustering uses 3 hierarchical strategies:**

1. **Strategy 1: Photos WITH datetime** (HIGH CONFIDENCE)
   - `0.45 * time + 0.40 * filename + 0.15 * hash`
   - Time and filename are primary signals
   - Hash validates visual similarity

2. **Strategy 2: NO datetime, strong filename** (MEDIUM CONFIDENCE)
   - `0.75 * filename + 0.25 * hash`
   - Filename is PRIMARY (sequential numbers highly predictive)
   - Requires filename score > 0.3 to use this strategy

3. **Strategy 3: Weak filename** (LOW CONFIDENCE)
   - Uses `hash` only (visual similarity)
   - Fallback when filename pattern is unclear

**Filename Scoring** (Optimized for sequential files):
```python
Same prefix + gap=1:  0.90  # IMG_55→IMG_56 (almost certain match)
Same prefix + gap≤3:  0.80  # IMG_55→IMG_57 (very likely match)
Same prefix + gap≤10: 0.40  # Close sequence
```

**Output:** Combined GPS + fused groups  
**Saved to:** `_work/clusters.json`, `_work/fused_explain_no_gps.json`  
**Statistics:** Printed at end via `print_clustering_stats()` - `utils/stats.py`

### C. Test Mode: pHash-Only Clustering
- **Flag:** `--phash-only`
- **Function:** `cluster_phash_only(items, hash_threshold)` - `clustering/temporal.py`
- Clusters using ONLY visual similarity (ignores filename and time)
- Useful for testing: pHash alone performs poorly on construction photos
- Sequential filenames + datetime provide much better accuracy

---

## STEP 3: CLASSIFICATION (Optional)
**Identify surface types using OpenAI Vision API**

**Function:** `classify_batches(items, batch_size=12, model='gpt-4o')` - `classification/openai_classifier.py`

**Process:**
1. Split items into batches (default: 12 images)
2. For each batch:
   - Encode thumbnails as base64
   - Call `openai.chat.completions.create()` with vision model
   - System prompt: "Classify construction surfaces..."
   - Structured Outputs (JSON schema):
     ```json
     {
       "label": "asphalt" | "concrete" | "gravel" | ...,
       "confidence": 0.0-1.0,
       "descriptor": "brief description"
     }
     ```
3. Parse response for each image

**Output:** `{item_id: classification_result}` dictionary  
**Saved to:** `_work/labels.json`

---

## STEP 4: ORGANIZATION
**Create organized folders and rename files with SEO-friendly names**

**Function:** `organize(groups, labels, out_dir, brand, rotate_cities)` - `organization.py`

**For each cluster:**

**1. Determine Surface Type**
- Majority vote from all labels in group
- Canonicalize using `SURFACE_CANON` mapping

**2. Determine Location**
- If GPS exists: `nearest_city(gps, city_list)` - `utils/geo.py`
  - Uses `haversine()` to find closest city
- If no GPS: Rotate through cities (if `--rotate-cities`)

**3. Create Folder Name**
- Format: `YYYY-MM-DD-surface-city`
- Example: `2024-01-15-concrete-bellevue`

**4. Process Each Photo**
- Build filename: `brand-primary-surface-city-hash.jpg`
- Components:
  - Brand name (if provided)
  - Primary surface name
  - Surface type
  - City
  - `short_hash(path)` - 12-char MD5 hash for uniqueness
- Slugify all components: `RC Concrete` → `rc-concrete`
- Convert HEIC/HEIF extensions to `.jpg`
- Copy file: `shutil.copy2(src, dst)`

**5. Generate Manifest**
- Maps: `{src, dst, cluster, label, city}`

**Output:** Organized folder structure + `manifest.json`

---

## Key Functions Reference

### Concurrent Operations
| Function | Module | Type | Workers | Speedup |
|----------|--------|------|---------|---------|
| `read_exif_batch()` | `utils/exif.py` | Threading (I/O) | 8 | 6-8x |
| `create_thumbnails_batch()` | `utils/image.py` | Multiprocessing (CPU) | CPU count | 6-8x |
| `compute_phashes_batch()` | `utils/image.py` | Multiprocessing (CPU) | CPU count | 6-8x |

### Image Processing
- `ensure_thumb(src, dst, max_px=768)` - `utils/image.py`
- `phash(image, hash_size=8)` - `utils/image.py`
- `short_hash(path, length=12)` - `utils/image.py`

### EXIF Extraction
- `read_exif_combined(path)` - `utils/exif.py` (datetime + GPS in one call)
- `read_exif_batch(files, max_workers=8)` - `utils/exif.py` (concurrent batch extraction)
- Supports: DateTimeOriginal, CreateDate, human-readable dates (e.g., "April 21, 2021")
- Prioritizes creation date over modification date

### Geolocation
- `haversine(lat1, lon1, lat2, lon2)` - `utils/geo.py`
- `meters_between(gps1, gps2)` - `utils/geo.py`
- `nearest_city(gps, city_list, rotation_idx=0)` - `utils/geo.py`

### Filename Analysis
- `name_features(path)` - `utils/filename.py`
- `filename_score(feat1, feat2)` - `utils/filename.py`

### Clustering
- `cluster_gps_only(items, max_meters)` - `clustering/gps.py`
- `fused_cluster(items, name_map, fuse_threshold)` - `clustering/fused.py`
- `cluster_phash_only(items, hash_threshold)` - `clustering/temporal.py` (test mode)
- `fuse_score(item_a, item_b, name_map)` - `clustering/fused.py` (hierarchical scoring)
- `time_score(dt1, dt2)` - `clustering/temporal.py`
- `phash_score(hash1, hash2)` - `clustering/temporal.py`

### Statistics & Reporting
- `print_clustering_stats(summary, gps_count, non_gps_count)` - `utils/stats.py`
- Displays singleton percentage, strategy breakdown, cluster counts

### Classification
- `classify_batches(items, batch_size, model)` - `classification/openai_classifier.py`

### Organization
- `organize(groups, labels, out_dir, brand, rotate_cities)` - `organization.py`
- `get_thumb_path(filename, work_dir)` - `cli.py` (thumbnail path builder)

---

## Data Flow

```
Input Images
    ↓
[Ingestion] → Item objects (id, path, thumb, dt, gps, h)
    ↓
[Clustering] → Groups: [[Item, ...], [Item, ...], ...]
    ↓
[Classification] → Labels: {item_id: {label, confidence, descriptor}}
    ↓
[Organization] → Organized folders + manifest.json
```

---

---

## Output Files

All saved to `output/_work/`:
- `ingest.json` - All extracted metadata (datetime, GPS, pHash, filenames)
- `clusters.json` - Cluster summary with strategy tags and thumbnail paths
  - Each cluster includes: count, strategy used, files with thumbnail links
- `fused_explain_no_gps.json` - Clustering details for non-GPS photos
- `labels.json` - Classification results (if `--classify` enabled)
- `manifest.json` - Complete file mapping (src → dst)
- `thumbs/` - Generated thumbnails (768px JPEG)

## Performance Optimizations

### Clustering Speed (37x faster)
- **Old:** O(n²) - Re-sort for each photo (90,000 ops for 300 photos)
- **New:** O(n log n) - Pre-sort once, sliding window (2,400 ops for 300 photos)
- Sequential files (IMG_55→IMG_56) are adjacent in sorted list = instant match

### Filename Scoring Priority
- **Sequential numbers** (gap=1) score 0.90 - almost certain match
- **Close sequences** (gap≤3) score 0.80 - very likely match
- Based on user validation: sequential filenames are the strongest signal

### Hierarchical Signal Weighting
- **GPS:** Always first priority (same location = same project)
- **Datetime + Filename:** Best for photos with timestamps (45% time, 40% filename)
- **Filename + Hash:** Best for photos without datetime (75% filename, 25% hash)
- **Hash only:** Fallback (unreliable for construction photos with similar materials)
