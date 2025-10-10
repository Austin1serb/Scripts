# Migration Guide: v1_photo_cli.py → photo_organizer

This guide explains how to migrate from the monolithic `v1_photo_cli.py` script to the new modular `photo_organizer` package.

## What Changed?

The 966-line monolithic script has been refactored into a clean, maintainable package structure:

### Before (v1_photo_cli.py)
- Single 966-line file
- All functions in one namespace
- Difficult to test individual components
- Hard to extend with new features

### After (photo_organizer package)
- Modular structure with ~15 files
- Clear separation of concerns
- Easy to test and extend
- Better documentation

## File Mapping

| Old Location (v1_photo_cli.py) | New Location | Description |
|--------------------------------|--------------|-------------|
| Lines 61-116 | `config.py` | Constants and configuration |
| Lines 122-143 | `models.py` (DSU class) | Union-Find data structure |
| Lines 166-191 | `models.py` (NameFeat, Item) | Data classes |
| Lines 208-257 | `utils/exif.py` | EXIF extraction |
| Lines 260-342 | `utils/exif.py` | GPS extraction |
| Lines 344-376 | `utils/geo.py` | Geographic utilities |
| Lines 378-398 | `utils/image.py` | Image processing |
| Lines 406-434 | `ingestion.py` | Photo ingestion |
| Lines 437-516 | `utils/filename.py` | Filename parsing and scoring |
| Lines 518-582 | `clustering/fused.py` | Fused clustering |
| Lines 590-677 | `ai_classification/openai_classifier.py` | OpenAI ai_classification |
| Lines 685-730 | `clustering/temporal.py` | Time+hash clustering |
| Lines 146-163 | `clustering/gps.py` | GPS-only clustering |
| Lines 738-797 | `organization.py` | File organization |
| Lines 805-948 | `cli.py` | CLI interface |

## Usage Changes

### Command Line

**Before:**
```bash
python v1_photo_cli.py run --input /path/to/photos --output /path/to/organized
```

**After:**
```bash
# As module
python -m photo_organizer.cli run --input /path/to/photos --output /path/to/organized

# Or as installed command (after pip install -e .)
photo-organizer run --input /path/to/photos --output /path/to/organized
```

### Programmatic Usage

**Before:**
```python
# All in one file
from v1_photo_cli import ingest, cluster, classify_batches, organize

items = ingest(input_dir, work_dir)
groups = cluster(items, time_gap_min, hash_threshold)
labels = classify_batches(items, batch_size, model)
organize(groups, labels, out_dir, brand, rotate_cities)
```

**After:**
```python
# Clean imports from modules
from photo_organizer.ingestion import ingest
from photo_organizer.clustering import cluster_temporal, cluster_gps_only, fused_cluster
from photo_organizer.ai_classification import classify_batches
from photo_organizer.organization import organize
from photo_organizer.utils.filename import name_features

items = ingest(input_dir, work_dir)
name_map = {it.id: name_features(it.path) for it in items}

# Choose clustering strategy
groups = cluster_temporal(items, time_gap_min, hash_threshold)
# OR
groups = fused_cluster(items, name_map, fuse_threshold=0.75)
# OR
groups = cluster_gps_only(items, max_meters=100)

labels = classify_batches(items, batch_size, model)
organize(groups, labels, out_dir, brand, rotate_cities)
```

## Benefits of New Structure

### 1. Testability
Each module can now be tested independently:
```python
from photo_organizer.utils.filename import filename_score
from photo_organizer.models import NameFeat

# Easy to unit test
feat1 = NameFeat(prefix="img", num=100, suffix="", raw="img_100")
feat2 = NameFeat(prefix="img", num=101, suffix="", raw="img_101")
score = filename_score(feat1, feat2)
assert score > 0.7
```

### 2. Extensibility
Easy to add new clustering strategies:
```python
# Create new file: clustering/semantic.py
def cluster_semantic(items, model):
    """Cluster by semantic similarity using embeddings."""
    # Implementation here
    pass
```

### 3. Maintainability
- Each file has a single responsibility
- Clear imports show dependencies
- Easy to navigate and understand
- Better documentation per module

### 4. Reusability
Import only what you need:
```python
# Just need GPS utilities?
from photo_organizer.utils.geo import haversine, nearest_city

# Just need EXIF reading?
from photo_organizer.utils.exif import read_exif_dt, read_exif_gps
```

## Installation

### Development Mode
```bash
cd image_orginization
pip install -e .
```

This installs the package in editable mode, allowing you to modify the code and see changes immediately.

### With Optional Dependencies
```bash
# With OpenAI ai_classification support
pip install -e ".[ai_classification]"

# With development tools
pip install -e ".[dev]"

# With everything
pip install -e ".[ai_classification,dev]"
```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=photo_organizer tests/

# Run specific test file
pytest tests/test_clustering.py
```

## Configuration

Configuration is now centralized in `config.py`. To customize:

```python
# Option 1: Modify config.py directly
from photo_organizer import config
config.IMAGE_DIR = "/new/path/to/photos"

# Option 2: Pass as arguments to CLI
python -m photo_organizer.cli run --input /custom/path ...
```

## Backwards Compatibility

The old `v1_photo_cli.py` script is preserved for reference but should not be used for new work. It will continue to function as before.

## Need Help?

- Check the [README.md](README.md) for detailed usage
- Look at test files in `tests/` for examples
- Read module docstrings for API documentation

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| Lines of code | 966 (1 file) | ~800 (15 files) |
| Testability | Difficult | Easy |
| Documentation | Inline comments | Module docstrings |
| Extensibility | Hard to extend | Easy to add features |
| Maintainability | Low | High |
| Import clarity | N/A (monolithic) | Clear dependencies |
| Reusability | Limited | High |
