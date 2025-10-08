"""Data models and structures for photo organization."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import imagehash


@dataclass
class NameFeat:
    """Features extracted from filename."""

    prefix: str
    num: Optional[int]
    suffix: str
    raw: str


@dataclass
class Item:
    """Represents a single photo with metadata."""

    id: str
    path: Path
    thumb: Path
    dt: Optional[datetime]
    gps: Optional[Tuple[float, float]]
    h: Optional[imagehash.ImageHash]


class DSU:
    """Disjoint Set Union (Union-Find) data structure for clustering."""

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        """Find root of element x with path compression."""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int):
        """Union two sets by rank."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1
