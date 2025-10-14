# Name-Only Mode: SEO-Optimized AI Naming

## Overview

Name-only mode generates unique, SEO-optimized filenames for every image using AI vision, without re-clustering or matching. This is the most efficient mode for getting professional, search-optimized filenames.

## How It Works

### Phase 1: Flatten & Collage (Batch Processing)
1. **Flatten ALL images** from ALL clusters into one list
2. **Create collages** of 50 images each (numbered 0-49, 50-99, etc.)
3. Each collage is sent to AI for batch naming

### Phase 2: AI Naming (SEO Specialist)
1. AI acts as **SEO specialist** for local SERP ranking
2. Analyzes each numbered image in the collage
3. Generates **unique, descriptive filename** for each image
4. Format: `<primary-keyword>-<surface/identifiers>`
5. Examples:
   - `custom-concrete-logo-stained-overlay`
   - `decorative-concrete-celtic-cross-inlay`
   - `stamped-patio-decorative-border-curves`
   - `exposed-aggregate-walkway-modern-design`

### Phase 3: Organization (Add Location/Brand)
1. Maps AI filenames back to original images
2. Adds location and brand: `{ai-name}-{city}-{brand}.jpg`
3. Handles duplicates: `{ai-name}-{city}-{brand}-02.jpg`
4. Groups into folders:
   - **Large clusters (>2 images)**: Each gets own folder
   - **Small clusters (≤2 images)**: ALL go into one `misc-concrete-{city}` folder

## Example Workflow

```
Input: 562 images in 287 clusters

Step 1: Flatten
  → [img1, img2, img3, ..., img562]

Step 2: Create Collages
  → Collage 1: images 0-49
  → Collage 2: images 50-99
  → ...
  → Collage 12: images 550-561

Step 3: AI Naming (12 API calls total)
  Collage 1 → 50 unique filenames
  Collage 2 → 50 unique filenames
  ...
  Collage 12 → 12 unique filenames

Step 4: Map Back to Clusters
  Cluster 1 (10 images): img1-img10 → names 0-9
  Cluster 2 (2 images): img11-img12 → names 10-11 (goes to misc)
  Cluster 3 (15 images): img13-img27 → names 12-26
  ...

Step 5: Organize with Location
  cluster-1-bellevue/
    ├── custom-concrete-logo-stained-bellevue-rc-concrete.jpg
    ├── stamped-patio-decorative-border-bellevue-rc-concrete.jpg
    └── ...
  
  cluster-3-seattle/
    ├── exposed-aggregate-walkway-modern-seattle-rc-concrete.jpg
    └── ...
  
  misc-concrete-bellevue/
    ├── decorative-concrete-celtic-cross-bellevue-rc-concrete.jpg
    ├── concrete-driveway-broom-finish-bellevue-rc-concrete.jpg
    └── ...
```

## Usage

```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --brand "rc-concrete" \
  --name-only \
  --model gpt-4o
```

## Output Structure

```
organized/
├── _work/
│   ├── clusters.json
│   ├── ingest.json
│   └── thumbs/
│
└── name-only-photos/
    ├── _collages/              # AI naming collages
    │   ├── batch_1_of_12.jpg
    │   ├── batch_2_of_12.jpg
    │   └── ...
    │
    ├── cluster-1-bellevue/     # Large cluster folders
    │   ├── custom-concrete-logo-stained-bellevue-rc-concrete.jpg
    │   ├── stamped-patio-decorative-border-bellevue-rc-concrete.jpg
    │   └── ...
    │
    ├── cluster-3-seattle/
    │   └── ...
    │
    └── misc-concrete-bellevue/  # Small clusters grouped
        ├── decorative-concrete-celtic-cross-bellevue-rc-concrete.jpg
        ├── concrete-driveway-broom-finish-bellevue-rc-concrete.jpg
        └── ...
```

## AI Prompt Details

The AI receives this role:

> You are an SEO specialist who optimizes concrete construction photos for local search rankings (SERP). Your job is to create unique, descriptive filenames for each image that will help them rank in Google Images and local search results.

**Target Keywords** (from `config.py`):
- stamped-concrete, concrete-driveway, concrete-patio, retaining-wall, etc.

**Filename Format**:
- `<primary-keyword>-<surface/identifiers>.jpg`
- Use hyphens between words (kebab-case)
- 3-6 words per filename
- No numbers, dates, or location names
- Focus on work type, surface, and unique features

**Classification Focus**:
- Concrete type (driveway, patio, walkway, steps, etc.)
- Surface finish (stamped, exposed-aggregate, broom, smooth, etc.)
- Unique features (curves, borders, patterns, logos, inlays, etc.)
- Style (modern, decorative, custom, residential, etc.)

## Key Features

### ✅ Efficiency
- **~12 API calls** for 562 images (vs 562 individual calls)
- **50 images per collage** = massive cost savings
- **Batch processing** = faster execution

### ✅ SEO Optimization
- **Unique filenames** for every image
- **Keyword-rich** descriptions
- **Natural language** (not generic numbered files)
- **Search-friendly** format

### ✅ Smart Organization
- **Large clusters**: Individual project folders
- **Small clusters**: Grouped into misc folders by city
- **Duplicate handling**: Numbers added only when needed
- **Location/brand**: Automatically appended

### ✅ No Re-clustering
- **Trusts clustering** step (GPS + time + filename + hash)
- **No AI matching** or merging
- **Simple workflow**: Name → Organize → Done

## Cost Comparison

### Example: 562 images, 287 clusters

| Method | API Calls | Cost* |
|--------|-----------|-------|
| Individual naming | 562 | $2.81 |
| Cluster examples | 287 | $1.44 |
| **Name-only (collages)** | **12** | **$0.06** |

*Assumes gpt-4o pricing ($0.005 per image)

## Advantages Over Other Modes

### vs Standard Classification Mode:
- ✅ **Every image gets unique name** (not cluster-wide label)
- ✅ **97% fewer API calls** (12 vs 287)
- ✅ **Better SEO** (descriptive vs generic)

### vs Unified Matching Mode:
- ✅ **Simpler workflow** (no matching logic)
- ✅ **Faster execution** (no re-clustering)
- ✅ **More control** (clustering stays as-is)
- ✅ **Lower cost** (fewer API calls)

## When to Use

**Use name-only mode when:**
- ✅ You trust the clustering results
- ✅ You want unique SEO filenames for every image
- ✅ Cost efficiency is important
- ✅ You don't need AI-based re-clustering
- ✅ You want maximum simplicity

**Use other modes when:**
- ❌ You have many singletons that need matching
- ❌ Clustering produced poor results
- ❌ You need AI to refine clusters
- ❌ Accuracy > cost

## Files Modified/Created

### New Files:
1. **`photo_organizer/ai_classification/seo_namer.py`**
   - SEO specialist AI prompt
   - Batch collage naming
   - Response parsing

2. **`photo_organizer/organization_name_only.py`**
   - Name-only organization logic
   - Location/brand appending
   - Duplicate handling
   - Small cluster grouping

### Modified Files:
1. **`photo_organizer/name_only.py`**
   - Flatten all images
   - Call SEO namer
   - Return labels for organization

2. **`photo_organizer/cli.py`**
   - Integrate name-only mode
   - Route to correct organization function
   - Output to `name-only-photos/` folder

## Configuration

No special configuration needed! Just use the `--name-only` flag.

**Optional tuning in code:**
- `max_images_per_collage`: Default 50 (can increase for fewer API calls)
- `thumb_size`: Default 256px (collage thumbnail size)
- `grid_cols`: Default 10 (collage grid columns)

## Troubleshooting

### Issue: AI returns fewer filenames than expected
**Solution**: Fallback to placeholder names (`concrete-photo-N`)

### Issue: Duplicate filenames in same folder
**Solution**: Automatic numbering at end (`-02`, `-03`, etc.)

### Issue: API rate limiting
**Solution**: Adjust `API_RATE_LIMIT_DELAY` in `config.py`

### Issue: Poor filename quality
**Solution**: 
- Adjust AI prompt in `seo_namer.py`
- Add more target keywords to `LABELS` in `config.py`
- Increase `temperature` for more creativity

## Future Enhancements

Potential improvements:
- [ ] Multi-language support
- [ ] Custom keyword lists per project
- [ ] Filename templates
- [ ] Batch review/editing interface
- [ ] Export to CSV for manual review
