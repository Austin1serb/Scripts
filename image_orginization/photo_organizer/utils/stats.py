"""Clustering statistics utility functions."""

from typing import List, Dict, Any


def print_clustering_stats(
    summary: List[Dict[str, Any]], gps_groups_count: int, non_gps_groups_count: int
) -> None:
    """Print comprehensive clustering statistics.

    Args:
        summary: List of cluster dictionaries with metadata
        gps_groups_count: Number of GPS-based clusters
        non_gps_groups_count: Number of non-GPS clusters
    """
    total_clusters = len(summary)
    total_photos = sum(c["count"] for c in summary)
    singleton_clusters = sum(1 for c in summary if c["count"] == 1)
    hash_only_files = sum(c["count"] for c in summary if c["strategy"] == "hash_only")

    print(f"\n{'='*60}")
    print("CLUSTERING SUMMARY")
    print(f"{'='*60}")
    print(f"Total clusters: {total_clusters}")
    print(f"  ├─ GPS clusters: {gps_groups_count}")
    print(f"  └─ Non-GPS clusters: {non_gps_groups_count}")
    print(
        f"\nSingleton clusters (1 photo): {singleton_clusters} "
        f"({singleton_clusters/total_photos*100:.1f}% of photos)"
    )
    print(f"\nFiles clustered by strategy:")
    print(
        f"  ├─ GPS location: "
        f"{sum(c['count'] for c in summary if c['strategy'] == 'gps_location')} files"
    )

    # Check if in pHash-only test mode
    phash_test_files = sum(
        c["count"] for c in summary if c["strategy"] == "phash_only_test"
    )
    if phash_test_files > 0:
        print(f"  └─ pHash only (TEST MODE): {phash_test_files} files")
    else:
        print(
            f"  ├─ Time+Filename+Hash: "
            f"{sum(c['count'] for c in summary if c['strategy'] == 'time+filename+hash')} files"
        )
        print(
            f"  ├─ Filename+Hash: "
            f"{sum(c['count'] for c in summary if c['strategy'] == 'filename+hash')} files"
        )
        print(f"  └─ Hash only: {hash_only_files} files")
    print(f"{'='*60}\n")
