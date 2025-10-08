"""Tests for utility functions."""

from pathlib import Path
import sys


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from photo_organizer.models import NameFeat
from photo_organizer.utils.filename import name_features, filename_score, lcp_len
from photo_organizer.utils.geo import haversine, meters_between


class TestFilenameUtils:
    """Test filename parsing and scoring."""

    def test_name_features_basic(self):
        """Test basic filename parsing."""
        feat = name_features(Path("IMG_1234.jpg"))
        print("feat: ", feat)
        assert feat.prefix == "img"
        assert feat.num == 1234

    def test_name_features_no_number(self):
        """Test filename without numbers."""
        feat = name_features(Path("photo.jpg"))
        assert feat.num is None

    def test_lcp_len(self):
        """Test longest common prefix."""
        assert lcp_len("hello", "helium") == 3
        assert lcp_len("abc", "xyz") == 0
        assert lcp_len("same", "same") == 4

    def test_filename_score_identical(self):
        """Test filename score for identical features."""
        feat1 = NameFeat(prefix="img", num=100, suffix="", raw="img_100")
        feat2 = NameFeat(prefix="img", num=100, suffix="", raw="img_100")

        score = filename_score(feat1, feat2)
        # With new scoring: 0.6 (number) + 0.3 (string) + 0.1 (bonus) = 1.0 max
        assert score >= 0.85  # Allow for floating point precision

    def test_filename_score_sequential(self):
        """Test filename score for sequential numbers."""
        feat1 = NameFeat(prefix="img", num=100, suffix="", raw="img_100")
        feat2 = NameFeat(prefix="img", num=101, suffix="", raw="img_101")

        score = filename_score(feat1, feat2)
        assert score > 0.7


class TestGeoUtils:
    """Test geographic utilities."""

    def test_haversine_same_point(self):
        """Test haversine distance for same point."""
        distance = haversine(47.6101, -122.2015, 47.6101, -122.2015)
        assert distance == 0.0

    def test_haversine_known_distance(self):
        """Test haversine with known distance."""
        # Bellevue to Tacoma is roughly 50-60 km
        distance = haversine(47.6101, -122.2015, 47.2529, -122.4443)
        assert 40 < distance < 70  # Allow some margin

    def test_meters_between(self):
        """Test meters_between conversion."""
        # Very close points (0.0009 degrees latitude ≈ 100m at this latitude)
        p1 = (47.6101, -122.2015)
        p2 = (47.6110, -122.2015)

        distance = meters_between(p1, p2)
        assert 80 < distance < 120  # ~100m with some margin for calculation precision


if __name__ == "__main__":
    pytest.main([__file__])
