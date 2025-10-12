#!/usr/bin/env python3
"""
Full pipeline test WITHOUT AI classification.

This test runs the complete pipeline up to (but not including) AI classification:
1. Ingestion (thumbnails, EXIF, pHash)
2. Clustering (GPS + fused)
3. Stops before classification

Use this to verify the pipeline works without spending money on API calls.

Usage:
    python tests/test_full_pipeline_no_ai.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.ingestion import ingest
from photo_organizer.clustering import cluster_gps_only, fused_cluster
from photo_organizer.utils.filename import name_features
from photo_organizer.config import DEFAULT_SITE_DISTANCE_FEET, IMAGE_DIR, SCRIPT_DIR

# Setup paths - use same as main.py
input_dir = Path(IMAGE_DIR)
output_dir = SCRIPT_DIR / "organized"
work_dir = output_dir / "_work"
work_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("FULL PIPELINE TEST (NO AI)")
print("=" * 70)
print(f"Input: {input_dir}")
print(f"Output: {output_dir}")
print()

# STEP 1: INGESTION
print("=" * 70)
print("STEP 1: INGESTION")
print("=" * 70)

items = ingest(input_dir, work_dir)
name_map = {it.id: name_features(it.path) for it in items}

print(f"✅ Ingested: {len(items)} images")
gps_ct = sum(1 for it in items if it.gps)
print(f"   With GPS: {gps_ct}  Without GPS: {len(items)-gps_ct}")

if not items:
    print("❌ No images found!")
    sys.exit(1)

# Save ingest results
ingest_json = [
    {
        "id": it.id,
        "path": str(it.path),
        "thumb": str(it.thumb),
        "dt": it.dt.isoformat() if it.dt else None,
        "gps": it.gps,
        "phash": str(it.h) if it.h else None,
        "name": name_map[it.id].raw,
    }
    for it in items
]
with open(work_dir / "ingest.json", "w", encoding="utf-8") as f:
    json.dump(ingest_json, f, indent=2)
print(f"✅ Saved: {work_dir / 'ingest.json'}")

# STEP 2: CLUSTERING
print("\n" + "=" * 70)
print("STEP 2: CLUSTERING")
print("=" * 70)

# Split by GPS
with_gps = [it for it in items if it.gps]
without_gps = [it for it in items if not it.gps]

# GPS clustering
site_meters = DEFAULT_SITE_DISTANCE_FEET * 0.3048
gps_groups, gps_singletons = cluster_gps_only(with_gps, max_meters=site_meters)
print(f"✅ GPS clustering: {len(gps_groups)} groups, {len(gps_singletons)} singletons")

# Fused clustering for non-GPS photos
items_for_fused = without_gps + gps_singletons
th_groups = fused_cluster(
    items_for_fused, name_map, fuse_threshold=0.5, max_edges_per_node=5
)
print(f"✅ Fused clustering: {len(th_groups)} groups")

# Combine all groups
groups = gps_groups + th_groups
print(f"✅ Total clusters: {len(groups)}")


# Save clusters
def get_thumb_path(original_filename: str, work_dir: Path) -> str:
    """Construct full absolute path to thumbnail file."""
    stem = Path(original_filename).stem
    thumb_path = work_dir / "thumbs" / f"{stem}.jpg"
    return str(thumb_path.resolve())


summary = []
cluster_num = 1
for g in groups:
    has_gps = any(item.gps for item in g)
    strategy = "gps_location" if has_gps else "fused_clustering"

    summary.append(
        {
            "cluster": cluster_num,
            "count": len(g),
            "strategy": strategy,
            "has_gps": has_gps,
            "example": g[0].path.name,
            "files": [
                {
                    "name": item.path.name,
                    "thumb": get_thumb_path(item.path.name, work_dir),
                }
                for item in g
            ],
        }
    )
    cluster_num += 1

with open(work_dir / "clusters.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print(f"✅ Saved: {work_dir / 'clusters.json'}")

# STEP 3: STOPPED (No AI classification)
print("\n" + "=" * 70)
print("STEP 3: CLASSIFICATION - SKIPPED (No AI)")
print("=" * 70)
print("⏭️  AI classification skipped to avoid API costs")
print(
    f"   To classify, run: python -m photo_organizer.cli run --input {input_dir} --classify"
)

# Print summary
print("\n" + "=" * 70)
print("PIPELINE TEST COMPLETE")
print("=" * 70)
print(f"✅ Thumbnails created: {work_dir / 'thumbs/'}")
print(f"✅ Metadata saved: {work_dir / 'ingest.json'}")
print(f"✅ Clusters saved: {work_dir / 'clusters.json'}")
print()
print("📊 Cluster Statistics:")
print(f"   Total images: {len(items)}")
print(f"   Total clusters: {len(groups)}")
print(f"   Average cluster size: {len(items) / len(groups):.1f}")
print(f"   Largest cluster: {max(len(g) for g in groups)}")
print(f"   Smallest cluster: {min(len(g) for g in groups)}")
print(f"   Singletons: {sum(1 for g in groups if len(g) == 1)}")
print()

# Show first 5 clusters
print("First 5 clusters:")
for i, cluster_info in enumerate(summary[:5], 1):
    print(
        f"  {i}. {cluster_info['example']} ({cluster_info['count']} images, {cluster_info['strategy']})"
    )

print()
print("✅ Test passed! Pipeline works up to AI classification step.")
