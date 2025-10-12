"""Tests for clustering algorithms."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from datetime import datetime
from photo_organizer.models import Item
from photo_organizer.clustering import cluster_gps_only, phash_score, time_score


class TestGPSClustering:
    """Test GPS-based clustering."""

    def test_cluster_gps_only_basic(self):
        """Test basic GPS clustering."""
        # Create mock items with GPS coordinates
        items = [
            Item(
                id="1",
                path=Path("/tmp/1.jpg"),
                thumb=Path("/tmp/1_thumb.jpg"),
                dt=None,
                gps=(47.6101, -122.2015),  # Bellevue
                h=None,
            ),
            Item(
                id="2",
                path=Path("/tmp/2.jpg"),
                thumb=Path("/tmp/2_thumb.jpg"),
                dt=None,
                gps=(47.6102, -122.2016),  # Very close to Bellevue
                h=None,
            ),
            Item(
                id="3",
                path=Path("/tmp/3.jpg"),
                thumb=Path("/tmp/3_thumb.jpg"),
                dt=None,
                gps=(47.2529, -122.4443),  # Tacoma (far away)
                h=None,
            ),
        ]

        # Cluster within 100 meters - returns (multi_clusters, singletons)
        multi_clusters, singletons = cluster_gps_only(items, max_meters=100.0)

        # Should have 1 multi-photo cluster [1,2] and 1 singleton [3]
        assert len(multi_clusters) == 1
        assert len(singletons) == 1
        # Items 1&2 should be in the multi-photo cluster
        assert len(multi_clusters[0]) == 2
        cluster_ids = {it.id for it in multi_clusters[0]}
        assert cluster_ids == {"1", "2"}
        # Item 3 should be a singleton
        assert singletons[0].id == "3"

    def test_cluster_gps_only_no_gps(self):
        """Test GPS clustering with no GPS data."""
        items = [
            Item(
                id="1",
                path=Path("/tmp/1.jpg"),
                thumb=Path("/tmp/1_thumb.jpg"),
                dt=None,
                gps=None,
                h=None,
            ),
        ]

        # Returns (multi_clusters, singletons) - both should be empty for no GPS
        multi_clusters, singletons = cluster_gps_only(items, max_meters=100.0)
        assert len(multi_clusters) == 0
        assert len(singletons) == 0


class TestTemporalScoring:
    """Test temporal and hash scoring functions."""

    def test_time_score_close(self):
        """Test time score for close timestamps."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0)
        dt2 = datetime(2024, 1, 1, 12, 3, 0)  # 3 minutes apart

        score = time_score(dt1, dt2)
        assert score == 1.0

    def test_time_score_far(self):
        """Test time score for distant timestamps."""
        dt1 = datetime(2024, 1, 1, 12, 0, 0)
        dt2 = datetime(2024, 1, 2, 12, 0, 0)  # 24 hours apart

        score = time_score(dt1, dt2)
        assert score == 0.0

    def test_phash_score_none(self):
        """Test phash score with None values."""
        score = phash_score(None, None)
        assert score == 0.0


if __name__ == "__main__":
    pytest.main([__file__])
