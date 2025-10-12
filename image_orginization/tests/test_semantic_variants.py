"""Test semantic keyword rotation for SEO optimization."""

import json
import shutil
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.models import Item
from photo_organizer.organization import organize
from photo_organizer.config import SEMANTIC_KEYWORDS


def test_semantic_variants():
    """Test that semantic keywords rotate across images in a cluster."""

    print("\n" + "=" * 70)
    print("🎯 Testing Semantic Keyword Rotation")
    print("=" * 70)

    # Create temporary directory for test files
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create dummy image files
        test_images = []
        for i in range(1, 6):  # 5 images
            img_path = temp_dir / f"img_{i}.jpg"
            # Create a minimal valid JPEG file
            with open(img_path, "wb") as f:
                # Minimal JPEG header + footer
                f.write(
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
                )
            test_images.append(img_path)

        # Create mock items in a single cluster (5 images of stamped concrete driveways)
        mock_items = [
            Item(
                id=f"img_{i}",
                path=test_images[i - 1],
                dt="2024-01-15 10:00:00",
                h="abc123",
                thumb=test_images[i - 1],  # Using same file as thumb for simplicity
                gps=None,  # No GPS - will use fallback city
            )
            for i in range(1, 6)
        ]

        # Mock AI classification - all same label
        mock_labels = {
            f"img_{i}": {
                "label": "stamped-concrete-driveway",
                "descriptor": "Beautiful stamped concrete driveway with stone pattern",
                "confidence": 0.95,
            }
            for i in range(1, 6)
        }

        # Create output directory
        out_dir = Path(__file__).parent / "test_semantic_output"
        out_dir.mkdir(exist_ok=True)

        # Show expected behavior
        print("\nLabel: stamped-concrete-driveway")
        print("\nSemantic variants available:")
        variants = SEMANTIC_KEYWORDS["stamped-concrete-driveway"]
        for i, v in enumerate(variants, 1):
            print(f"  {i}. {v}")

        print(
            f"\n📸 Expected rotation pattern ({len(mock_items)} images, {len(variants)} variants):"
        )
        print("   (Using fixed city 'puyallup' - no rotation)\n")
        for idx in range(1, len(mock_items) + 1):
            variant_idx = (idx - 1) % len(variants)
            keyword = variants[variant_idx]
            print(f"  Image {idx} → {keyword}-puyallup-rc-concrete-{idx:02d}.jpg")

        # Organize with semantic rotation
        groups = [mock_items]  # Single cluster

        print("\n" + "-" * 70)
        print("Running organize()...")
        print("-" * 70 + "\n")

        organize(
            groups=groups,
            labels=mock_labels,
            out_dir=out_dir,
            brand="rc-concrete",
            rotate_cities=False,  # Use fixed city for predictable, consistent results
            use_semantic_keywords=True,  # Enable semantic rotation
        )

        # Validate results
        manifest_path = out_dir / "manifest.json"
        assert manifest_path.exists(), "manifest.json should be created"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        print("\n" + "=" * 70)
        print("✅ VALIDATION RESULTS")
        print("=" * 70)

        # Check that files were created
        assert len(manifest) == 5, f"Expected 5 files, got {len(manifest)}"
        print(f"✓ Created {len(manifest)} organized files")

        # Extract semantic keywords used
        keywords_used = [entry["semantic_keyword"] for entry in manifest]
        unique_keywords = set(keywords_used)

        print(f"✓ Semantic keywords used: {len(unique_keywords)} unique")
        for kw in unique_keywords:
            count = keywords_used.count(kw)
            print(f"  - {kw}: {count}x")

        # Verify rotation pattern
        print("\n📋 Actual filename rotation:")
        for i, entry in enumerate(manifest, 1):
            filename = Path(entry["dst"]).name
            keyword = entry["semantic_keyword"]
            expected_variant_idx = (i - 1) % len(variants)
            expected_keyword = variants[expected_variant_idx]

            match = "✓" if keyword == expected_keyword else "✗"
            print(f"  {match} Image {i}: {filename}")
            print(f"    └─ Keyword: {keyword}")

            # Assert correct rotation
            assert (
                keyword == expected_keyword
            ), f"Image {i} should use variant '{expected_keyword}', got '{keyword}'"

        # Verify multiple keywords were used (not just one repeated)
        assert (
            len(unique_keywords) > 1
        ), f"Should use multiple semantic variants, only used: {unique_keywords}"
        print(f"\n✅ Semantic rotation working correctly!")
        print(
            f"   Used {len(unique_keywords)} different keywords across {len(manifest)} images"
        )

        # Show folder structure
        folders = set(Path(entry["dst"]).parent.name for entry in manifest)
        print(f"\n📁 Folder structure:")
        for folder in folders:
            files = [
                Path(e["dst"]).name
                for e in manifest
                if Path(e["dst"]).parent.name == folder
            ]
            print(f"  {folder}/")
            for file in files[:3]:  # Show first 3
                print(f"    - {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")

        print("\n" + "=" * 70)
        print("🎉 TEST PASSED - Semantic keyword rotation is working!")
        print("=" * 70)
        print("\n💡 SEO Benefits:")
        print("   • Targets multiple high-value search terms")
        print("   • Looks natural (not keyword stuffing)")
        print("   • Improves discoverability across related queries")
        print("=" * 70 + "\n")

    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_no_semantic_variants():
    """Test that disabling semantic keywords uses only primary label."""

    print("\n" + "=" * 70)
    print("🎯 Testing WITHOUT Semantic Keyword Rotation")
    print("=" * 70)

    # Create temporary directory for test files
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Create dummy image files
        test_images = []
        for i in range(1, 4):  # 3 images
            img_path = temp_dir / f"img_{i}.jpg"
            # Create a minimal valid JPEG file
            with open(img_path, "wb") as f:
                f.write(
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
                )
            test_images.append(img_path)

        # Create mock items in a single cluster
        mock_items = [
            Item(
                id=f"img_{i}",
                path=test_images[i - 1],
                dt="2024-01-15 10:00:00",
                h="abc123",
                thumb=test_images[i - 1],
                gps=None,
            )
            for i in range(1, 4)
        ]

        # Mock AI classification
        mock_labels = {
            f"img_{i}": {
                "label": "stamped-concrete-driveway",
                "descriptor": "Stamped concrete driveway",
                "confidence": 0.95,
            }
            for i in range(1, 4)
        }

        # Create output directory
        out_dir = Path(__file__).parent / "test_no_semantic_output"
        out_dir.mkdir(exist_ok=True)

        print("\nLabel: stamped-concrete-driveway")
        print("\n📸 Expected behavior (3 images, NO semantic rotation):")
        print("   All images use the SAME primary label\n")

        for idx in range(1, 4):
            print(
                f"  Image {idx} → stamped-concrete-driveway-puyallup-rc-concrete-{idx:02d}.jpg"
            )

        # Organize WITHOUT semantic rotation
        groups = [mock_items]

        print("\n" + "-" * 70)
        print("Running organize() with use_semantic_keywords=False...")
        print("-" * 70 + "\n")

        organize(
            groups=groups,
            labels=mock_labels,
            out_dir=out_dir,
            brand="rc-concrete",
            rotate_cities=False,
            use_semantic_keywords=False,  # DISABLE semantic rotation
        )

        # Validate results
        manifest_path = out_dir / "manifest.json"
        assert manifest_path.exists(), "manifest.json should be created"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        print("\n" + "=" * 70)
        print("✅ VALIDATION RESULTS")
        print("=" * 70)

        # Check that files were created
        assert len(manifest) == 3, f"Expected 3 files, got {len(manifest)}"
        print(f"✓ Created {len(manifest)} organized files")

        # Extract semantic keywords used
        keywords_used = [entry["semantic_keyword"] for entry in manifest]
        unique_keywords = set(keywords_used)

        print(f"✓ Keywords used: {len(unique_keywords)} unique")
        for kw in unique_keywords:
            count = keywords_used.count(kw)
            print(f"  - {kw}: {count}x")

        # Verify ALL use the same primary label (no rotation)
        print("\n📋 Actual filename pattern:")
        for i, entry in enumerate(manifest, 1):
            filename = Path(entry["dst"]).name
            keyword = entry["semantic_keyword"]

            match = "✓" if keyword == "stamped-concrete-driveway" else "✗"
            print(f"  {match} Image {i}: {filename}")
            print(f"    └─ Keyword: {keyword}")

            # Assert all use primary label
            assert (
                keyword == "stamped-concrete-driveway"
            ), f"Image {i} should use primary label 'stamped-concrete-driveway', got '{keyword}'"

        # Verify only ONE keyword was used
        assert (
            len(unique_keywords) == 1
        ), f"Should use only 1 keyword (primary label), used: {unique_keywords}"
        assert (
            "stamped-concrete-driveway" in unique_keywords
        ), f"Should use primary label, got: {unique_keywords}"

        print(f"\n✅ No semantic rotation - all images use primary label!")
        print(
            f"   Used '{list(unique_keywords)[0]}' consistently across all {len(manifest)} images"
        )

        print("\n" + "=" * 70)
        print("🎉 TEST PASSED - Non-semantic mode working correctly!")
        print("=" * 70)
        print("\n💡 Use Case:")
        print("   • Use --no-semantic-keywords for consistent branding")
        print("   • Good when you prefer uniformity over SEO diversity")
        print("=" * 70 + "\n")

    finally:
        # Cleanup temporary files
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "🧪 Running Semantic Keyword Tests ".center(70, "="))
    print()

    # Test 1: WITH semantic rotation
    test_semantic_variants()

    # Test 2: WITHOUT semantic rotation
    test_no_semantic_variants()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70 + "\n")
