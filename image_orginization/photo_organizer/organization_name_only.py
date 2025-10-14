"""Photo organization for name-only mode with SEO-optimized filenames.

This module handles the final organization step for name-only mode:
- Takes AI-generated SEO filenames
- Adds location (city) and brand to each filename
- Handles duplicate filenames (adds numbers at end only when needed)
- Groups small clusters (≤2 images) into single misc folder
- Creates individual folders for larger clusters
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from slugify import slugify

from .models import Item
from .config import CITIES
from .utils.geo import nearest_city


def organize_name_only(
    groups: List[List[Item]],
    labels: Dict[str, Dict],
    out_dir: Path,
    brand: str,
    rotate_cities: bool,
):
    """Organize photos using SEO-optimized filenames from AI.

    Process:
    1. Separate small clusters (≤2) from large clusters (>2)
    2. For each image, build filename: {ai-name}-{city}-{brand}.jpg
    3. Handle duplicates by adding numbers at end: {ai-name}-{city}-{brand}-02.jpg
    4. Large clusters: Each gets its own folder
    5. Small clusters: ALL go into one misc-concrete-{city} folder per city

    Args:
        groups: List of clusters (each cluster is a list of Items)
        labels: Dict mapping item IDs to {"seo_filename": str, ...}
        out_dir: Output directory for organized photos
        brand: Brand name to add to filenames
        rotate_cities: Whether to rotate cities if no GPS
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cycle = list(CITIES.keys())

    manifest = []

    # Separate small and large clusters
    large_clusters = [grp for grp in groups if len(grp) > 2]
    small_clusters = [grp for grp in groups if len(grp) <= 2]

    print(f"\n📁 Organizing photos with SEO filenames...")
    print(f"   Large clusters (>2 images): {len(large_clusters)}")
    print(f"   Small clusters (≤2 images): {len(small_clusters)}")

    # Track used filenames per folder for duplicate detection
    folder_filenames: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Process large clusters (each gets its own folder)
    for gi, grp in enumerate(large_clusters, start=1):
        # Determine city for this cluster
        gps_any = next((it.gps for it in grp if it.gps), None)
        city = nearest_city(
            gps_any,
            cycle if rotate_cities else CITIES,
            gi - 1,
        )

        # Create folder name (generic cluster-based)
        folder_name = f"cluster-{gi}-{slugify(city, lowercase=True)}"
        folder = out_dir / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        print(f"\n  📂 {folder_name}/ ({len(grp)} images)")

        # Process each image in the cluster
        for it in grp:
            # Get AI-generated SEO filename
            seo_filename = labels.get(it.id, {}).get("seo_filename", "concrete-photo")

            # Build final filename: {seo-name}-{city}-{brand}
            parts = [seo_filename]
            parts.append(slugify(city, lowercase=True))
            if brand:
                parts.append(slugify(brand, lowercase=True))

            base = "-".join(parts)

            # Handle duplicates: add number at end if needed
            if folder_filenames[folder_name][base] > 0:
                # Duplicate found, add number
                counter = folder_filenames[folder_name][base] + 1
                final_base = f"{base}-{counter:02d}"
                folder_filenames[folder_name][base] = counter
            else:
                final_base = base
                folder_filenames[folder_name][base] = 1

            # Get file extension
            ext = it.path.suffix.lower()
            if ext in {".heic", ".heif"}:
                ext = ".jpg"

            dst = folder / f"{final_base}{ext}"

            # Copy file
            try:
                shutil.copy2(it.path, dst)
                print(f"     ✓ {dst.name}")
            except Exception as e:
                print(f"     ✗ Failed to copy {it.path.name}: {e}")
                continue

            manifest.append(
                {
                    "src": str(it.path),
                    "dst": str(dst),
                    "cluster": gi,
                    "seo_filename": seo_filename,
                    "city": city,
                    "folder": folder_name,
                }
            )

    # Process small clusters - group ALL by city into misc folders
    if small_clusters:
        print(
            f"\n📦 Grouping {len(small_clusters)} small clusters into misc folders..."
        )

        # Group all small cluster items by city
        small_items_by_city: Dict[str, List[Item]] = defaultdict(list)

        for grp in small_clusters:
            for it in grp:
                gps_any = it.gps
                city = nearest_city(gps_any, cycle if rotate_cities else CITIES, 0)
                small_items_by_city[city].append(it)

        # Create one misc folder per city
        for city, items in small_items_by_city.items():
            folder_name = f"misc-concrete-{slugify(city, lowercase=True)}"
            folder = out_dir / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            print(f"\n  📂 {folder_name}/ ({len(items)} images)")

            # Process each image
            for it in items:
                # Get AI-generated SEO filename
                seo_filename = labels.get(it.id, {}).get(
                    "seo_filename", "concrete-photo"
                )

                # Build final filename: {seo-name}-{city}-{brand}
                parts = [seo_filename]
                parts.append(slugify(city, lowercase=True))
                if brand:
                    parts.append(slugify(brand, lowercase=True))

                base = "-".join(parts)

                # Handle duplicates
                if folder_filenames[folder_name][base] > 0:
                    counter = folder_filenames[folder_name][base] + 1
                    final_base = f"{base}-{counter:02d}"
                    folder_filenames[folder_name][base] = counter
                else:
                    final_base = base
                    folder_filenames[folder_name][base] = 1

                # Get file extension
                ext = it.path.suffix.lower()
                if ext in {".heic", ".heif"}:
                    ext = ".jpg"

                dst = folder / f"{final_base}{ext}"

                # Copy file
                try:
                    shutil.copy2(it.path, dst)
                    print(f"     ✓ {dst.name}")
                except Exception as e:
                    print(f"     ✗ Failed to copy {it.path.name}: {e}")
                    continue

                manifest.append(
                    {
                        "src": str(it.path),
                        "dst": str(dst),
                        "cluster": "small",
                        "seo_filename": seo_filename,
                        "city": city,
                        "folder": folder_name,
                    }
                )

    # Write manifest
    manifest_path = out_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Summary
    total_folders = len(large_clusters)
    if small_clusters:
        total_folders += len(small_items_by_city)

    print(f"\n✅ Organized {len(manifest)} files into {total_folders} folders")
    print(f"   - {len(large_clusters)} multi-image cluster folders")
    if small_clusters:
        print(
            f"   - {len(small_items_by_city)} misc-concrete-{{city}} folders ({len(small_clusters)} small clusters)"
        )
    print(f"📄 Manifest: {manifest_path}")
