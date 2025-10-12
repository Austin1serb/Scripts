#!/usr/bin/env python3
"""
Test photo organization using AI classification results.

This test loads the AI classification results from test_ai_classification.py
and tests the organize() function to see how photos would be organized.

Usage:
    python tests/test_organization.py

Results are saved to tests/organization_output.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.models import Item
from photo_organizer.organization import organize
import imagehash


def load_test_images() -> List[Item]:
    """Load test images from organized/_work directory."""
    organized_dir = project_root / "organized" / "_work"
    ingest_file = organized_dir / "ingest.json"
    thumbs_dir = organized_dir / "thumbs"

    if not ingest_file.exists():
        raise FileNotFoundError(f"ingest.json not found at {ingest_file}")

    if not thumbs_dir.exists():
        raise FileNotFoundError(f"thumbs directory not found at {thumbs_dir}")

    # Load metadata
    with open(ingest_file, "r") as f:
        metadata = json.load(f)

    # Convert to Item objects
    items = []
    for item_data in metadata:
        # Check if thumbnail exists
        thumb_path = Path(item_data["thumb"])
        if thumb_path.exists():
            # Convert phash string to ImageHash object if present
            phash_str = item_data.get("phash")
            phash_obj = None
            if phash_str:
                try:
                    phash_obj = imagehash.hex_to_hash(phash_str)
                except Exception as e:
                    print(f"Warning: Could not convert phash {phash_str}: {e}")

            item = Item(
                id=item_data["id"],
                path=Path(item_data["path"]),
                thumb=thumb_path,
                dt=item_data.get("dt"),
                gps=item_data.get("gps"),
                h=phash_obj,
            )
            items.append(item)
        else:
            print(f"Warning: Thumbnail not found for {item_data['id']}: {thumb_path}")

    print(f"Loaded {len(items)} images with valid thumbnails")
    return items


def load_ai_classification_results() -> Dict[str, Dict]:
    """Load AI classification results from test_ai_classification.py output."""
    output_file = Path(__file__).parent / "output.json"

    if not output_file.exists():
        raise FileNotFoundError(f"AI classification results not found at {output_file}")

    with open(output_file, "r") as f:
        data = json.load(f)

    if data.get("status") != "success":
        raise ValueError(
            f"AI classification failed: {data.get('error', 'Unknown error')}"
        )

    results = data.get("results", {})
    print(f"Loaded AI classification results for {len(results)} images")

    # Show classification summary
    label_counts = {}
    for result in results.values():
        label = result.get("label", "unknown")
        label_counts[label] = label_counts.get(label, 0) + 1

    print("Classification summary:")
    for label, count in sorted(label_counts.items()):
        print(f"  {label}: {count} images")

    return results


def create_test_clusters(items: List[Item], max_images: int = 10) -> List[List[Item]]:
    """Create test clusters from the first N images."""
    # Take first max_images items and create single-item clusters for testing
    test_items = items[:max_images]
    clusters = [[item] for item in test_items]  # Each image in its own cluster

    print(f"Created {len(clusters)} test clusters (one image per cluster)")
    return clusters


def test_organization(max_images: int = 10) -> Dict[str, Any]:
    """Test photo organization with AI classification results."""
    print(f"🗂️  Testing Photo Organization with {max_images} images")
    print("=" * 60)

    # Load test data
    all_items = load_test_images()
    ai_results = load_ai_classification_results()

    if len(all_items) == 0:
        raise ValueError("No images found to test")

    # Create test clusters
    test_clusters = create_test_clusters(all_items, max_images)

    # Filter AI results to only include test images
    test_image_ids = {item.id for cluster in test_clusters for item in cluster}
    test_ai_results = {
        id: result for id, result in ai_results.items() if id in test_image_ids
    }

    print(f"Using AI results for {len(test_ai_results)} test images")

    # Create test output directory
    test_output_dir = Path(__file__).parent / "test_organized"
    test_output_dir.mkdir(exist_ok=True)

    print(f"Output directory: {test_output_dir}")
    print("\n" + "=" * 60)

    # Test organization
    try:
        organize(
            groups=test_clusters,
            labels=test_ai_results,
            out_dir=test_output_dir,
            brand="RC Concrete",
            rotate_cities=True,
            use_semantic_keywords=True,  # Test with semantic keyword rotation
        )

        print(f"✅ Organization completed successfully!")

        # Analyze results
        manifest_file = test_output_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            print(f"Organized {len(manifest)} files:")

            # Group by folder
            folders = {}
            for entry in manifest:
                folder = Path(entry["dst"]).parent.name
                if folder not in folders:
                    folders[folder] = []
                folders[folder].append(entry)

            for folder, entries in folders.items():
                print(f"  📁 {folder}: {len(entries)} files")
                for entry in entries[:3]:  # Show first 3 files per folder
                    filename = Path(entry["dst"]).name
                    label = entry["label"]
                    print(f"    - {filename} ({label})")
                if len(entries) > 3:
                    print(f"    ... and {len(entries) - 3} more files")

        return {
            "status": "success",
            "total_images": len(test_clusters),
            "output_directory": str(test_output_dir),
            "manifest_file": str(manifest_file),
            "ai_results_used": test_ai_results,
            "clusters": [
                {
                    "cluster_id": i,
                    "items": [
                        {"id": item.id, "path": str(item.path)} for item in cluster
                    ],
                }
                for i, cluster in enumerate(test_clusters, 1)
            ],
        }

    except Exception as e:
        print(f"❌ Organization failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "total_images": len(test_clusters),
            "ai_results_used": test_ai_results,
        }


def main():
    """Main test function."""
    print("🧪 Photo Organization Test")
    print("=" * 60)

    # Run test
    try:
        results = test_organization(max_images=10)

        # Save results
        output_file = Path(__file__).parent / "organization_output.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📁 Results saved to: {output_file}")

        if results["status"] == "success":
            print("✅ Test completed successfully!")
            print(f"📁 Organized files in: {results['output_directory']}")
            return 0
        else:
            print("❌ Test failed!")
            return 1

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

        # Save error results
        error_results = {
            "status": "error",
            "error": str(e),
            "total_images": 0,
        }

        output_file = Path(__file__).parent / "organization_output.json"
        with open(output_file, "w") as f:
            json.dump(error_results, f, indent=2, default=str)

        print(f"📁 Error results saved to: {output_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
