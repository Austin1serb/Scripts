#!/usr/bin/env python3
"""
Test optimized cluster-based classification.

This test demonstrates the cost savings of classifying only cluster examples
instead of every individual image.
"""

import json
from pathlib import Path

from photo_organizer.models import Item
from photo_organizer.ai_classification import classify_cluster_examples

# Setup paths
project_root = Path(__file__).parent.parent
work_dir = project_root / "organized" / "_work"
clusters_file = work_dir / "clusters.json"

# Load clusters
with open(clusters_file, "r") as f:
    clusters_data = json.load(f)

# Limit to first 5 clusters for testing
clusters_data = clusters_data[:5]

print(f"📊 Test Setup:")
print(f"   Clusters: {len(clusters_data)}")
print(f"   Total images: {sum(c['count'] for c in clusters_data)}")
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

print("🚀 Running optimized classification...")
print(f"   OLD WAY: Would classify {sum(len(g) for g in groups)} images")
print(f"   NEW WAY: Classifying only {len(groups)} examples")
print()

# Classify using optimized method
labels = classify_cluster_examples(
    groups=groups,
    batch_size=12,
    model="gpt-4o",
)

# Verify results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

for i, group in enumerate(groups, 1):
    example_id = group[0].id
    label_info = labels[example_id]

    print(f"\nCluster {i} ({len(group)} images):")
    print(f"  Label: {label_info['label']}")
    print(f"  Confidence: {label_info['confidence']:.0%}")
    print(f"  Descriptor: {label_info['descriptor']}")

    # Verify all images in cluster have same label
    for item in group:
        assert labels[item.id] == label_info, f"Label mismatch in cluster {i}"

    print(f"  ✅ All {len(group)} images have same label")

# Calculate savings
total_images = sum(len(g) for g in groups)
api_calls_old = (total_images + 11) // 12  # Batch size of 12
api_calls_new = (len(groups) + 11) // 12
savings = (
    ((api_calls_old - api_calls_new) / api_calls_old * 100) if api_calls_old else 0
)

print("\n" + "=" * 60)
print("COST SAVINGS")
print("=" * 60)
print(f"Old approach: {api_calls_old} API calls")
print(f"New approach: {api_calls_new} API calls")
print(f"Savings: {savings:.0f}% 💰")

# Save results
output_file = Path(__file__).parent / "cluster_classification_test.json"
with open(output_file, "w") as f:
    json.dump(labels, f, indent=2)

print(f"\n✅ Results saved to: {output_file}")
