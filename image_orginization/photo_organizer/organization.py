"""Photo organization and renaming logic."""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from slugify import slugify
from .models import Item
from .config import (
    CITIES,
    GENERIC_PRIMARIES,
    SURFACE_NOUNS,
    SURFACE_MAP,
    SEMANTIC_KEYWORDS,
    USE_SEMANTIC_KEYWORDS,
)
from .utils.geo import nearest_city


def extract_surface_from_descriptor(descriptor: str, label_words: set) -> str:
    """Extract surface noun from AI descriptor, avoiding words already in label.

    Args:
        descriptor: AI-generated description (e.g., "patio with stamped pattern")
        label_words: Set of words already in the primary label

    Returns:
        Surface noun if found and not redundant, else empty string
    """
    if not descriptor:
        return ""

    descriptor_lower = descriptor.lower()

    # Check for surface nouns in the descriptor
    for surface in SURFACE_NOUNS:
        # Only use if:
        # 1. Surface word appears in descriptor
        # 2. Surface word is NOT already in the label
        if surface in descriptor_lower and surface not in label_words:
            return surface

    return ""


def organize(
    groups: List[List[Item]],
    labels: Dict[str, Dict],
    out_dir: Path,
    brand: str,
    rotate_cities: bool,
    use_semantic_keywords: bool = USE_SEMANTIC_KEYWORDS,
):
    """Organize photos into folders with SEO-friendly filenames.

    Creates folder structure: {label}-{city}/
    Creates filenames: {keyword}[-{surface}]-{city}-{brand}-{index}.jpg

    Args:
        groups: List of photo clusters
        labels: Dictionary mapping item IDs to classification results
        out_dir: Output directory for organized photos
        brand: Brand name for filenames
        rotate_cities: Whether to rotate cities for photos without GPS
        use_semantic_keywords: Whether to rotate through semantic keyword variants

    This format is optimized for SEO with keyword-first naming.
    When use_semantic_keywords=True, cycles through related terms for broad coverage.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cycle = list(CITIES.keys())

    manifest = []

    for gi, grp in enumerate(groups, start=1):
        # Get classification label (majority vote)
        votes: Dict[str, int] = {}
        for it in grp:
            lab = labels.get(it.id, {}).get("label", "unknown")
            votes[lab] = votes.get(lab, 0) + 1

        label = max(votes, key=votes.get) if votes else "unknown"

        # Determine city
        gps_any = next((it.gps for it in grp if it.gps), None)
        city = nearest_city(
            gps_any,
            cycle if rotate_cities else CITIES,
            gi - 1,
        )

        # Smart disambiguation: Add surface noun only for generic primaries
        # Check if primary is generic and needs a surface noun
        surface = None
        if label in GENERIC_PRIMARIES:
            label_words = set(label.split("-"))

            # Try to extract surface from AI descriptors in this group
            for it in grp:
                item_labels = labels.get(it.id, {})
                descriptor = item_labels.get("descriptor", "")

                if descriptor:
                    surface = extract_surface_from_descriptor(descriptor, label_words)
                    if surface:
                        break  # Found a surface noun

            # Fallback to SURFACE_MAP if configured
            if not surface:
                surface_candidate = SURFACE_MAP.get(label, "")
                if surface_candidate and surface_candidate not in label_words:
                    surface = surface_candidate

        # Build folder name
        if surface:
            # Generic primary + surface: decorative-concrete-steps-bellevue
            folder_name = f"{slugify(label, lowercase=True)}-{slugify(surface, lowercase=True)}-{slugify(city, lowercase=True)}"
        else:
            # Specific primary (no surface): stamped-concrete-driveway-bellevue
            folder_name = (
                f"{slugify(label, lowercase=True)}-{slugify(city, lowercase=True)}"
            )

        folder = out_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        # Get semantic keyword variants for this label (if enabled)
        if use_semantic_keywords:
            semantic_variants = SEMANTIC_KEYWORDS.get(label, [label])
            if not semantic_variants:
                semantic_variants = [label]
        else:
            # Use only the primary label
            semantic_variants = [label]

        # Process each photo in the group
        for idx, it in enumerate(grp, start=1):
            # Rotate through semantic variants for SEO diversity (if enabled)
            # Image 1 uses variant 0, Image 2 uses variant 1, etc.
            variant_idx = (idx - 1) % len(semantic_variants)
            current_keyword = semantic_variants[variant_idx]

            # Build filename: {keyword}[-{surface}]-{city}-{brand}-{index}
            # Example: stamped-concrete-driveway-bellevue-rc-concrete-01.jpg
            # Example: imprinted-concrete-driveway-bellevue-rc-concrete-02.jpg (semantic variant)
            # Example: decorative-concrete-steps-bellevue-rc-concrete-01.jpg
            parts = []

            # Add keyword (primary or semantic variant)
            parts.append(slugify(current_keyword, lowercase=True))

            # Add surface only if needed (generic primary)
            if surface:
                parts.append(slugify(surface, lowercase=True))

            # Add city
            parts.append(slugify(city, lowercase=True))

            # Add brand
            if brand:
                parts.append(slugify(brand, lowercase=True))

            # Add index
            parts.append(f"{idx:02d}")

            base = "-".join(parts)
            ext = it.path.suffix.lower()

            # Convert HEIC/HEIF to JPG extension
            if ext in {".heic", ".heif"}:
                ext = ".jpg"

            dst = folder / f"{base}{ext}"

            try:
                shutil.copy2(it.path, dst)
            except Exception as e:
                print(f"[warn] copy failed {it.path.name}: {e}")
                continue

            manifest.append(
                {
                    "src": str(it.path),
                    "dst": str(dst),
                    "cluster": gi,
                    "label": label,
                    "semantic_keyword": current_keyword,
                    "city": city,
                    "index": idx,
                }
            )

    # Write manifest
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Organized {len(manifest)} files into {len(groups)} folders")
    print(f"📄 Manifest: {out_dir/'manifest.json'}")
