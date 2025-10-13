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

# Limit to first N clusters for testing (adjust as needed)
# Use 20-30 clusters to demonstrate collage savings without excessive API costs
#
# Examples:
#   TEST_CLUSTER_COUNT = 5   → Quick test (~$0.25)
#   TEST_CLUSTER_COUNT = 20  → Better demo (~$1.00)
#   TEST_CLUSTER_COUNT = 50  → Full collage test (~$2.50)
#   TEST_CLUSTER_COUNT = None → ALL clusters (expensive!)
#
TEST_CLUSTER_COUNT = 20  # Change this to test with more/fewer clusters

if TEST_CLUSTER_COUNT is not None:
    clusters_data = clusters_data[:TEST_CLUSTER_COUNT]

total_images = sum(c["count"] for c in clusters_data)
num_clusters = len(clusters_data)

print("=" * 70)
print("AI CLASSIFICATION TEST")
print("=" * 70)
print(f"Clusters to classify: {num_clusters}")
print(f"Total images: {total_images}")
print()
print("API Call Comparison:")
print(f"  OLD (classify every image): {total_images} API calls")
print(f"  NEW (classify cluster examples): {num_clusters} API calls")
print(
    f"  💰 SAVINGS: {((total_images - num_clusters) / total_images * 100):.0f}% reduction!"
)
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
print("COST SAVINGS SUMMARY")
print("=" * 70)
print(f"Total images in test: {total_images}")
print(f"Total clusters in test: {num_clusters}")

# Calculate collage API calls
collage_calls = (num_clusters + 49) // 50

print()
print("Method Comparison (this test):")
print(f"  1. Individual images:     {total_images} API calls")
print(f"  2. Cluster examples:      {num_clusters} API calls (this test used)")
print(
    f"  3. Collage mode (50/img): {collage_calls} API call{'s' if collage_calls != 1 else ''}"
)
print()
print(f"Savings vs individual:")
print(
    f"  Cluster examples: {((total_images - num_clusters) / total_images * 100):.0f}% reduction"
)
if collage_calls < total_images:
    print(
        f"  Collage mode:     {((total_images - collage_calls) / total_images * 100):.0f}% reduction"
    )

# Show full dataset projection
with open(clusters_file, "r") as f:
    all_clusters = json.load(f)
total_all_images = sum(c["count"] for c in all_clusters)
total_all_clusters = len(all_clusters)
all_collage_calls = (total_all_clusters + 49) // 50

print()
print(
    f"Full Dataset Projection ({total_all_clusters} clusters, {total_all_images} images):"
)
print(
    f"  Individual images:     {total_all_images} API calls (~${total_all_images * 0.05:.2f})"
)
print(
    f"  Cluster examples:      {total_all_clusters} API calls (~${total_all_clusters * 0.05:.2f}) "
    f"- {((total_all_images - total_all_clusters) / total_all_images * 100):.0f}% reduction"
)
print(
    f"  Collage mode (50/img): {all_collage_calls} API calls (~${all_collage_calls * 0.05:.2f}) "
    f"- {((total_all_images - all_collage_calls) / total_all_images * 100):.0f}% reduction"
)
print()
print("=" * 70)
print(f"✅ Full results saved to: {output_file}")
print("=" * 70)
print()
print("💡 Review the AI labels above to verify they make sense for your photos.")
print("💡 Enable collage mode in config.py for even greater savings!")
