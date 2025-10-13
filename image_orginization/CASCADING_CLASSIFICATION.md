# Cascading Classification Feature

## Overview

Cascading Classification is an advanced AI classification strategy that solves the **cluster comparison limit** problem by using label-guided filtering for singleton matching.

### The Problem It Solves

**Old Approach (without cascading):**
- API has `MAX_CLUSTERS_PER_CALL = 10` limit
- Singleton can only compare against first 10 clusters
- If you have 50 clusters, singleton never sees clusters 11-50
- Result: Many false "no match" results

**New Approach (with cascading):**
- Classify high-confidence clusters FIRST to get their labels
- Classify singleton to get its label
- Filter clusters by matching label
- Singleton compares only against matching clusters
- Result: Can match against UNLIMITED clusters!

---

## How It Works

### 5-Phase Process

#### Phase 1: Separate by Confidence
```
Input: 100 clusters total

Analysis:
- 60 high-confidence (GPS, time+filename+hash)
- 15 low-confidence (hash_only)
- 25 singletons (len=1)
```

#### Phase 2: Classify High-Confidence First
```
classify_cluster_examples(60 high-confidence clusters)
→ 60 API calls
→ Labels: {"img1": "stamped-concrete-driveway", "img2": "concrete-patio", ...}
```

#### Phase 3: Classify Singletons
```
For each singleton:
  classify_singleton(singleton) → "stamped-concrete-driveway"

→ 25 API calls
→ Labels: {"singleton1": "stamped-concrete-driveway", ...}
```

#### Phase 4: Label-Guided Matching
```
For singleton with label "stamped-concrete-driveway":

  1. Filter clusters:
     matching = [c for c in 60 high-conf if c.label == "stamped-concrete-driveway"]
     → Found: [cluster_1, cluster_5, cluster_12, cluster_22]

  2. Show singleton:
     - 4 matching clusters (stamped driveways)
     - + 5 largest clusters (for context)
     → Total: 9 clusters shown (not 60!)

  3. AI assigns:
     → "This singleton matches cluster_5"

  4. Merge:
     cluster_5.append(singleton)

→ ~25 API calls (one per singleton batch)
→ Result: 18 matched, 7 remain unmatched
```

#### Phase 5: Classify Remaining
```
classify_cluster_examples(15 low-conf + 7 unmatched singletons)
→ 22 API calls
```

---

## Cost Analysis

### API Call Comparison

**Basic Classification (no cascading):**
```
100 clusters = 100 API calls
```

**Cascading Classification:**
```
Phase 2: 60 high-confidence = 60 calls
Phase 3: 25 singletons      = 25 calls
Phase 4: 25 matching        = 25 calls
Phase 5: 22 remaining       = 22 calls
TOTAL:                      = 132 calls
```

**Trade-off:**
- 32% more API calls
- **Much better accuracy** (unlimited cluster comparison)
- **Fewer false negatives** (singletons find their clusters)

---

## When to Use

### Use Cascading Classification When:

✅ You have **many clusters** (>10)
✅ You have **many singletons** (>10% of total clusters)
✅ You want **maximum accuracy** for singleton assignment
✅ Clustering is already good (GPS + time-based)

### Skip Cascading When:

❌ You have **few clusters** (<10)
❌ You have **few singletons** (<5% of total)
❌ You want to **minimize API costs**
❌ Clustering is poor (singletons are truly unique, not false separations)

---

## Usage

### Enable Cascading Classification

```bash
python main.py run \
  --input "photos/" \
  --output "organized/" \
  --classify \
  --assign-singletons \  # ← Enables cascading
  --model gpt-4o
```

### Configuration

Edit `photo_organizer/config.py`:

```python
# Enable/disable cascading
ENABLE_CASCADING_CLASSIFICATION = True

# Define high-confidence strategies
HIGH_CONFIDENCE_STRATEGIES = [
    "gps_location",         # GPS-based clusters
    "time+filename+hash",   # Strong temporal + filename match
]

# Define low-confidence strategies
LOW_CONFIDENCE_STRATEGIES = [
    "filename+hash",  # Filename + visual only
    "hash_only",      # Visual similarity only
]

# Singleton matching limits
MAX_SINGLETONS_TO_ASSIGN = 20      # Max singletons to process
SINGLETON_BATCH_SIZE = 5           # Singletons per API call
CLUSTER_SAMPLES_PER_CLUSTER = 2    # Sample images from each cluster
MAX_CLUSTERS_PER_CALL = 10         # Max clusters to show per API call
```

---

## Implementation Details

### New Functions

#### `classify_singleton(item, model)`
**Location:** `photo_organizer/ai_classification/openai_classifier.py:196`

Classifies a single image (wrapper around `classify_batches` with batch_size=1).

```python
singleton_label = classify_singleton(singleton_item, "gpt-4o")
# → {"label": "stamped-concrete-driveway", "confidence": 0.95, "descriptor": "..."}
```

#### `assign_singletons_batched(..., cluster_labels)`
**Location:** `photo_organizer/ai_classification/openai_classifier.py:327`

**NEW parameter:** `cluster_labels: Dict[str, Dict]`

When provided, enables cascading mode:
- Classifies each singleton first
- Filters clusters by matching label
- Shows only matching + top N largest clusters
- Uses label-guided prompt for better context

```python
assignments = assign_singletons_batched(
    singletons,
    high_conf_clusters,
    model="gpt-4o",
    cluster_labels=high_conf_labels,  # ← NEW
)
```

### New Messages

#### `build_singleton_assignment_messages_with_labels()`
**Location:** `photo_organizer/ai_classification/messages.py:54`

Builds prompt for label-guided singleton matching:

```
System: "You are an expert at matching construction photos to LABELED project clusters.
         Each cluster has already been classified with a specific label
         (e.g., 'stamped-concrete-driveway')..."
```

#### `add_cluster_label_message(cluster_id, label, num_samples)`
**Location:** `photo_organizer/ai_classification/messages.py:88`

Updated to include label in cluster description:

```
Old: "CLUSTER 5 (2 sample photos):"
New: "CLUSTER 5: stamped-concrete-driveway (2 sample photos):"
```

---

## Testing

### Test the Cascading Flow

```bash
# Run test (uses existing organized/_work data)
python tests/test_5_classification_ai.py

# Output: test_output/5_ai_classification_output.json
```

The test classifies 5 clusters and shows:
- Example images
- Thumbnail paths
- AI labels and confidence scores
- All images in each cluster

---

## Benefits Summary

### Accuracy Improvements

1. **Unlimited Cluster Comparison**
   - Old: Singleton vs first 10 clusters only
   - New: Singleton vs ALL matching clusters

2. **Semantic + Visual Matching**
   - Old: Visual similarity only
   - New: Label filtering + visual similarity

3. **Contextual Understanding**
   - Old: AI sees unlabeled clusters
   - New: AI sees "CLUSTER 5: stamped-concrete-driveway"

4. **Reduced False Negatives**
   - Old: Singleton doesn't see its cluster (beyond 10)
   - New: Singleton always sees matching clusters

### Real-World Example

**Scenario:** 50 clusters, 20 singletons

**Without Cascading:**
```
Singleton: IMG_999.jpg
Compared against: Clusters 1-10 (first 10 only)
Result: "No match found" (actual match was cluster 35)
```

**With Cascading:**
```
Singleton: IMG_999.jpg → classified as "concrete-patio"

Filter:
  50 clusters → 8 have label "concrete-patio"
  Show: 8 matching + 5 largest = 13 clusters

Compared against: 13 filtered clusters (includes cluster 35!)
Result: "Matches cluster 35" ✅
```

---

## Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `ENABLE_CASCADING_CLASSIFICATION` | `True` | Master switch for cascading |
| `HIGH_CONFIDENCE_STRATEGIES` | `["gps_location", "time+filename+hash"]` | Strategies considered reliable |
| `LOW_CONFIDENCE_STRATEGIES` | `["filename+hash", "hash_only"]` | Strategies needing more validation |
| `MAX_SINGLETONS_TO_ASSIGN` | `20` | Cost control limit |
| `SINGLETON_BATCH_SIZE` | `5` | Singletons per API batch |
| `CLUSTER_SAMPLES_PER_CLUSTER` | `2` | Sample images shown per cluster |
| `MAX_CLUSTERS_PER_CALL` | `10` | Max clusters compared per API call |

---

## Troubleshooting

### "Too many API calls"
- Reduce `MAX_SINGLETONS_TO_ASSIGN`
- Disable cascading: `ENABLE_CASCADING_CLASSIFICATION = False`
- Or disable singleton assignment: Don't use `--assign-singletons`

### "Singletons not matching clusters"
- Increase `MAX_CLUSTERS_PER_CALL` to show more context clusters
- Check cluster labels are accurate (run test_5_classification_ai.py)
- Verify clustering strategy (high-confidence clusters should have good labels)

### "Wrong singleton assignments"
- Check if singleton label matches cluster label
- Increase `CLUSTER_SAMPLES_PER_CLUSTER` to show more context
- Review AI confidence scores in labels.json

---

## Future Improvements

Potential enhancements:

1. **Batch Singleton Classification**
   - Currently: 1 singleton → 1 API call
   - Improvement: Batch N singletons → 1 API call
   - Savings: N× reduction in Phase 3

2. **Confidence Thresholds**
   - Skip Phase 4 if singleton confidence < 0.5
   - Treat as "truly unique" rather than mismatched

3. **Iterative Refinement**
   - After Phase 5, re-evaluate low-confidence assignments
   - Use final labels to re-filter and re-assign

4. **Cluster Merging**
   - Extend cascading to merge small clusters (2-5 images)
   - Use label matching to suggest merges

---

## Credits

Implemented based on user feedback about MAX_CLUSTERS_PER_CALL limitation.

**Key Insight:** "Why classify every singleton against all clusters when we can filter by label first?"

This cascading approach combines the benefits of:
- Hierarchical clustering (high-confidence first)
- Semantic filtering (label-guided)
- Visual matching (AI comparison)

Result: More accurate singleton assignment with controlled cost increase.
