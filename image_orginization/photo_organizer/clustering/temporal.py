"""Time-based clustering with perceptual hash centroid matching."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import numpy as np
import imagehash
from ..models import Item
from ..config import DEFAULT_TIME_GAP_MINUTES


def phash_score(
    hash_a: Optional[imagehash.ImageHash], hash_b: Optional[imagehash.ImageHash]
) -> float:
    """Calculate similarity score between two perceptual hashes.

    Args:
        hash_a, hash_b: ImageHash objects to compare

    Returns:
        Similarity score between 0.0 and 1.0 (smaller distance = higher score)
    """
    if hash_a is None or hash_b is None:
        return 0.0

    hamming_distance = hash_a - hash_b
    if hamming_distance <= 4:
        return 1.0
    if hamming_distance <= 6:
        return 0.8
    if hamming_distance <= 8:
        return 0.6
    if hamming_distance <= 12:
        return 0.3
    return 0.0


def time_score(datetime_a: Optional[datetime], datetime_b: Optional[datetime]) -> float:
    """Calculate similarity score between two timestamps.

    Args:
        datetime_a, datetime_b: Datetime objects to compare

    Returns:
        1.0 if within DEFAULT_TIME_GAP_MINUTES, 0.0 otherwise
    """
    if not datetime_a or not datetime_b:
        return 0.0

    time_gap_minutes = abs((datetime_a - datetime_b).total_seconds()) / 60.0
    return 1.0 if time_gap_minutes <= DEFAULT_TIME_GAP_MINUTES else 0.0


def phash_median(hashes) -> Optional[imagehash.ImageHash]:
    """Calculate median perceptual hash from a list of hashes.

    Used to find the centroid hash for a cluster of images.

    Args:
        hashes: List of ImageHash objects

    Returns:
        Median ImageHash or None if no valid hashes
    """
    valid_hashes = [image_hash for image_hash in hashes if image_hash is not None]
    print("valid_hashes: ", valid_hashes)
    if not valid_hashes:
        return None

    reference_hash = valid_hashes[0]
    bit_count = reference_hash.hash.size  # 256 for 16x16
    bit_accumulator = np.zeros(bit_count, dtype=int)

    for image_hash in valid_hashes:
        flattened_hash = image_hash.hash.flatten().astype(bool)
        bit_accumulator += np.where(flattened_hash, 1, -1)

    median_hash_array = (bit_accumulator >= 0).reshape(
        reference_hash.hash.shape
    )  # (16,16)
    return imagehash.ImageHash(median_hash_array)


def cluster_temporal(
    items: List[Item], time_gap_min: int, hash_threshold: int
) -> List[List[Item]]:
    """Cluster items using time + pHash centroid with AND logic.

    Images must be within both the time gap AND hash threshold to stay in same cluster.

    Args:
        items: List of items to cluster
        time_gap_min: Maximum time gap in minutes
        hash_threshold: Maximum perceptual hash distance

    Returns:
        List of clusters
    """
    items_sorted = sorted(
        items, key=lambda item: (item.dt or datetime.min, item.path.name)
    )
    clusters: List[List[Item]] = []
    current_cluster: List[Item] = []

    for current_item in items_sorted:
        if not current_cluster:
            current_cluster = [current_item]
            continue

        # Check time constraint
        latest_datetime = max(
            (item.dt for item in current_cluster if item.dt), default=None
        )
        time_constraint_met = True
        if current_item.dt and latest_datetime:
            time_constraint_met = (current_item.dt - latest_datetime) <= timedelta(
                minutes=time_gap_min
            )

        # Check hash constraint against cluster centroid
        cluster_centroid = phash_median([item.h for item in current_cluster])
        hash_constraint_met = True
        if cluster_centroid is not None and current_item.h is not None:
            try:
                hash_constraint_met = (
                    current_item.h - cluster_centroid
                ) <= hash_threshold
            except Exception:
                hash_constraint_met = True

        # AND logic: require both conditions
        if time_constraint_met and hash_constraint_met:
            current_cluster.append(current_item)
        else:
            clusters.append(current_cluster)
            current_cluster = [current_item]

    if current_cluster:
        clusters.append(current_cluster)

    return clusters


def cluster_phash_only(items: List[Item], hash_threshold: int = 6) -> List[List[Item]]:
    """Cluster photos using ONLY perceptual hash similarity (visual similarity).

    This is a pure visual similarity clustering to test pHash accuracy in isolation.
    Uses connected components: photos within hash_threshold distance are connected.

    Args:
        items: List of items to cluster
        hash_threshold: Maximum hamming distance to consider photos similar (0-64)
            Lower = stricter (more similar required)
            Default 6 = visually very similar

    Returns:
        List of clusters, each cluster is a list of similar-looking photos
    """
    if not items:
        return []

    # Filter out items without pHash
    items_with_hash = [item for item in items if item.h is not None]

    if not items_with_hash:
        return []

    # Build adjacency graph based on pHash distance
    adjacency: Dict[str, List[str]] = defaultdict(list)

    # Compare all pairs (O(n²) but simple for testing)
    for i, item_a in enumerate(items_with_hash):
        for item_b in items_with_hash[i + 1 :]:
            hamming_distance = item_a.h - item_b.h

            if hamming_distance <= hash_threshold:
                adjacency[item_a.id].append(item_b.id)
                adjacency[item_b.id].append(item_a.id)

    # Find connected components using BFS
    visited = set()
    clusters = []

    for item in items_with_hash:
        if item.id in visited:
            continue

        # BFS to find all connected items
        cluster = []
        queue = [item.id]
        visited.add(item.id)

        while queue:
            current_id = queue.pop(0)
            # Find the actual item object
            current_item = next(it for it in items_with_hash if it.id == current_id)
            cluster.append(current_item)

            # Add unvisited neighbors
            for neighbor_id in adjacency[current_id]:
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        clusters.append(cluster)

    return clusters
