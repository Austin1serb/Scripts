#!/usr/bin/env python3
"""
Test AI ai_classification using existing organized images.

This test loads images from the organized/_work directory and tests the AI ai_classification
with a limited number of requests (10) to validate the system is working correctly.

Usage:
    python tests/test_ai_classification.py

Results are saved to tests/output.json
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from photo_organizer.utils.loading_spinner import Spinner
import imagehash

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from photo_organizer.models import Item
from photo_organizer.ai_classification.openai_classifier import classify_batches, b64


BATCH_SIZE = 5
MAX_API_CALLS = 4  # Limit API calls for testing


def load_existing_images() -> List[Item]:
    """Load existing images from organized/_work directory.
    return a slugified version of the filename:

    <primary-intent>-<specific-surface>-<city?>-<short-hash>.jpg
    Naming pattern:
    <primary-intent>-<specific-surface>-<city?>-<short-hash>.jpg
    One primary keyword per image, concise, hyphenated, and under ~60 chars.

    """
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


def show_ai_request_details(items: List[Item]) -> None:
    """Show what will be sent to the AI."""
    print("🔍 AI Request Details:")
    print("=" * 60)

    # Show system prompt
    from photo_organizer.config import MESSAGES

    print("System Prompt:")
    print(f"  {MESSAGES[0]['content']}")
    print()

    # Show user prompt
    from photo_organizer.config import LABELS

    print("User Prompt:")
    print(f"  Allowed labels: {', '.join(LABELS)}]")
    print(
        "  For each image return id, label, confidence (0-1), and a short descriptor."
    )
    print()

    # Show images that will be sent
    print(f"Images to be sent ({len(items)} total):")
    for i, item in enumerate(items, 1):
        print(f"  {i}. ID: {item.id}")
        print(f"     Thumbnail: {item.thumb}")

        # Show base64 data preview (first 50 chars)
        try:
            b64_data = b64(item.thumb)
            print(f"     Base64 preview: {b64_data[:50]}...")
            print(f"     Base64 length: {len(b64_data)} characters")
        except Exception as e:
            print(f"     Base64 error: {e}")
        print()

    print("=" * 60)


def save_ai_request_payload(
    items: List[Item],
) -> None:
    """Save the complete AI request payload to a file for inspection."""
    from photo_organizer.config import LABELS

    # Build the complete request payload
    from photo_organizer.config import MESSAGES

    messages = MESSAGES.copy()

    # Add image data
    for item in items:
        try:
            b64_data = b64(item.thumb)
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"id={item.id}"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"},
                        },
                    ],
                }
            )
        except Exception as e:
            print(f"Warning: Could not encode {item.id}: {e}")

    # Save to file
    output_file = Path(__file__).parent / "ai_request_payload.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "model": "gpt-4o",
                "messages": messages,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "batch_classify_cluster",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "images": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "label": {"type": "string", "enum": LABELS},
                                            "confidence": {
                                                "type": "number",
                                                "minimum": 0,
                                                "maximum": 1,
                                            },
                                            "descriptor": {"type": "string"},
                                        },
                                        "required": [
                                            "id",
                                            "label",
                                            "confidence",
                                            "descriptor",
                                        ],
                                        "additionalProperties": False,
                                    },
                                }
                            },
                            "required": ["images"],
                            "additionalProperties": False,
                        },
                    },
                },
            },
            f,
            indent=2,
        )

    print(f"📁 Complete AI request payload saved to: {output_file}")
    print(f"\nThis shows exactly what will be sent to OpenAI API")


def test_ai_classification(
    max_images: int = 10,
) -> Dict[str, Any]:
    """Test AI ai_classification with limited number of images."""
    print(f"🤖 Testing AI Classification with {max_images} images")
    print("=" * 60)

    # Load existing images
    all_items = load_existing_images()

    if len(all_items) == 0:
        raise ValueError("No images found to test")

    # Limit to max_images for testing
    test_items = all_items[:max_images]

    # Further limit by max API calls to control costs
    max_items_by_api_calls = MAX_API_CALLS * BATCH_SIZE
    if len(test_items) > max_items_by_api_calls:
        test_items = test_items[:max_items_by_api_calls]
        print(f"Limited to {len(test_items)} images ({MAX_API_CALLS} API calls max)")
    print(f"Testing with {len(test_items)} images:")
    for i, item in enumerate(test_items, 1):
        print(f"  {i}. {item.id}")

    print("\n" + "=" * 60)

    # Show what will be sent to AI
    show_ai_request_details(test_items)

    # Save complete request payload for inspection
    save_ai_request_payload(test_items)

    # Test ai_classification
    try:
        spinner = Spinner("🤖 AI classifying images")
        spinner.start()

        results = classify_batches(
            items=test_items,
            batch_size=BATCH_SIZE,
            model="gpt-4o",
        )

        spinner.stop()

        print(f"✅ Classification completed successfully!")
        print(f"Results for {len(results)} images:")

        # Display results
        for item_id, result in results.items():
            print(
                f"  {item_id}: {result['label']} (confidence: {result['confidence']:.2f})"
            )
            if result.get("descriptor"):
                print(f"    Description: {result['descriptor']}")

        return {
            "status": "success",
            "total_images": len(test_items),
            "results": results,
            "test_images": [
                {"id": item.id, "thumb_path": str(item.thumb)} for item in test_items
            ],
        }

    except Exception as e:
        print(f"❌ Classification failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "total_images": len(test_items),
            "test_images": [
                {"id": item.id, "thumb_path": str(item.thumb)} for item in test_items
            ],
        }


def main():
    """Main test function."""
    print("🧪 AI Classification Test")
    print("=" * 60)

    # Check if .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. Make sure OPENAI_API_KEY is set.")
        print("   You can create .env file with: OPENAI_API_KEY=sk-your-key-here")

    # Run test
    try:
        results = test_ai_classification(max_images=10)

        # Save results
        output_file = Path(__file__).parent / "output.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📁 Results saved to: {output_file}")

        if results["status"] == "success":
            print("✅ Test completed successfully!")
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
            "results": {},
            "test_images": [],
        }

        output_file = Path(__file__).parent / "output.json"
        with open(output_file, "w") as f:
            json.dump(error_results, f, indent=2, default=str)

        print(f"📁 Error results saved to: {output_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
