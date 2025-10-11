# Photo Organizer

AI-powered construction photo organization pipeline that intelligently clusters, classifies, and organizes photos with SEO-friendly naming.

## Features

- **Smart Ingestion**: Extracts EXIF metadata (datetime, GPS), creates thumbnails, computes perceptual hashes
- **Multi-Strategy Clustering**:
  - GPS-based clustering for photos at the same physical location
  - Fused clustering using filename patterns, perceptual hashes, and timestamps
  - Temporal clustering with time gaps and hash centroids
- **AI Classification**: Optional OpenAI Vision API integration for concrete construction type ai_classification
- **SEO-Optimized Output**: Generates meaningful folder structures and filenames with brand, surface type, city, and unique identifiers

## Project Structure

```
image_orginization/
├── photo_organizer/           # Main package
│   ├── __init__.py
│   ├── config.py             # Configuration and constants
│   ├── models.py             # Data structures (Item, DSU, NameFeat)
│   ├── cli.py                # CLI entry point
│   ├── ingestion.py          # Photo ingestion logic
│   ├── organization.py       # Photo organization and renaming
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── image.py          # Image processing (thumbnails, hashing)
│   │   ├── exif.py           # EXIF data extraction
│   │   ├── geo.py            # GPS and geospatial utilities
│   │   └── filename.py       # Filename parsing and scoring
│   ├── clustering/           # Clustering algorithms
│   │   ├── __init__.py
│   │   ├── gps.py            # GPS-based clustering
│   │   ├── fused.py          # Multi-feature fusion clustering
│   │   └── temporal.py       # Time-based clustering
│   └── ai_classification/       # AI ai_classification
│       ├── __init__.py
│       └── openai_classifier.py  # OpenAI Vision integration
├── requirements.txt
├── README.md
├── v1_photo_cli.py          # Legacy monolithic script (deprecated)
└── venv/                    # Virtual environment
```

## Installation

1. **Create and activate virtual environment**:
```bash
cd image_orginization
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API key** (optional, only if using --classify):
```bash
export OPENAI_API_KEY=sk-...
```

## Usage

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
  --time-gap-min 600 \           # 10 hours max gap for same cluster
  --hash-threshold 8 \            # Max perceptual hash distance
  --site-distance-feet 300 \      # GPS clustering radius
  --rotate-cities \               # Rotate city names if no GPS
  --classify \                    # Enable AI ai_classification
  --batch-size 12 \              # Images per API batch
  --model gpt-4o \               # OpenAI model
  --dry-run                       # Test without copying files
```

## CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | Required | Input folder with images |
| `--output` | `./organized` | Output folder for organized photos |
| `--brand` | `""` | Brand name slug for filenames |
| `--time-gap-min` | `20` | Max minutes between photos in same cluster |
| `--hash-threshold` | `6` | Max pHash distance for same cluster |
| `--site-distance-feet` | `300.0` | GPS clustering radius in feet |
| `--classify` | `False` | Enable OpenAI ai_classification |
| `--model` | `gpt-4o` | OpenAI vision model |
| `--batch-size` | `12` | Images per API batch |
| `--rotate-cities` | `False` | Rotate cities if GPS missing |
| `--dry-run` | `False` | Process without copying files |

## Output Structure

The tool creates the following structure:

```
output/
├── _work/                    # Temporary processing files
│   ├── thumbs/              # Generated thumbnails
│   ├── ingest.json          # Ingestion metadata
│   ├── clusters.json        # Cluster summary
│   ├── fused_explain_no_gps.json   # Clustering explanation
│   └── labels.json          # Classification results
├── 2024-01-15-patio-bellevue/
│   ├── brand-concrete-patio-patio-bellevue-a3b5c7d2.jpg
│   └── brand-concrete-patio-patio-bellevue-f8e1d4c9.jpg
├── 2024-01-16-driveway-tacoma/
│   └── ...
└── manifest.json            # Complete file mapping
```

## Pipeline Steps

1. **Ingestion**: 
   - Walks input directory for supported image formats
   - Creates 768px thumbnails
   - Extracts EXIF datetime and GPS coordinates
   - Computes 16x16 perceptual hashes

2. **Clustering**:
   - Photos with GPS: clustered by physical proximity
   - Photos without GPS: fused clustering using filename patterns, hashes, and timestamps

3. **Classification** (optional):
   - Batch ai_classification using OpenAI Vision API
   - Structured output with confidence scores
   - Labels: concrete-patio, driveway, walkway, retaining-wall, etc.

4. **Organization**:
   - Creates folders: `{date}-{surface}-{city}`
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

- stamped-concrete-patio
- concrete-patio
- concrete-walkway
- concrete-steps
- concrete-driveway
- exposed-aggregate
- retaining-wall
- concrete-slab
- concrete-repair
- decorative-concrete
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
- `ai_classification/`: AI ai_classification logic
- `ingestion.py`: Photo ingestion pipeline
- `organization.py`: Output organization logic
- `cli.py`: Command-line interface

## Migration from v1_photo_cli.py

The original monolithic `v1_photo_cli.py` (966 lines) has been refactored into a modular structure for better maintainability. The legacy script is kept for reference but should not be used for new work.

Key improvements:
- Separated concerns into logical modules
- Better testability with isolated functions
- Easier to extend with new clustering or ai_classification strategies
- Clear dependencies and imports
- Comprehensive documentation

## License

MIT

## Author

Austin Serb - Serbyte Development
