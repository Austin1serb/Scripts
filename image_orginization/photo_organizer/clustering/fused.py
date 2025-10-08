"""Fused clustering using filename, hash, and time similarities.

Expected EXIF Data Structures (from utils.exif):
    - Item.dt: Optional[datetime]
      → Naive datetime object (timezone stripped for consistency)
      → Example: datetime(2021, 10, 28, 16, 27, 25, 412000)
      → None if datetime unavailable

    - Item.h: Optional[str]
      → Perceptual hash string for visual similarity
      → None if hash unavailable
"""

from collections import defaultdict, deque
from typing import List, Dict
from ..models import Item, NameFeat
from ..utils.filename import filename_score, lcp_len
from .temporal import phash_score, time_score


def fuse_score(it_a: Item, it_b: Item, nf: Dict[str, NameFeat]) -> float:
    """Calculate combined similarity score between two items.

    Combines filename, perceptual hash, and time similarities with weighted sum.

    Args:
        it_a, it_b: Items to compare
        nf: Dictionary mapping item IDs to NameFeat objects

    Returns:
        Combined similarity score between 0.0 and 1.0
    """
    a, b = nf[it_a.id], nf[it_b.id]
    s_name = filename_score(a, b)
    s_hash = phash_score(it_a.h, it_b.h)
    s_time = time_score(it_a.dt, it_b.dt)

    # Weighted sum: filename and hash carry more weight than time
    return 0.5 * s_name + 0.35 * s_hash + 0.15 * s_time


def fused_cluster(
    items: List[Item],
    nf: Dict[str, NameFeat],
    fuse_threshold: float = 0.75,
    max_edges_per_node: int = 40,
) -> List[List[Item]]:
    """Build similarity graph using fused score and return connected components.

    To keep it fast on hundreds of images, only connect each node to its top-K neighbors.

    Args:
        items: List of items to cluster
        nf: Dictionary mapping item IDs to NameFeat objects
        fuse_threshold: Minimum similarity score to connect items (default: 0.75)
        max_edges_per_node: Maximum connections per item (default: 20)

    Returns:
        List of clusters (connected components)
    """
    if not items:
        return []

    # Index by simple buckets to prune comparisons: same prefix bucket
    prefix_buckets = defaultdict(list)
    for item in items:
        prefix_buckets[nf[item.id].prefix].append(item)

    adjacency_graph: Dict[str, List[str]] = defaultdict(list)

    def consider_items_in_bucket(items_in_bucket: List[Item]):
        """Compute pairwise scores in a pruned way."""
        for item_a in items_in_bucket:
            # Pick candidates: nearest numbers by absolute diff if numeric exists
            candidate_items = sorted(
                items_in_bucket,
                key=lambda x: (
                    abs((nf[item_a.id].num or 10**9) - (nf[x.id].num or 10**9)),
                    lcp_len(nf[item_a.id].raw, nf[x.id].raw),
                ),
            )[: max_edges_per_node * 4]

            scored_candidates = []
            for item_b in candidate_items:
                if item_a.id == item_b.id:
                    continue
                similarity_score = fuse_score(item_a, item_b, nf)
                scored_candidates.append((similarity_score, item_b))

            scored_candidates.sort(reverse=True, key=lambda x: x[0])
            for similarity_score, item_b in scored_candidates[:max_edges_per_node]:
                if similarity_score >= fuse_threshold:
                    adjacency_graph[item_a.id].append(item_b.id)
                    adjacency_graph[item_b.id].append(item_a.id)

    for items_in_bucket in prefix_buckets.values():
        # Light heuristic: also try a global pool for empty/short prefixes
        consider_items_in_bucket(items_in_bucket)

    # Connected components over adjacency graph; include isolated nodes
    item_id_to_item = {item.id: item for item in items}
    visited_item_ids = set()
    clusters: List[List[Item]] = []

    for item in items:
        if item.id in visited_item_ids:
            continue
        cluster_items = []
        bfs_queue = deque([item.id])
        visited_item_ids.add(item.id)
        while bfs_queue:
            current_item_id = bfs_queue.popleft()
            cluster_items.append(item_id_to_item[current_item_id])
            for neighbor_item_id in adjacency_graph.get(current_item_id, []):
                if neighbor_item_id not in visited_item_ids:
                    visited_item_ids.add(neighbor_item_id)
                    bfs_queue.append(neighbor_item_id)
        clusters.append(cluster_items)

    return clusters
