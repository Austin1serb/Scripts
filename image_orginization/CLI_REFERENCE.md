# CLI Reference

Complete reference for all command-line arguments.

## Basic Usage

```bash
python main.py run --input <path> --output <path> [OPTIONS]
```

---

## Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `run` | Execute full pipeline | `run` |
| `--input PATH` | Input folder with images | `--input photos` |

---

## Mode Selection (Choose ONE)

| Argument | Default | Description |
|----------|---------|-------------|
| `--name-only` | `DEFAULT_MODE_NAME_ONLY` | SEO-optimized AI naming (most efficient) |
| `--classify` | `DEFAULT_AI_CLASSIFY` | Standard AI classification |
| `--assign-singletons` | `DEFAULT_ASSIGN_SINGLETONS` | Advanced singleton matching |
| `--no-assign-singletons` | - | Explicitly disable singleton matching |

**Examples:**
```bash
# Name-only mode (SEO filenames)
python main.py run --input photos --output organized --name-only

# Standard classification
python main.py run --input photos --output organized --classify

# Advanced mode with matching
python main.py run --input photos --output organized --classify --assign-singletons
```

---

## Output & Branding

| Argument | Default | Description |
|----------|---------|-------------|
| `--output PATH` | `DEFAULT_OUTPUT_DIR` | Output folder for organized photos |
| `--brand NAME` | `DEFAULT_BRAND` | Brand name for filenames |

**Examples:**
```bash
--output organized
--brand "rc-concrete"
```

---

## Clustering Parameters

| Argument | Default | Description |
|----------|---------|-------------|
| `--site-distance-feet N` | `900.0` | GPS clustering radius in feet |
| `--time-gap-min N` | `180` | Max minutes between photos in cluster |
| `--hash-threshold N` | `14` | Max perceptual hash distance (0-64) |

**Examples:**
```bash
# Tighter GPS clustering (smaller radius)
--site-distance-feet 500

# Longer time window (more photos per cluster)
--time-gap-min 360

# Stricter visual similarity
--hash-threshold 12
```

---

## AI Configuration

| Argument | Default | Description |
|----------|---------|-------------|
| `--model NAME` | `gpt-4.1` | OpenAI vision model |
| `--batch-size N` | `12` | Images per API batch |

**Examples:**
```bash
--model gpt-4o
--batch-size 10
```

---

## Organization Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--rotate-cities` | `True` | Rotate city names if no GPS |
| `--no-rotate-cities` | - | Use first city for all non-GPS images |
| `--semantic-keywords` | `True` | Rotate semantic keyword variants |
| `--no-semantic-keywords` | - | Use only primary keywords |

**Examples:**
```bash
# Disable city rotation (use first city only)
--no-rotate-cities

# Disable semantic keywords (no variants)
--no-semantic-keywords
```

---

## Execution Control

| Argument | Default | Description |
|----------|---------|-------------|
| `--dry-run` | `False` | Test without copying files |
| `--no-dry-run` | - | Actually copy files (default) |

**Examples:**
```bash
# Test run (no files copied)
--dry-run

# Production run (copy files)
--no-dry-run
```

---

## Experimental/Debug

| Argument | Description |
|----------|-------------|
| `--phash-only` | TEST MODE: Use only perceptual hash for clustering |

---

## Complete Examples

### Minimal (Use Config Defaults)

```bash
python main.py run --input photos --output organized
```

### SEO-Optimized Production

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "your-company" \
  --name-only \
  --model gpt-4o
```

### Standard Classification

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "your-company" \
  --classify \
  --rotate-cities \
  --semantic-keywords \
  --model gpt-4.1
```

### Advanced with Custom Clustering

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "your-company" \
  --classify \
  --assign-singletons \
  --site-distance-feet 600 \
  --time-gap-min 240 \
  --hash-threshold 16 \
  --model gpt-4.1
```

### Dry Run (Test First)

```bash
python main.py run \
  --input photos \
  --output test_output \
  --name-only \
  --dry-run
```

---

## Output Locations by Mode

### Name-Only Mode
```
output_dir/
├── _work/                 # Internal files
└── name-only-photos/      # Final organized photos
    ├── _collages/         # AI naming collages
    └── cluster-*/         # Organized folders
```

### Standard Classification
```
output_dir/
├── _work/                 # Internal files
└── organized_photos/      # Final organized photos
    └── label-city/        # Organized folders
```

---

## Environment Variables

Set `OPENAI_API_KEY` environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
python main.py run --input photos --output organized
```

Or use `.env` file in project root:
```
OPENAI_API_KEY=your-api-key
```

---

## Configuration Priority

1. **CLI arguments** (highest priority)
2. **Config file** (`config.py`)
3. **Built-in defaults** (lowest priority)

Example:
```python
# config.py
DEFAULT_BRAND = "RC Concrete"
DEFAULT_AI_CLASSIFY = True
```

```bash
# CLI overrides config
python main.py run --input photos --brand "other-company" --name-only
```

Result: Uses `"other-company"` and name-only mode (overriding config).

---

## Tips

### Quick Mode Switching

Edit `config.py` once, then just run:
```bash
python main.py run --input photos --output organized
```

### Override Just One Setting

```bash
# Use config defaults except for brand
python main.py run --input photos --brand "custom-brand"
```

### Test New Settings

Always do a dry run first:
```bash
python main.py run --input photos --dry-run --site-distance-feet 500
```

### Check What Will Happen

Dry run shows you:
- How many clusters will be created
- What labels will be assigned
- File organization structure
- NO files are copied

---

## Deprecated/Removed Arguments

The following arguments were removed in the latest version:

- ~~`--work-type`~~ - Not used
- ~~`--enable-collage`~~ - Always enabled
- ~~`--singleton-batch-size`~~ - Auto-optimized

All configuration is now in `config.py` or via the remaining CLI arguments above.
