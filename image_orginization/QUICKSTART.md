# Quick Start Guide

Get up and running with Photo Organizer in 5 minutes.

## 1. Setup Environment

```bash
cd image_orginization

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
# OR manually:
pip install -r requirements.txt
```

## 2. Basic Usage (No AI Classification)

Organize photos by GPS location and timestamps:

```bash
# Simple direct execution
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --brand "your-company-name"

# Or using module syntax
python -m photo_organizer.cli run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --brand "your-company-name"
```

This will:
- ✅ Create thumbnails
- ✅ Extract EXIF metadata (date, GPS)
- ✅ Cluster photos by location and time
- ✅ Organize into dated folders
- ✅ Generate SEO-friendly filenames

## 3. With AI Classification (Recommended)

For automatic concrete construction type detection:

### Option A: Using .env file (Recommended)

```bash
# Install python-dotenv if not already installed
pip install python-dotenv

# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-actual-api-key-here

# Run with ai_classification
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --brand "your-company-name" \
  --classify \
  --batch-size 12 \
  --model gpt-4o
```

### Option B: Using environment variable

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Run with ai_classification
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --brand "your-company-name" \
  --classify \
  --batch-size 12 \
  --model gpt-4o
```

## 4. Dry Run (Test First)

Test without copying files:

```bash
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --dry-run
```

Results will be in `./organized/_work/`:
- `ingest.json` - All extracted metadata
- `clusters.json` - Cluster summary
- `labels.json` - Classification results (if --classify used)

## 5. Advanced Configuration

### GPS-Based Projects
Group photos taken at the same location:

```bash
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --site-distance-feet 300 \  # Within 300 feet = same project
  --classify
```

### Large Time Gaps
For projects spanning multiple days:

```bash
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --time-gap-min 600 \  # 10 hours max gap
  --hash-threshold 8     # More lenient similarity
```

### Multiple Cities
Rotate city names if GPS is missing:

```bash
python main.py run \
  --input "/path/to/your/photos" \
  --output "./organized" \
  --rotate-cities  # Cycle through: puyallup, bellevue, tacoma
```

## 6. Understanding Output

After running, your output directory will look like:

```
organized/
├── _work/                           # Processing metadata
│   ├── thumbs/                      # Generated thumbnails
│   ├── ingest.json                  # Extraction results
│   ├── clusters.json                # Cluster summary
│   └── labels.json                  # Classifications
│
├── 2024-01-15-patio-bellevue/      # Dated project folders
│   ├── brand-concrete-patio-patio-bellevue-a3b5c7d2.jpg
│   └── brand-concrete-patio-patio-bellevue-f8e1d4c9.jpg
│
├── 2024-01-16-driveway-tacoma/
│   └── ...
│
└── manifest.json                    # Complete file mapping
```

## 7. Common Use Cases

### Case 1: Organize Phone Photos
```bash
python main.py run \
  --input "~/Pictures/iPhone" \
  --output "./organized-projects" \
  --brand "my-concrete-co" \
  --classify
```

### Case 2: Historical Archive (No GPS)
```bash
python main.py run \
  --input "./old-photos" \
  --output "./organized" \
  --rotate-cities \
  --time-gap-min 1440  # 24 hours
```

### Case 3: Quick Sort by Location Only
```bash
python main.py run \
  --input "./photos" \
  --output "./by-location" \
  --site-distance-feet 100  # Very tight clustering
```

## 8. Verify Installation

Run tests to ensure everything works:

```bash
make test
# OR
pytest tests/ -v
```

## 9. Get Help

```bash
python main.py --help
```

## 10. Troubleshooting

### OpenAI API Errors
```bash
# Check API key is set (if using environment variable)
echo $OPENAI_API_KEY

# Check .env file exists and has correct format
cat .env

# Reduce batch size if hitting token limits
python main.py run ... --batch-size 6
```

### No GPS Found
```bash
# Use --rotate-cities to assign cities anyway
python main.py run ... --rotate-cities
```

### Photos Not Clustering Well
```bash
# Increase time gap and hash threshold
python main.py run ... --time-gap-min 600 --hash-threshold 10
```

### HEIC Format Issues
```bash
# Install HEIF support
pip install pillow-heif
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if migrating from v1
- Look at `tests/` for code examples
- Customize `photo_organizer/config.py` for your needs

---

**Need more help?** Open an issue or check the documentation in each module.
