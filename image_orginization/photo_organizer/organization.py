"""Photo organization and renaming logic."""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from slugify import slugify
from .models import Item
from .config import SURFACE_CANON, CITIES
from .utils.geo import nearest_city
from .utils.image import short_hash


def organize(
    groups: List[List[Item]],
    labels: Dict[str, Dict],
    out_dir: Path,
    brand: str,
    rotate_cities: bool,
):
    """Organize photos into folders with SEO-friendly filenames.

    For each cluster/group:
    1. Determines surface type by majority vote of classified labels
    2. Assigns city based on GPS or rotation
    3. Creates folder with date-surface-city naming
    4. Copies photos with SEO-optimized filenames
    5. Generates manifest.json with mapping

    Args:
        groups: List of photo clusters
        labels: Dictionary mapping item IDs to ai_classification results
        out_dir: Output directory for organized photos
        brand: Brand name slug to include in filenames
        rotate_cities: Whether to rotate cities if GPS is missing
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    cycle = list(CITIES.keys())

    manifest = []

    for gi, grp in enumerate(groups, start=1):
        # Pick surface by majority vote over classified labels
        votes: Dict[str, int] = {}
        for it in grp:
            lab = labels.get(it.id, {}).get("label", "unknown")
            votes[lab] = votes.get(lab, 0) + 1

        label = max(votes, key=votes.get) if votes else "unknown"
        primary, surface = SURFACE_CANON.get(
            label, SURFACE_CANON["unknown"]
        )  # canonicalize

        # Determine city
        gps_any = next((it.gps for it in grp if it.gps), None)
        city = nearest_city(
            gps_any,
            cycle if rotate_cities else CITIES,
            gi - 1,
        )

        # Create folder name
        rep_dt = next((it.dt for it in grp if it.dt), None)
        date_part = rep_dt.strftime("%Y-%m-%d") if rep_dt else f"cluster-{gi:02d}"
        folder = out_dir / f"{date_part}-{surface}-{city}"
        folder.mkdir(parents=True, exist_ok=True)

        # Process each photo in the group
        for it in grp:
            pieces = []
            if brand:
                pieces.append(slugify(brand, lowercase=True))
            pieces += [primary, surface, city, short_hash(it.path)]

            base = "-".join([slugify(x, lowercase=True) for x in pieces if x])
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
                    "city": city,
                }
            )

    # Write manifest
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {len(manifest)} files. Manifest at {out_dir/'manifest.json'}")
