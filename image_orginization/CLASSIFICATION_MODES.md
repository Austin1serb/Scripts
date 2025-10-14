# Classification Modes

The photo organizer supports three classification modes, each with different trade-offs between simplicity, accuracy, and cost.

## Mode Comparison

| Feature | Name-Only | Standard | Unified Matching |
|---------|-----------|----------|------------------|
| **CLI Flag** | `--name-only` | `--classify` | `--classify --assign-singletons` |
| **Config Required** | None | None | `ENABLE_UNIFIED_MATCHING = True` |
| **AI Sorting** | ❌ No | ✅ Yes | ✅✅ Yes (Advanced) |
| **AI Matching** | ❌ No | ❌ No | ✅ Yes |
| **Collage-Based** | ✅ Yes | ❌ No | ✅ Yes (for matching) |
| **API Calls** | ~1 per 50 images | ~1 per cluster | ~1 per cluster + matching |
| **Complexity** | Simple | Medium | Advanced |
| **Best For** | Trusted clustering | Most use cases | Maximum accuracy |

---

## 1. Name-Only Mode 🎨

**CLI:**
```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --name-only \
  --model gpt-4o
```

**How it works:**
1. Takes existing clusters from clustering step (GPS + time + filename + hash)
2. Groups small clusters (1-2 images) into city-based "misc" folders
3. Creates collages for each cluster (50 images max per collage)
4. Uses AI to name each cluster based on the collage
5. Organizes original photos into folders by AI-generated names

**Pros:**
- ✅ Simplest mode (no AI sorting/matching)
- ✅ Fewest API calls (~1 per 50 images)
- ✅ Most cost-effective
- ✅ Maximum control (you control clustering, AI just names)
- ✅ Fastest execution

**Cons:**
- ❌ No AI-based cluster refinement
- ❌ Relies entirely on clustering accuracy
- ❌ No singleton assignment to existing clusters

**When to use:**
- You trust the clustering step
- You want AI naming without AI re-clustering
- Cost is a primary concern
- You want maximum simplicity

---

## 2. Standard Classification Mode 🎯

**CLI:**
```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --classify \
  --batch-size 12 \
  --model gpt-4o
```

**How it works:**
1. Takes existing clusters from clustering step
2. Selects best representative image from each cluster
3. Classifies all cluster examples in batches
4. Propagates labels to all images in each cluster
5. Organizes photos into folders

**Pros:**
- ✅ Balanced approach (AI classification without re-clustering)
- ✅ Efficient (~1 API call per cluster)
- ✅ Good accuracy for well-formed clusters
- ✅ Medium complexity

**Cons:**
- ❌ No singleton assignment
- ❌ No cluster refinement
- ❌ Singletons remain as individual folders

**When to use:**
- Default recommended mode for most use cases
- You want AI classification without extra complexity
- Clustering already produced good results

---

## 3. Unified Matching Mode (Advanced) 🚀

**CLI:**
```bash
python main.py run \
  --input "/path/to/photos" \
  --output "/path/to/organized" \
  --classify \
  --assign-singletons \
  --model gpt-4o
```

**Config:** Set `ENABLE_UNIFIED_MATCHING = True` in `config.py`

**How it works:**
1. Separates clusters into "confident" and "uncertain":
   - **Confident:** GPS-based, time+filename+hash, filename+hash
   - **Uncertain:** Singletons, hash-only clusters
2. Classifies confident clusters first
3. Creates collage of confident clusters
4. Matches each uncertain item against the collage
5. Merges uncertain items into confident clusters (if confidence > threshold)
6. Classifies remaining unmatched items
7. Organizes all photos

**Pros:**
- ✅ Maximum accuracy (AI matching + classification)
- ✅ Handles singletons intelligently
- ✅ Reduces singleton folders
- ✅ No 10-cluster limitation (uses collage)
- ✅ Conservative (confidence threshold prevents bad merges)

**Cons:**
- ❌ Most complex mode
- ❌ Highest API call count
- ❌ Requires tuning (`MIN_MATCH_CONFIDENCE`)
- ❌ Slower execution

**When to use:**
- You have many singletons or hash-only clusters
- Accuracy is more important than cost
- You're willing to tune confidence thresholds
- You want the most advanced AI capabilities

---

## Configuration Options

### Name-Only Mode

No special configuration needed. Just use `--name-only` flag.

**Tunable parameters in `name_only.py`:**
- `max_images_per_collage`: Images per collage (default: 50)
- `max_size`: Max cluster size to group as "small" (default: 2)

### Standard Classification Mode

**In `config.py`:**
```python
DEFAULT_AI_CLASSIFY = True  # Enable classification
DEFAULT_ASSIGN_SINGLETONS = False  # Disable matching
```

**Tunable parameters:**
- `DEFAULT_BATCH_SIZE`: Images per API batch (default: 12)
- `DEFAULT_MODEL`: OpenAI model (default: "gpt-4o")

### Unified Matching Mode

**In `config.py`:**
```python
DEFAULT_AI_CLASSIFY = True
DEFAULT_ASSIGN_SINGLETONS = True
ENABLE_UNIFIED_MATCHING = True

MIN_MATCH_CONFIDENCE = 0.65  # Adjust for accuracy vs coverage
MAX_SINGLETONS_TO_ASSIGN = 199  # Cost control

CONFIDENT_STRATEGIES = [
    "gps_location",
    "time+filename+hash",
    "filename+hash",
]

UNCERTAIN_STRATEGIES = [
    "hash_only",
]
```

**Tuning `MIN_MATCH_CONFIDENCE`:**
- **Higher (0.8-0.9):** Fewer merges, more accurate, more singleton folders
- **Lower (0.5-0.6):** More merges, less accurate, fewer singleton folders
- **Recommended:** Start at 0.65 and adjust based on results

---

## Quick Decision Tree

```
Do you want AI naming?
├─ No → Use basic mode (no --classify flag)
└─ Yes
   ├─ Trust clustering, want simplest/cheapest? → Name-Only Mode (--name-only)
   ├─ Want balanced approach? → Standard Mode (--classify)
   └─ Have many singletons, want maximum accuracy? → Unified Matching (--classify --assign-singletons)
```

---

## Cost Comparison (Example: 1000 images, 50 clusters, 100 singletons)

| Mode | API Calls | Approx Cost* |
|------|-----------|--------------|
| Name-Only | ~20-30 | $0.10-$0.15 |
| Standard | ~50 | $0.25 |
| Unified Matching | ~150 | $0.75 |

*Assumes gpt-4o pricing ($0.005 per image)

---

## Migration Guide

### From Standard to Name-Only:
1. Remove `--classify` flag
2. Add `--name-only` flag
3. No config changes needed

### From Standard to Unified Matching:
1. Keep `--classify` flag
2. Add `--assign-singletons` flag
3. Set `ENABLE_UNIFIED_MATCHING = True` in config.py
4. Tune `MIN_MATCH_CONFIDENCE` as needed

### From Unified Matching to Name-Only:
1. Remove `--classify` and `--assign-singletons` flags
2. Add `--name-only` flag
3. Optionally set `ENABLE_UNIFIED_MATCHING = False` in config.py
