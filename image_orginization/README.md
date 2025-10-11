# Photo Organizer

AI-powered construction photo organization pipeline that intelligently clusters, classifies, and organizes photos into groups based on the project site with SEO-friendly file-names.

it takes your unorganized photos and organizes them into groups based on the project site with SEO-friendly file-names, based the type of job, finish(surface), city, and unique identifiers.

## Features

- **Smart Ingestion**: Extracts EXIF metadata (datetime, GPS), creates thumbnails, computes perceptual hashes
- **Multi-Strategy Clustering**:
  - GPS-based clustering for photos at the same physical location
  - Fused clustering using filename patterns, perceptual hashes, and timestamps
  - Temporal clustering with time gaps and hash centroids
- **AI Classification**: Optional OpenAI Vision API integration for concrete construction type classification
- **SEO-Optimized Output**: Generates meaningful folder structures and filenames with brand, surface type, city, and unique identifiers

### Basic Usage

```bash
# Simple direct execution
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "your-brand-name"

# Or using module syntax
python -m photo_organizer.cli run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "your-brand-name"
```

### With Classification

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "bespoke-concrete" \
  --classify \
  --batch-size 12 \
  --model gpt-4o
```

### Advanced Options

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "bespoke-concrete" \
  --time-gap-min 60 \             # Max minutes between photos in same cluster
  --hash-threshold 14 \           # Max perceptual hash distance (0-64)
  --site-distance-feet 900 \      # GPS clustering radius in feet
  --rotate-cities \               # Rotate city names if no GPS
  --classify \                    # Enable AI classification
  --batch-size 12 \               # Images per API batch
  --model gpt-4o \                # OpenAI model
  --dry-run                       # Test without copying files
```

## CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | Required | Input folder with images |
| `--output` | `./organized` | Output folder for organized photos |
| `--brand` | `""` | Brand name slug for filenames |
| `--time-gap-min` | `60` | Max minutes between photos in same cluster |
| `--hash-threshold` | `14` | Max pHash distance for same cluster (0-64 scale) |
| `--site-distance-feet` | `900.0` | GPS clustering radius in feet |
| `--classify` | `False` | Enable OpenAI classification |
| `--model` | `o4-mini` | OpenAI vision model |
| `--batch-size` | `12` | Images per API batch |
| `--rotate-cities` | `True` | Rotate cities if GPS missing |
| `--dry-run` | `True` | Process without copying files |

## Pipeline Steps

1. **Ingestion**: 
   - Walks input directory for supported image formats
   - Creates 512px thumbnails (optimized for GPT-4 Vision API cost)
   - Extracts EXIF datetime and GPS coordinates
   - Computes 8x8 perceptual hashes (hash_size=8)

2. **Clustering**:
   - Photos with GPS: clustered by physical proximity (default: 900 feet radius)
   - Photos without GPS: fused clustering using filename patterns, hashes, and timestamps
   - Three strategies: datetime+filename+hash, filename+hash, or hash-only

3. **Classification** (optional):
   - Batch classification using OpenAI Vision API
   - Structured output with confidence scores
   - 24 concrete construction type labels (see full list below)
   - Optional singleton assignment to merge single-photo clusters

4. **Organization**:
   - Creates folders: `{date}-{surface}-{city}` or `cluster-{id}-{surface}-{city}`
   - Generates filenames: `{brand}-{primary}-{surface}-{city}-{hash}.{ext}`
   - Copies files to organized structure
   - Creates manifest.json with complete mapping

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- HEIC/HEIF (.heic, .heif)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tif, .tiff)

## Classification Labels

All 24 concrete construction type labels:

- stamped-concrete-patio
- stamped-concrete-driveway
- stamped-concrete-walkway
- concrete-patio
- concrete-driveway
- concrete-walkway
- concrete-steps
- exposed-aggregate-driveway
- exposed-aggregate-patio
- retaining-wall
- concrete-repair
- concrete-resurfacing
- decorative-concrete
- polished-concrete
- broom-finish-concrete
- acid-stained-concrete
- epoxy-floor-coating
- concrete-foundation
- concrete-slab
- colored-concrete
- concrete-overlay
- pool-deck
- basement-floor
- garage-floor
- unknown

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

### Code Structure

- `config.py`: All configuration constants in one place
- `models.py`: Data structures used throughout the pipeline
- `utils/`: Reusable utility functions organized by concern
- `clustering/`: Different clustering strategies as separate modules
- `ai_classification/`: AI classification logic
- `ingestion.py`: Photo ingestion pipeline
- `organization.py`: Output organization logic
- `cli.py`: Command-line interface

## Migration from v1_photo_cli.py

The original monolithic `v1_photo_cli.py` (966 lines) has been refactored into a modular structure for better maintainability. The legacy script is kept for reference but should not be used for new work.

Key improvements:
- Separated concerns into logical modules
- Better testability with isolated functions
- Easier to extend with new clustering or classification strategies
- Clear dependencies and imports
- Comprehensive documentation

## License

MIT

## Author

Austin Serb - Serbyte Development
