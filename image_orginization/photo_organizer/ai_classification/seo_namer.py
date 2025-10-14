"""SEO-optimized image naming using AI vision models.

This module provides AI-powered filename generation for construction photos,
optimized for local SERP ranking. Each image gets a unique, descriptive filename
that naturally incorporates target SEO keywords.
"""

import base64
import time
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image

from ..config import LABELS, API_RATE_LIMIT_DELAY, MAX_RETRIES, RETRY_DELAY
from ..models import Item

try:
    from openai import OpenAI

    client = OpenAI()
except ImportError:
    OpenAI = None
    client = None


def create_seo_naming_prompt(target_keywords: List[str]) -> List[Dict]:
    """Create the AI prompt for SEO-optimized filename generation.

    Args:
        target_keywords: List of target SEO keywords from LABELS config

    Returns:
        List of message dicts for OpenAI API
    """
    keywords_list = ", ".join(target_keywords[:30])  # Show first 30 keywords

    return [
        {
            "role": "system",
            "content": (
                "You are an SEO specialist who optimizes concrete construction photos for local search rankings (SERP). "
                "Your job is to create unique, descriptive filenames for each image that will help them rank in Google Images "
                "and local search results.\n\n"
                "TARGET KEYWORDS (try to naturally incorporate these):\n"
                f"{keywords_list}\n\n"
                "FILENAME FORMAT:\n"
                "- Use format: <primary-keyword>-<surface/identifiers>.jpg\n"
                "- Examples:\n"
                "  * stamped-concrete-driveway.jpg\n"
                "  * imprinted-concrete-driveway.jpg\n"
                "  * decorative-concrete-steps.jpg\n"
                "  * custom-concrete-logo-stained-overlay.jpg\n"
                "  * decorative-concrete-celtic-cross-inlay.jpg\n"
                "  * stamped-patio-decorative-border-curves.jpg\n"
                "  * exposed-aggregate-walkway-modern-design.jpg\n"
                "  * concrete-driveway-broom-finish-new-pour.jpg\n\n"
                "RULES:\n"
                "1. Each image gets a UNIQUE filename (no duplicates)\n"
                "2. Use target keywords when they match the image content\n"
                "3. You CAN create better keywords if target list doesn't fit\n"
                "4. Be specific about what's in the photo (surface, finish, features)\n"
                "5. Use hyphens between words (kebab-case)\n"
                "6. Keep filenames concise but descriptive (3-6 words)\n"
                "7. Focus on what makes each image unique\n"
                "8. DO NOT include numbers, dates, or location names\n"
                "9. DO NOT include file extensions in your response\n\n"
                "CLASSIFY THE WORK:\n"
                "- Identify the concrete type (driveway, patio, walkway, steps, etc.)\n"
                "- Note the surface finish (stamped, exposed-aggregate, broom, smooth, etc.)\n"
                "- Mention unique features (curves, borders, patterns, logos, inlays, etc.)\n"
                "- Describe the style (modern, decorative, custom, residential, etc.)\n\n"
                "Your goal: Create SEO-friendly filenames that accurately describe each image "
                "while naturally incorporating relevant keywords for local search ranking."
            ),
        },
        {
            "role": "user",
            "content": (
                "TASK: Generate a unique SEO-optimized filename for EACH numbered image in the collage.\n\n"
                "OUTPUT FORMAT (one per line):\n"
                "0 — filename-without-extension\n"
                "1 — another-unique-filename\n"
                "2 — third-descriptive-filename\n"
                "...\n\n"
                "IMPORTANT:\n"
                "- Match the number to the image position in the collage\n"
                "- Each filename must be unique and descriptive\n"
                "- Use hyphens between words (kebab-case)\n"
                "- DO NOT include .jpg or any extension\n"
                "- DO NOT include location or brand names\n"
                "- Focus on the work type, surface, and unique features"
            ),
        },
    ]


def encode_image_to_base64(image_path: Path) -> str:
    """Encode image to base64 for OpenAI API.

    Args:
        image_path: Path to image file

    Returns:
        Base64-encoded image string
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_openai_for_naming(
    collage_path: Path,
    num_images: int,
    model: str = "gpt-4o",
) -> Dict[int, str]:
    """Call OpenAI API to generate SEO filenames for images in a collage.

    Args:
        collage_path: Path to collage image
        num_images: Number of images in the collage
        model: OpenAI model to use

    Returns:
        Dict mapping image index (0-based) to filename (without extension)
    """
    if OpenAI is None or client is None:
        print("[warn] openai package not installed, returning placeholder names")
        return {i: f"concrete-photo-{i}" for i in range(num_images)}

    # Encode collage image
    image_base64 = encode_image_to_base64(collage_path)

    # Build messages
    messages = create_seo_naming_prompt(LABELS)
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": f"Generate unique SEO-optimized filenames for all {num_images} images in this collage.",
                },
            ],
        }
    )

    # Call API with retries
    for attempt in range(MAX_RETRIES):
        try:
            print(f"🤖 Calling OpenAI API for {num_images} filenames...")

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,  # Some creativity for unique names
            )

            # Parse response
            content = response.choices[0].message.content
            filenames = parse_naming_response(content, num_images)

            if len(filenames) == num_images:
                print(f"✅ Received {len(filenames)} unique filenames")
                return filenames
            else:
                print(f"⚠️  Expected {num_images} filenames, got {len(filenames)}")
                # Fill in missing with placeholders
                for i in range(num_images):
                    if i not in filenames:
                        filenames[i] = f"concrete-photo-{i}"
                return filenames

        except Exception as e:
            print(f"❌ API call failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"   Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print("   Max retries reached, using placeholder names")
                return {i: f"concrete-photo-{i}" for i in range(num_images)}

    # Fallback
    return {i: f"concrete-photo-{i}" for i in range(num_images)}


def parse_naming_response(response_text: str, expected_count: int) -> Dict[int, str]:
    """Parse AI response to extract numbered filenames.

    Expected format:
        0 — custom-concrete-logo-stained
        1 — decorative-concrete-celtic-cross
        2 — exposed-aggregate-walkway

    Args:
        response_text: Raw AI response text
        expected_count: Expected number of filenames

    Returns:
        Dict mapping index to filename (without extension)
    """
    filenames = {}

    for line in response_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        # Try to parse "0 — filename" or "0: filename" or "0. filename"
        for separator in ["—", ":", ".", "-"]:
            if separator in line:
                parts = line.split(separator, 1)
                if len(parts) == 2:
                    try:
                        idx = int(parts[0].strip())
                        filename = parts[1].strip()

                        # Clean up filename
                        filename = filename.lower()
                        filename = filename.replace(" ", "-")
                        filename = filename.replace("_", "-")
                        # Remove any file extensions
                        for ext in [".jpg", ".jpeg", ".png", ".heic"]:
                            filename = filename.replace(ext, "")

                        # Remove any leading/trailing hyphens
                        filename = filename.strip("-")

                        if filename and idx >= 0 and idx < expected_count:
                            filenames[idx] = filename
                            break
                    except (ValueError, IndexError):
                        continue

    return filenames


def generate_seo_filenames_for_all_images(
    all_items: List[Item],
    collage_dir: Path,
    images_per_collage: int = 50,
    model: str = "gpt-4o",
) -> Dict[str, str]:
    """Generate SEO-optimized filenames for all images using collages.

    This is the main entry point for name-only mode. It:
    1. Creates collages of all images (50 per collage)
    2. Sends each collage to AI for filename generation
    3. Maps filenames back to original images

    Args:
        all_items: List of ALL items from ALL clusters (flattened)
        collage_dir: Directory to save collages
        images_per_collage: Images per collage (default: 50)
        model: OpenAI model to use

    Returns:
        Dict mapping item.id to SEO filename (without extension)
    """
    from ..utils.collage import create_cluster_collage

    print(f"\n🎨 Creating collages for {len(all_items)} images...")
    print(f"   {images_per_collage} images per collage")

    collage_dir.mkdir(parents=True, exist_ok=True)

    # Calculate number of collages needed
    num_collages = (len(all_items) + images_per_collage - 1) // images_per_collage
    print(f"   Will create {num_collages} collage(s)")

    all_filenames: Dict[str, str] = {}

    # Create and process each collage
    for collage_idx in range(num_collages):
        start_idx = collage_idx * images_per_collage
        end_idx = min(start_idx + images_per_collage, len(all_items))
        batch_items = all_items[start_idx:end_idx]

        print(
            f"\n📸 Collage {collage_idx + 1}/{num_collages}: images {start_idx}-{end_idx - 1}"
        )

        # Create collage (wrap each item in a list to match expected format)
        collage_path = collage_dir / f"batch_{collage_idx + 1}_of_{num_collages}.jpg"
        create_cluster_collage(
            clusters=[[item] for item in batch_items],
            labels=None,
            max_clusters=len(batch_items),
            grid_cols=10,
            thumb_size=256,
            output_path=collage_path,
        )

        print(f"   Saved collage: {collage_path.name}")

        # Get filenames from AI
        filenames = call_openai_for_naming(
            collage_path,
            num_images=len(batch_items),
            model=model,
        )

        # Map filenames back to items
        for local_idx, item in enumerate(batch_items):
            if local_idx in filenames:
                all_filenames[item.id] = filenames[local_idx]
                print(f"      {local_idx} → {filenames[local_idx]}")
            else:
                # Fallback
                all_filenames[item.id] = f"concrete-photo-{start_idx + local_idx}"

        # Rate limiting
        if collage_idx < num_collages - 1 and API_RATE_LIMIT_DELAY > 0:
            time.sleep(API_RATE_LIMIT_DELAY)

    print(f"\n✅ Generated {len(all_filenames)} unique SEO filenames")

    return all_filenames
