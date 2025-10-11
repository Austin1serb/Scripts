#!/usr/bin/env python3
"""
Test matching unclustered images to existing clusters using AI vision comparison.

This test:
1. Loads existing clusters and their example images
2. Finds images not in any cluster
3. Uses AI to compare unclustered images against cluster examples
4. Suggests cluster assignments based on visual similarity

Usage:
    python tests/test_cluster_matching.py
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.models import Item
from photo_organizer.ai_classification.openai_classifier import classify_batches, b64


@dataclass
class Cluster:
    """Represents a cluster of related images."""

    id: int
    example_image: str
    example_thumb: str
    strategy: str
    has_gps: bool
    count: int


def load_clusters() -> List[Cluster]:
    """Load existing clusters from clusters.json."""
    clusters_file = project_root / "organized" / "_work" / "clusters.json"

    if not clusters_file.exists():
        raise FileNotFoundError(f"clusters.json not found at {clusters_file}")

    with open(clusters_file, "r") as f:
        data = json.load(f)

    clusters = []
    for cluster in data:
        clusters.append(
            Cluster(
                id=cluster["cluster"],
                example_image=cluster["example"],
                example_thumb=cluster["files"][0]["thumb"],  # First file is example
                strategy=cluster["strategy"],
                has_gps=cluster["has_gps"],
                count=cluster["count"],
            )
        )

    print(f"Loaded {len(clusters)} existing clusters")
    return clusters


def load_all_images() -> List[Item]:
    """Load all images from ingest.json."""
    ingest_file = project_root / "organized" / "_work" / "ingest.json"

    if not ingest_file.exists():
        raise FileNotFoundError(f"ingest.json not found at {ingest_file}")

    with open(ingest_file, "r") as f:
        metadata = json.load(f)

    items = []
    for item_data in metadata:
        thumb_path = Path(item_data["thumb"])
        if thumb_path.exists():
            item = Item(
                id=item_data["id"],
                path=Path(item_data["path"]),
                thumb=thumb_path,
                dt=item_data.get("dt"),
                gps=item_data.get("gps"),
                h=None,
            )
            items.append(item)

    print(f"Loaded {len(items)} total images")
    return items


def find_unclustered_images(
    all_images: List[Item], clusters: List[Cluster]
) -> List[Item]:
    """Find images that aren't in any cluster."""
    clustered_images = set()
    for cluster in clusters:
        clustered_images.add(cluster.example_image)

    unclustered = []
    for img in all_images:
        if img.id not in clustered_images:
            unclustered.append(img)

    print(f"Found {len(unclustered)} unclustered images")
    return unclustered


def compare_with_cluster(image: Item, cluster: Cluster) -> Dict[str, Any]:
    """Compare an image with a cluster's example image using AI."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert at comparing construction project photos. "
                "Determine if two photos are from the same concrete project by analyzing: "
                "materials, patterns, lighting, time of day, surroundings, and construction phase."
            ),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Compare these two photos and determine if they're from the same concrete project. "
                        "Photo 1 is from an existing project cluster. Photo 2 is unclustered. "
                        "Consider:\n"
                        "1. Concrete patterns and textures\n"
                        "2. Construction phase\n"
                        "3. Surroundings and context\n"
                        "4. Lighting and time of day\n"
                        "Return a JSON response with:\n"
                        "- match_score: 0.0-1.0 (how likely they're from same project)\n"
                        "- reasoning: Brief explanation of your decision\n"
                        "- same_project: true/false (recommend if they should be clustered together)"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64(Path(cluster.example_thumb))}"
                    },
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64(image.thumb)}"},
                },
            ],
        },
    ]

    schema = {
        "type": "object",
        "properties": {
            "match_score": {"type": "number", "minimum": 0, "maximum": 1},
            "reasoning": {"type": "string"},
            "same_project": {"type": "boolean"},
        },
        "required": ["match_score", "reasoning", "same_project"],
        "additionalProperties": False,
    }

    # Call OpenAI API
    results = classify_batches(
        items=[image], batch_size=1, model="gpt-4o", messages=messages, schema=schema
    )

    return results.get(image.id, {})


def test_cluster_matching(
    max_images: int = 10, min_score: float = 0.8
) -> Dict[str, Any]:
    """Test matching unclustered images to existing clusters."""
    print(f"🔍 Testing Cluster Matching")
    print("=" * 60)

    # Load data
    clusters = load_clusters()
    all_images = load_all_images()
    unclustered = find_unclustered_images(all_images, clusters)

    # Limit test size
    test_images = unclustered[:max_images]
    print(f"Testing with {len(test_images)} unclustered images")

    results = {"status": "success", "matches": [], "errors": []}

    # Compare each unclustered image with cluster examples
    for img in test_images:
        print(f"\nAnalyzing {img.id}...")
        best_match = None
        best_score = 0
        best_cluster = None

        for cluster in clusters:
            try:
                comparison = compare_with_cluster(img, cluster)
                score = comparison.get("match_score", 0)
                if score > best_score:
                    best_score = score
                    best_match = comparison
                    best_cluster = cluster
            except Exception as e:
                print(f"Error comparing with cluster {cluster.id}: {e}")
                results["errors"].append(
                    {"image": img.id, "cluster": cluster.id, "error": str(e)}
                )

        if best_match and best_score >= min_score:
            print(
                f"✅ Found match: Cluster {best_cluster.id} (score: {best_score:.2f})"
            )
            print(f"   Reason: {best_match['reasoning']}")
            results["matches"].append(
                {
                    "image": img.id,
                    "cluster": best_cluster.id,
                    "score": best_score,
                    "reasoning": best_match["reasoning"],
                }
            )
        else:
            print("❌ No strong matches found")

    # Save results
    output_file = Path(__file__).parent / "cluster_matching_output.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📁 Results saved to: {output_file}")
    print(f"Found {len(results['matches'])} matches out of {len(test_images)} images")

    return results


def main():
    """Main test function."""
    print("🧪 Cluster Matching Test")
    print("=" * 60)

    try:
        results = test_cluster_matching(max_images=10, min_score=0.8)

        if results["status"] == "success":
            print("✅ Test completed successfully!")
            if results["matches"]:
                print("\nRecommended cluster assignments:")
                for match in results["matches"]:
                    print(f"• {match['image']} → Cluster {match['cluster']}")
                    print(f"  Score: {match['score']:.2f}")
                    print(f"  Reason: {match['reasoning']}")
            return 0
        else:
            print("❌ Test failed!")
            return 1

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
