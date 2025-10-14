"""Test collage generation using actual thumbnail images.

This test creates a grid collage from thumbnails in organized/_work/thumbs/
and outputs it to test_output/ for visual inspection.

Configuration:
    - COLLAGE_SIZE: Number of images to include (max)
    - GRID_COLS: Number of columns in the grid
    - THUMB_SIZE: Size of each thumbnail in pixels
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from photo_organizer.ai_classification.collage import create_cluster_collage
from photo_organizer.models import Item
from PIL import Image

# ============================================================================
# CONFIGURATION - Tweak these values
# ============================================================================
COLLAGE_SIZE = 50  # Number of images in collage
GRID_COLS = 10  # Grid columns (e.g., 10 cols × 5 rows = 50 images)
THUMB_SIZE = 256  # Size of each thumbnail in pixels (256, 384, or 512)
# ============================================================================


def test_create_collage():
    """Create a test collage from actual thumbnail images."""

    # Setup paths
    script_dir = Path(__file__).parent.parent
    thumbs_dir = script_dir / "organized" / "_work" / "thumbs"
    output_dir = script_dir / "test_output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n🖼️  Collage Test")
    print(f"━" * 60)
    print(f"📁 Reading thumbnails from: {thumbs_dir}")

    # Check if thumbs directory exists
    if not thumbs_dir.exists():
        print(f"❌ Thumbnails directory not found: {thumbs_dir}")
        print("   Run the main script first to generate thumbnails.")
        return

    # Get all thumbnail images
    thumb_files = sorted(thumbs_dir.glob("*.jpg"))[:COLLAGE_SIZE]

    if not thumb_files:
        print(f"❌ No thumbnail images found in {thumbs_dir}")
        return

    print(f"✅ Found {len(thumb_files)} thumbnails")
    print(
        f"📐 Collage config: {len(thumb_files)} images, {GRID_COLS} columns, {THUMB_SIZE}px thumbnails"
    )

    # Create fake clusters (each "cluster" is just one Item with a thumbnail)
    # We're just testing the collage layout, not actual clustering logic
    fake_clusters = []
    for idx, thumb_path in enumerate(thumb_files, start=1):
        # Create a minimal Item object with just the thumbnail path
        # Using a dummy path for the original since we only need the thumb
        item = Item(
            id=f"thumb_{idx}",
            path=Path(f"/fake/path/{thumb_path.name}"),
            thumb=thumb_path,
            h=None,  # Not needed for collage
            gps=None,
            dt=None,
        )
        fake_clusters.append([item])  # Each cluster has 1 item

    # Optional: Create fake labels for testing labeled collages
    fake_labels = {
        f"thumb_{idx}": {"label": f"cluster-{idx}", "confidence": 0.95}
        for idx in range(1, len(fake_clusters) + 1)
    }

    # Generate collage
    print(f"\n🎨 Creating collage...")
    output_path = output_dir / "0_test_collage.jpg"

    collage_path = create_cluster_collage(
        clusters=fake_clusters,
        labels=fake_labels,
        max_clusters=COLLAGE_SIZE,
        grid_cols=GRID_COLS,
        thumb_size=THUMB_SIZE,
        output_path=output_path,
    )

    # Verify output
    if collage_path.exists():
        # Get image dimensions
        with Image.open(collage_path) as img:
            width, height = img.size

        grid_rows = (len(fake_clusters) + GRID_COLS - 1) // GRID_COLS
        expected_width = GRID_COLS * THUMB_SIZE
        expected_height = grid_rows * THUMB_SIZE

        print(f"\n✅ Collage created successfully!")
        print(f"📊 Output: {collage_path}")
        print(f"📐 Dimensions: {width}x{height}px")
        print(f"   Expected: {expected_width}x{expected_height}px")
        print(f"   Grid: {GRID_COLS} columns × {grid_rows} rows")
        print(f"   Cell size: {THUMB_SIZE}x{THUMB_SIZE}px")

        # Calculate file size
        file_size_kb = collage_path.stat().st_size / 1024
        print(f"💾 File size: {file_size_kb:.1f} KB")

        print(f"\n🎉 Test passed! Open the collage to view:")
        print(f"   open {collage_path}")

    else:
        print(f"❌ Failed to create collage at {collage_path}")


if __name__ == "__main__":
    test_create_collage()
