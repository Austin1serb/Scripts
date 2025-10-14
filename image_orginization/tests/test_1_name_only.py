"""Test the name-only mode: collage-based naming without sorting/matching.

This test runs the full pipeline with --name-only flag:
1. Ingestion (existing)
2. Clustering (existing)
3. Name-only classification (creates collages, AI names them)
4. Organization (outputs to folders)
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from photo_organizer.ingestion import ingest
from photo_organizer.clustering.fused import fused_cluster
from photo_organizer.name_only import name_only_mode
from photo_organizer.organization import organize_photos


def test_name_only_mode():
    """Test name-only mode on existing clusters."""

    print("\n" + "=" * 60)
    print("TEST: Name-Only Mode (Collage-Based Naming)")
    print("=" * 60)

    # Setup paths
    script_dir = Path(__file__).parent.parent
    input_dir = script_dir / "organized"  # Use existing ingestion data
    output_dir = script_dir / "test_output" / "name_only"
    work_dir = input_dir / "_work"

    # Check if we have existing data
    clusters_file = work_dir / "clusters.json"
    if not clusters_file.exists():
        print(f"❌ No existing clusters found at {clusters_file}")
        print("   Run main pipeline first to generate clusters.")
        return

    # Load existing clusters
    print(f"\n📂 Loading existing clusters from: {clusters_file}")
    with open(clusters_file, "r") as f:
        clusters_data = json.load(f)

    print(f"✅ Loaded {len(clusters_data)} clusters")

    # Convert cluster data back to Item objects for name_only_mode
    from photo_organizer.models import Item

    groups = []
    for cluster_info in clusters_data:
        cluster_items = []
        for file_info in cluster_info.get("files", []):
            # Create minimal Item object
            item = Item(
                id=file_info["name"],
                path=Path(file_info["name"]),  # Dummy path
                thumb=Path(file_info["thumb"]),
                h=None,
                gps=None,
                dt=None,
            )
            cluster_items.append(item)

        if cluster_items:
            groups.append(cluster_items)

    print(f"✅ Converted to {len(groups)} cluster groups")

    # Run name-only mode
    print(f"\n🎨 Running name-only mode...")
    labels = name_only_mode(
        groups=groups,
        output_dir=work_dir,
        model="gpt-4o",
        max_images_per_collage=50,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total images labeled: {len(labels)}")

    # Count labels
    label_counts = {}
    for label_info in labels.values():
        label = label_info.get("label", "unknown")
        label_counts[label] = label_counts.get(label, 0) + 1

    print(f"\nLabel distribution:")
    for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
        print(f"  {label}: {count} images")

    # Output collages location
    collage_dir = work_dir / "collages"
    if collage_dir.exists():
        collage_files = list(collage_dir.glob("*.jpg"))
        print(f"\n🖼️  Generated {len(collage_files)} collages in: {collage_dir}")
        print(f"   View collages: open {collage_dir}")

    print(f"\n✅ Name-only mode test complete!")


if __name__ == "__main__":
    test_name_only_mode()
