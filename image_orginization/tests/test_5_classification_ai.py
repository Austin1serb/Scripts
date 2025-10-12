#!/usr/bin/env python3
"""
Test AI classification and view the actual output.

This test classifies a few cluster examples and shows what the AI returns
for each cluster so you can verify the labels make sense.
"""

import json
from pathlib import Path

from photo_organizer.models import Item
from photo_organizer.ai_classification import classify_cluster_examples

# Setup paths
project_root = Path(__file__).parent.parent
work_dir = project_root / "organized" / "_work"
clusters_file = work_dir / "clusters.json"
test_output_dir = project_root / "test_output"
test_output_dir.mkdir(exist_ok=True)
output_file = test_output_dir / "5_ai_classification_output.json"

# Load clusters
with open(clusters_file, "r") as f:
    clusters_data = json.load(f)

# Limit to first 5 clusters for testing
clusters_data = clusters_data[:5]

print("=" * 70)
print("AI CLASSIFICATION TEST")
print("=" * 70)
print(f"Clusters to classify: {len(clusters_data)}")
print(f"Total images: {sum(c['count'] for c in clusters_data)}")
print()

# Convert cluster data to Item objects
groups = []
for cluster_info in clusters_data:
    group = []
    for file_info in cluster_info["files"]:
        # Create Item from cluster data
        item = Item(
            id=file_info["name"],
            path=Path(file_info["name"]),
            thumb=Path(file_info["thumb"]),
            dt=None,
            gps=None,
            h=None,
        )
        group.append(item)
    groups.append(group)

print("🤖 Calling OpenAI API...")
print(f"   Classifying {len(groups)} cluster examples")
print()

# Classify using optimized method
labels = classify_cluster_examples(
    groups=groups,
    batch_size=12,
    model="gpt-4o",
)

# Display results with full details
print("=" * 70)
print("AI CLASSIFICATION RESULTS")
print("=" * 70)

for i, group in enumerate(groups, 1):
    example_id = group[0].id
    label_info = labels[example_id]

    print(f"\n{'='*70}")
    print(f"CLUSTER {i} ({len(group)} images)")
    print(f"{'='*70}")
    print(f"Example image: {example_id}")
    print()
    print(f"AI Classification:")
    print(f"  Label:       {label_info['label']}")
    print(f"  Confidence:  {label_info['confidence']:.0%}")
    print(f"  Description: {label_info['descriptor']}")
    print()
    print(f"Images in this cluster:")
    for item in group:
        print(f"  • {item.id}")

    # Verify all images in cluster have same label
    for item in group:
        assert labels[item.id] == label_info, f"Label mismatch in cluster {i}"

# Save full results to JSON with thumbnail paths
results_for_json = {}
for i, group in enumerate(groups, 1):
    example_id = group[0].id
    label_info = labels[example_id]

    results_for_json[f"cluster_{i}"] = {
        "example_image": example_id,
        "example_thumb": str(group[0].thumb),  # Thumbnail for quick preview
        "total_images": len(group),
        "all_images": [
            {
                "name": item.id,
                "thumb": str(item.thumb),  # Include thumb for each image
            }
            for item in group
        ],
        "classification": {
            "label": label_info["label"],
            "confidence": label_info["confidence"],
            "descriptor": label_info["descriptor"],
        },
    }

with open(output_file, "w") as f:
    json.dump(results_for_json, f, indent=2)

print()
print("=" * 70)
print(f"✅ Full results saved to: {output_file}")
print("=" * 70)
print()
print("💡 Review the AI labels above to verify they make sense for your photos.")
