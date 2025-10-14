"""Name-Only Mode: SEO-optimized AI naming without re-clustering or matching.

This mode takes existing clusters from the clustering step and:
1. Flattens ALL images from ALL clusters into one list
2. Creates collages (50 images per collage) with numbered positions
3. Uses AI to generate unique SEO-optimized filenames for each image
4. Maps filenames back to original images and clusters
5. Organizes photos with location/brand added to AI-generated names

NO sorting, NO matching, NO merging - just SEO naming what already exists.
"""

from pathlib import Path
from typing import List, Dict

from .models import Item
from .ai_classification.seo_namer import generate_seo_filenames_for_all_images


def name_only_mode(
    groups: List[List[Item]],
    output_dir: Path,
    model: str = "gpt-4o",
    max_images_per_collage: int = 50,
) -> Dict[str, Dict]:
    """Name-only mode: Generate SEO-optimized filenames for all images.

    Process:
    1. Flatten all images from all clusters into one list
    2. Create collages (50 images per collage, numbered 0-49, 50-99, etc.)
    3. Send each collage to AI to get unique SEO filenames
    4. Map filenames back to original images
    5. Return labels dict for organization step

    Args:
        groups: List of clusters from clustering step
        output_dir: Directory for collages
        model: OpenAI model to use
        max_images_per_collage: Max images per collage (default: 50)

    Returns:
        Dictionary mapping item IDs to {"seo_filename": str} for organization
    """
    print("\n" + "=" * 60)
    print("NAME-ONLY MODE: SEO-Optimized AI Naming")
    print("=" * 60)

    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Collages will be saved to: {output_dir}")

    # Step 1: Flatten all images from all clusters
    print(f"\n📊 Flattening images from {len(groups)} clusters...")
    all_items: List[Item] = []
    for cluster in groups:
        all_items.extend(cluster)

    print(f"   Total images to name: {len(all_items)}")

    # Step 2 & 3: Create collages and get AI filenames
    seo_filenames = generate_seo_filenames_for_all_images(
        all_items=all_items,
        collage_dir=output_dir,
        images_per_collage=max_images_per_collage,
        model=model,
    )

    # Step 4: Convert to labels format for organization step
    # Organization expects: {item_id: {"label": str, ...}}
    # We'll use "seo_filename" key to distinguish from regular classification
    labels: Dict[str, Dict] = {}
    for item_id, filename in seo_filenames.items():
        labels[item_id] = {
            "seo_filename": filename,  # AI-generated SEO filename (without extension)
            "label": "seo-optimized",  # Placeholder for compatibility
            "confidence": 1.0,
        }

    print(f"\n✅ Generated {len(labels)} unique SEO filenames")
    print(f"   Ready for organization step (will add location/brand)")

    return labels
