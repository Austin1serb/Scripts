"""GPS-based clustering for grouping photos by location. if only one photo is found, it is returned as a singleton.

Expected EXIF Data Structures (from utils.exif):
    - Item.gps: Optional[Tuple[float, float]]
      → (latitude, longitude) in decimal degrees
      → Example: (47.2389194444444, -122.091902777778)
      → None if GPS data unavailable

    - Item.dt: Optional[datetime]
      → Naive datetime object (timezone stripped for consistency)
      → Example: datetime(2021, 10, 28, 16, 27, 25, 412000)
      → None if datetime unavailable
"""

from typing import List
from ..models import Item, DSU
from ..utils.geo import meters_between


def cluster_gps_only(items: List[Item], max_meters: float = 300):
    """Cluster items strictly by GPS location threshold, ignoring time.

    Groups photos that are within max_meters of each other into the same cluster.
    GPS singletons are separated out - they'll be re-clustered using filename/datetime.

    Args:
        items: List of Item objects to cluster
            - Item.gps must be (lat, lon) tuple in decimal degrees or None
        max_meters: Maximum distance in meters for photos to be in same cluster

    Returns:
        Tuple of (multi_photo_clusters, singletons):
            - multi_photo_clusters: List of clusters with 2+ photos
            - singletons: List of single Item objects that didn't cluster
                         (these should be re-clustered using fused strategy)
    """
    # Only consider items with GPS data
    items_with_gps = [item for item in items if item.gps]
    if not items_with_gps:
        return [], []

    num_gps_items = len(items_with_gps)
    cluster_tracker = DSU(num_gps_items)

    # Compare all pairs and unite if within distance threshold
    for index_a in range(num_gps_items):
        item_a = items_with_gps[index_a]
        for index_b in range(index_a + 1, num_gps_items):
            item_b = items_with_gps[index_b]
            distance_meters = meters_between(item_a.gps, item_b.gps)
            if distance_meters <= max_meters:
                cluster_tracker.union(index_a, index_b)

    # Group items by their cluster root
    clusters_by_root: dict[int, List[Item]] = {}
    for item_index in range(num_gps_items):
        cluster_root = cluster_tracker.find(item_index)
        clusters_by_root.setdefault(cluster_root, []).append(items_with_gps[item_index])

    # Separate multi-photo clusters from singletons
    all_groups = list(clusters_by_root.values())
    multi_photo_groups = [g for g in all_groups if len(g) > 1]
    singletons = [g[0] for g in all_groups if len(g) == 1]

    return multi_photo_groups, singletons
