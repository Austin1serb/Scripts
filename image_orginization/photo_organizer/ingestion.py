"""Photo ingestion and metadata extraction."""

from pathlib import Path
from typing import List
from tqdm import tqdm
from .models import Item
from .config import SUPPORTED_EXTS
from .utils.image import register_heif, ensure_thumb, phash
from .utils.exif import read_exif_batch


def ingest(input_dir: Path, work_dir: Path, max_workers: int = 8) -> List[Item]:
    """Ingest photos from input directory, creating thumbnails and extracting metadata.

    For each supported image file found:
    1. Creates a thumbnail for efficient processing
    2. Extracts EXIF datetime and GPS concurrently (much faster!)
    3. Computes perceptual hash

    Args:
        input_dir: Directory containing input photos
        work_dir: Working directory for temporary files (thumbnails)
        max_workers: Maximum number of concurrent exiftool processes (default: 8)

    Returns:
        List of Item objects with extracted metadata
    """
    register_heif()
    thumbs_dir = work_dir / "thumbs"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    files = [
        p
        for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]

    # Step 1: Create thumbnails (sequential because it's CPU/disk intensive)
    valid_files = []
    for p in tqdm(files, desc="Creating thumbnails", unit="img"):
        thumb = thumbs_dir / f"{p.stem}.jpg"
        try:
            ensure_thumb(p, thumb)
            valid_files.append(p)
        except Exception as e:
            print(f"[warn] thumb failed for {p.name}: {e}")

    # Step 2: Extract EXIF data concurrently (much faster!)
    print(
        f"Extracting EXIF data from {len(valid_files)} files using {max_workers} workers..."
    )
    exif_data = read_exif_batch(valid_files, max_workers=max_workers)

    # Step 3: Build Item objects with all metadata
    items: List[Item] = []
    for p in tqdm(valid_files, desc="Building items", unit="img"):
        thumb = thumbs_dir / f"{p.stem}.jpg"
        exif = exif_data.get(p, {"dt": None, "gps": None})

        items.append(
            Item(
                id=p.name,
                path=p,
                thumb=thumb,
                dt=exif["dt"],
                gps=exif["gps"],
                h=phash(thumb),
            )
        )

    return items
