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
    """
    Gets the cluster label from AI classification
    Loads semantic variants from SEMANTIC_KEYWORDS config
    Loops through each photo in the cluster
    Rotates through semantic variants: variant_idx = (idx - 1) % len(semantic_variants)
    Builds filename: {keyword}[-{surface}]-{city}-{brand}-{index}.jpg
    Copies files and creates manifest
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cycle = list(CITIES.keys())

    manifest = []

    # Separate multi-image clusters from singletons
    multi_clusters = [grp for grp in groups if len(grp) > 1]
    singleton_clusters = [grp for grp in groups if len(grp) == 1]

    print(
        f"\n📁 Organizing {len(multi_clusters)} multi-image clusters into individual folders..."
    )
    print(
        f"📁 Grouping {len(singleton_clusters)} singletons into misc folders by city..."
    )

    # Process multi-image clusters (each gets its own folder)
    for gi, grp in enumerate(multi_clusters, start=1):
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

    # Process singletons - group by city into misc folders
    if singleton_clusters:
        # Group singletons by city
        singletons_by_city: Dict[str, List[Item]] = {}
        for grp in singleton_clusters:
            it = grp[0]  # Only one item per singleton cluster
            gps_any = it.gps
            city = nearest_city(gps_any, cycle if rotate_cities else CITIES, 0)
            if city not in singletons_by_city:
                singletons_by_city[city] = []
            singletons_by_city[city].append(it)

        # Create one misc folder per city
        for city, items in singletons_by_city.items():
            folder_name = f"misc-concrete-{slugify(city, lowercase=True)}"
            folder = out_dir / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            print(f"  📦 Grouping {len(items)} singletons in {folder_name}/")

            # Process each singleton
            for idx, it in enumerate(items, start=1):
                # Get classification label for SEO filename
                label = labels.get(it.id, {}).get("label", "unknown")
                descriptor = labels.get(it.id, {}).get("descriptor", "")

                # Get semantic keyword variants (if enabled)
                if use_semantic_keywords:
                    semantic_variants = SEMANTIC_KEYWORDS.get(label, [label])
                    if not semantic_variants:
                        semantic_variants = [label]
                else:
                    semantic_variants = [label]

                # Rotate through semantic variants
                variant_idx = (idx - 1) % len(semantic_variants)
                current_keyword = semantic_variants[variant_idx]

                # Build filename: {keyword}-{city}-{brand}-{index}
                parts = []
                parts.append(slugify(current_keyword, lowercase=True))
                parts.append(slugify(city, lowercase=True))

                if brand:
                    parts.append(slugify(brand, lowercase=True))

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
                        "cluster": "singleton",
                        "label": label,
                        "semantic_keyword": current_keyword,
                        "city": city,
                        "index": idx,
                    }
                )

    # Write manifest
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_folders = (
        len(multi_clusters) + len(singletons_by_city)
        if singleton_clusters
        else len(multi_clusters)
    )
    print(f"\n✅ Organized {len(manifest)} files into {total_folders} folders")
    print(f"   - {len(multi_clusters)} multi-image project folders")
    if singleton_clusters:
        print(
            f"   - {len(singletons_by_city)} misc-concrete-{{city}} folders with {len(singleton_clusters)} singletons"
        )
    print(f"📄 Manifest: {out_dir/'manifest.json'}")
