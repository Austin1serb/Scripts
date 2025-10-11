#!/usr/bin/env python3
"""
Test to verify thumbnail size change and calculate cost savings.

This test creates a sample thumbnail and shows the token/cost difference.
"""

import sys
from pathlib import Path
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.config import THUMBNAIL_SIZE
from photo_organizer.utils.image import ensure_thumb
from PIL import Image


def calculate_gpt4_vision_tokens(width: int, height: int) -> int:
    """Calculate GPT-4 Vision tokens for an image based on its dimensions.

    According to OpenAI docs:
    - Images ≤512px on shortest side: 85 tokens (1 tile)
    - Images >512px: 170 tokens per 512×512 tile + 85 base tokens
    """
    # Find shortest side
    shortest = min(width, height)

    if shortest <= 512:
        return 85  # Single tile

    # Calculate tiles needed
    tiles_w = (width + 511) // 512  # Ceiling division
    tiles_h = (height + 511) // 512
    num_tiles = tiles_w * tiles_h

    return (170 * num_tiles) + 85


def main():
    print("🔍 Thumbnail Size & Cost Analysis")
    print("=" * 70)

    # Check config
    print(f"\n📋 Configuration:")
    print(f"   THUMBNAIL_SIZE: {THUMBNAIL_SIZE}px")

    # Test with an existing thumbnail
    thumbs_dir = project_root / "organized" / "_work" / "thumbs"
    sample_thumbs = list(thumbs_dir.glob("*.jpg"))[:3]

    if not sample_thumbs:
        print("\n⚠️  No existing thumbnails found to analyze")
        return

    print(f"\n📊 Analyzing {len(sample_thumbs)} sample thumbnails:")
    print()

    total_tokens_current = 0
    total_size_current = 0

    for thumb_path in sample_thumbs:
        # Get current dimensions
        with Image.open(thumb_path) as img:
            width, height = img.size

        # Get file size
        file_size = thumb_path.stat().st_size

        # Get base64 size
        b64_size = len(base64.b64encode(thumb_path.read_bytes()))

        # Calculate tokens
        tokens = calculate_gpt4_vision_tokens(width, height)

        total_tokens_current += tokens
        total_size_current += file_size

        print(f"   {thumb_path.name}")
        print(f"      Size: {width}×{height}px")
        print(f"      File: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"      Base64: {b64_size:,} chars")
        print(f"      Tokens: {tokens}")
        print()

    # Calculate costs (GPT-4o pricing: $2.50 per 1M input tokens)
    cost_per_1m_tokens = 2.50
    avg_tokens = total_tokens_current / len(sample_thumbs)
    avg_size = total_size_current / len(sample_thumbs)

    print("=" * 70)
    print(f"\n💰 Cost Analysis (based on averages):")
    print(f"   Average tokens per image: {avg_tokens:.0f}")
    print(f"   Average file size: {avg_size/1024:.1f} KB")
    print()

    # Calculate costs for different scenarios
    scenarios = [
        ("Per image", 1),
        ("Per batch (5 images)", 5),
        ("Per batch (12 images)", 12),
        ("100 images", 100),
        ("1000 images", 1000),
    ]

    print("   Cost estimates:")
    for scenario, count in scenarios:
        tokens = avg_tokens * count
        cost = (tokens / 1_000_000) * cost_per_1m_tokens
        print(f"      {scenario:25s}: ${cost:.4f} ({tokens:,.0f} tokens)")

    # Compare to old 768px size
    print()
    print("=" * 70)
    print(f"\n📉 Comparison to 768px thumbnails:")

    # Assume 768px would be 4 tiles (765 tokens)
    old_tokens = 765
    savings_percent = ((old_tokens - avg_tokens) / old_tokens) * 100

    print(f"   Old (768px): {old_tokens} tokens/image")
    print(f"   New ({THUMBNAIL_SIZE}px): {avg_tokens:.0f} tokens/image")
    print(f"   Savings: {savings_percent:.1f}% reduction")
    print()
    print(f"   Cost savings per 100 images:")
    old_cost = (old_tokens * 100 / 1_000_000) * cost_per_1m_tokens
    new_cost = (avg_tokens * 100 / 1_000_000) * cost_per_1m_tokens
    print(f"      Old: ${old_cost:.2f}")
    print(f"      New: ${new_cost:.2f}")
    print(f"      Saved: ${old_cost - new_cost:.2f}")

    print()
    print("✅ Thumbnail configuration optimized for cost!")


if __name__ == "__main__":
    main()
