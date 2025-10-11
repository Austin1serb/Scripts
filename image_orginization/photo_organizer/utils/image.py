"""Image processing utilities."""

import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PIL import Image
import imagehash
from concurrent.futures import ProcessPoolExecutor, as_completed


def register_heif():
    """Register HEIF image format handler."""
    try:
        from pillow_heif import register_heif_opener  # type: ignore

        register_heif_opener()
    except Exception:
        pass


def ensure_thumb(src: Path, dst: Path, max_px: int = 512):
    """Create a thumbnail for the given image.

    Args:
        src: Source image path
        dst: Destination thumbnail path
        max_px: Maximum dimension in pixels (default: 512)
            Note: 512px keeps images as single tile for GPT-4 Vision (85 tokens)
            vs 768px which uses 4 tiles (765 tokens) - 89% cost reduction!
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((max_px, max_px))
        im.save(dst, "JPEG", quality=50, optimize=True)


def phash(path_or_image, hash_size: int = 8) -> Optional[imagehash.ImageHash]:
    """Calculate perceptual hash using pHash algorithm (DCT-based).

    pHash is optimal for photo clustering because it:
        - Robust to scaling, compression, brightness/contrast adjustments
        - Captures structural essence using Discrete Cosine Transform
        - Industry standard for image similarity detection

    Hash Size Recommendations (based on research):
        - hash_size=8 (64-bit): ✅ OPTIMAL for photo clustering
            → Hamming distance 5-10 = similar photos
            → Catches: edits, crops, filters, exports
        - hash_size=16 (256-bit): For exact duplicate detection only
            → Too strict, misses edited versions

    For your use case (organizing construction photos), hash_size=8 is ideal.

    Args:
        path_or_image: Path to image or PIL Image object
        hash_size: Size of hash grid (default: 8 - optimal for clustering)

    Returns:
        ImageHash object or None on error
    """
    try:
        if isinstance(path_or_image, Path):
            im = Image.open(path_or_image).convert("RGB")
        else:
            im = path_or_image.convert("RGB")
        return imagehash.phash(im, hash_size=hash_size)
    except Exception:
        return None


def phash_combined(path_or_image, hash_size: int = 8) -> Optional[str]:
    """Calculate combined perceptual hash using multiple algorithms.

    Combines phash, dhash, and average_hash for better accuracy:
        - phash: Robust to scaling/rotation
        - dhash: Robust to gradients/textures
        - average_hash: Fast baseline

    This provides better matching than single algorithm while reducing false positives.

    Args:
        path_or_image: Path to image or PIL Image object
        hash_size: Size of hash grid (default: 8)

    Returns:
        Combined hash string (hex) or None on error
    """
    try:
        if isinstance(path_or_image, Path):
            im = Image.open(path_or_image).convert("RGB")
        else:
            im = path_or_image.convert("RGB")

        # Calculate multiple hashes
        p_hash = imagehash.phash(im, hash_size=hash_size)
        d_hash = imagehash.dhash(im, hash_size=hash_size)
        a_hash = imagehash.average_hash(im, hash_size=hash_size)

        # Combine hashes (concatenate hex strings)
        return f"{str(p_hash)}-{str(d_hash)}-{str(a_hash)}"
    except Exception:
        return None


def short_hash(p: Path, length: int = 12) -> str:
    """Generate a short hash of file contents for unique identification.

    Uses MD5 (fast, non-cryptographic use case):
        - 8 chars: 4B combinations (~0.1% collision at 100k images) ❌
        - 12 chars: 16 trillion combinations (safe for millions) ✅
        - 16 chars: Full 128-bit hash (overkill but safest)

    Args:
        p: Path to file
        length: Number of hex characters to return (default: 12)

    Returns:
        First N characters of MD5 hash (hex string)
    """
    try:
        # Python 3.9+ supports usedforsecurity parameter
        return hashlib.md5(p.read_bytes(), usedforsecurity=False).hexdigest()[:length]
    except TypeError:
        # Fallback for older Python versions
        return hashlib.md5(p.read_bytes()).hexdigest()[:length]


def _process_single_thumbnail(
    args: Tuple[Path, Path, int],
) -> Tuple[Path, bool, Optional[str]]:
    """Process a single thumbnail (worker function for concurrent processing).

    Args:
        args: Tuple of (src_path, dst_path, max_px)

    Returns:
        Tuple of (src_path, success, error_message)
    """
    src, dst, max_px = args
    try:
        ensure_thumb(src, dst, max_px)
        return src, True, None
    except Exception as e:
        return src, False, str(e)


def create_thumbnails_batch(
    files: List[Path],
    thumbs_dir: Path,
    max_px: int = 512,
    max_workers: Optional[int] = None,
) -> Dict[Path, Path]:
    """Create thumbnails for multiple files concurrently using multiprocessing.

    This is much faster than sequential processing because it uses multiple CPU cores
    for the CPU-intensive image decoding and resizing operations.

    Args:
        files: List of source image paths
        thumbs_dir: Directory to store thumbnails
        max_px: Maximum dimension in pixels (default: 512)
            Note: 512px = single tile for GPT-4 Vision (89% token reduction vs 768px)
        max_workers: Maximum number of processes (default: CPU count)

    Returns:
        Dictionary mapping source paths to thumbnail paths for successful operations
    """
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    # Prepare arguments for each file
    tasks = [(f, thumbs_dir / f"{f.stem}.jpg", max_px) for f in files]

    results = {}

    # Use ProcessPoolExecutor for CPU-bound image processing
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(_process_single_thumbnail, task): task[0] for task in tasks
        }

        # Collect results as they complete
        for future in as_completed(future_to_file):
            src_path, success, error = future.result()
            if success:
                results[src_path] = thumbs_dir / f"{src_path.stem}.jpg"
            else:
                print(f"[warn] thumb failed for {src_path.name}: {error}")

    return results


def _compute_single_phash(
    args: Tuple[Path, int],
) -> Tuple[Path, Optional[imagehash.ImageHash]]:
    """Compute phash for a single image (worker function for concurrent processing).

    Args:
        args: Tuple of (image_path, hash_size)

    Returns:
        Tuple of (image_path, phash_result)
    """
    path, hash_size = args
    return path, phash(path, hash_size)


def compute_phashes_batch(
    paths: List[Path], hash_size: int = 8, max_workers: Optional[int] = None
) -> Dict[Path, Optional[imagehash.ImageHash]]:
    """Compute perceptual hashes for multiple images concurrently.

    Uses multiprocessing for CPU-bound hash calculations.

    Args:
        paths: List of image paths
        hash_size: Size of hash grid (default: 8)
        max_workers: Maximum number of processes (default: CPU count)

    Returns:
        Dictionary mapping image paths to their phash values
    """
    # Prepare arguments for each file
    tasks = [(p, hash_size) for p in paths]

    results = {}

    # Use ProcessPoolExecutor for CPU-bound hash calculations
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {
            executor.submit(_compute_single_phash, task): task[0] for task in tasks
        }

        # Collect results as they complete
        for future in as_completed(future_to_path):
            path, hash_value = future.result()
            results[path] = hash_value

    return results
