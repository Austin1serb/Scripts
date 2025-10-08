"""Tests for EXIF extraction utilities."""

from pathlib import Path
import sys
from unittest.mock import Mock, patch
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from photo_organizer.utils.exif import (
    read_exif_combined,
    read_exif_batch,
)


class TestExifExtraction:
    """Test EXIF data extraction functions."""

    @patch("photo_organizer.utils.exif.subprocess.run")
    def test_read_exif_combined_success(self, mock_run):
        """Test combined extraction of datetime and GPS."""
        # Mock exiftool response with both datetime and GPS
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "EXIF:DateTimeOriginal": "2024:01:15 14:30:45",
                        "Composite:SubSecDateTimeOriginal": "2024:01:15 14:30:45",
                        "Composite:GPSLatitude": 47.6101,
                        "Composite:GPSLongitude": -122.2015,
                    }
                ]
            ),
        )

        dt, gps = read_exif_combined(Path("test.jpg"))

        # Check datetime
        assert dt is not None
        assert dt.year == 2024

        # Check GPS
        assert gps is not None
        lat, lon = gps
        assert abs(lat - 47.6101) < 0.0001
        assert abs(lon - (-122.2015)) < 0.0001

    @patch("photo_organizer.utils.exif.subprocess.run")
    def test_read_exif_combined_partial_data(self, mock_run):
        """Test combined extraction with only datetime (no GPS)."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "EXIF:DateTimeOriginal": "2024:01:15 14:30:45",
                        "Composite:SubSecDateTimeOriginal": "2024:01:15 14:30:45",
                    }
                ]
            ),
        )

        dt, gps = read_exif_combined(Path("test.jpg"))
        assert dt is not None
        assert gps is None

    @patch("photo_organizer.utils.exif.read_exif_combined")
    def test_read_exif_batch_multiple_files(self, mock_combined):
        """Test batch extraction with multiple files."""
        from datetime import datetime

        # Mock responses for different files
        def side_effect(path):
            if "photo1" in str(path):
                return datetime(2024, 1, 15), (47.6101, -122.2015)
            elif "photo2" in str(path):
                return datetime(2024, 1, 16), None
            else:
                return None, None

        mock_combined.side_effect = side_effect

        paths = [Path("photo1.jpg"), Path("photo2.jpg"), Path("photo3.jpg")]
        results = read_exif_batch(paths, max_workers=2)

        # Check we got results for all files
        assert len(results) == 3

        # Check photo1 has both datetime and GPS
        assert results[Path("photo1.jpg")]["dt"] is not None
        assert results[Path("photo1.jpg")]["gps"] is not None

        # Check photo2 has datetime but no GPS
        assert results[Path("photo2.jpg")]["dt"] is not None
        assert results[Path("photo2.jpg")]["gps"] is None

        # Check photo3 has neither
        assert results[Path("photo3.jpg")]["dt"] is None
        assert results[Path("photo3.jpg")]["gps"] is None

    def test_read_exif_batch_empty_list(self):
        """Test batch processing with empty file list."""
        results = read_exif_batch([], max_workers=4)
        assert results == {}

    @patch("photo_organizer.utils.exif.read_exif_combined")
    def test_read_exif_batch_with_error(self, mock_combined, capsys):
        """Test batch processing when one file fails."""
        from datetime import datetime

        # Mock one file to succeed, one to fail
        def side_effect(path):
            if "good" in str(path):
                return datetime(2024, 1, 15), (47.6101, -122.2015)
            else:
                raise Exception("Simulated error")

        mock_combined.side_effect = side_effect

        paths = [Path("good.jpg"), Path("bad.jpg")]
        results = read_exif_batch(paths, max_workers=2)

        # Check that good file has data
        assert results[Path("good.jpg")]["dt"] is not None
        assert results[Path("good.jpg")]["gps"] is not None

        # Check that bad file has None values (graceful failure)
        assert results[Path("bad.jpg")]["dt"] is None
        assert results[Path("bad.jpg")]["gps"] is None

        # Check that warning was printed
        captured = capsys.readouterr()
        assert "EXIF extraction failed" in captured.out
        assert "bad.jpg" in captured.out

    @patch("photo_organizer.utils.exif.subprocess.run")
    def test_read_exif_combined_no_datetime_but_has_gps(self, mock_run):
        """Test combined extraction with only GPS (no datetime)."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(
                [
                    {
                        "Composite:GPSLatitude": 47.6101,
                        "Composite:GPSLongitude": -122.2015,
                    }
                ]
            ),
        )

        dt, gps = read_exif_combined(Path("test.jpg"))
        assert dt is None
        assert gps is not None
        lat, lon = gps
        assert abs(lat - 47.6101) < 0.0001

    @patch("photo_organizer.utils.exif.subprocess.run")
    def test_read_exif_combined_human_readable_date(self, mock_run):
        """Test datetime extraction with human-readable month names."""
        # Test various month name formats
        test_cases = [
            # Month-first formats (common in iOS/macOS)
            ("April 21, 2021 12:47", (2021, 4, 21, 12, 47, 0)),
            ("December 1, 2024 14:30:45", (2024, 12, 1, 14, 30, 45)),
            ("January 1st, 2023 09:15", (2023, 1, 1, 9, 15, 0)),
            ("March 3rd 2022 16:20:30", (2022, 3, 3, 16, 20, 30)),
            ("May 15th, 2020 08:00:00", (2020, 5, 15, 8, 0, 0)),
            # DD-MMM-YYYY format (some camera software)
            ("08-Oct-2025 14:30:45", (2025, 10, 8, 14, 30, 45)),
            ("1-Jan-2023 09:15", (2023, 1, 1, 9, 15, 0)),
            ("25-Dec-2024 23:59:59", (2024, 12, 25, 23, 59, 59)),
        ]

        for date_string, expected in test_cases:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=json.dumps([{"EXIF:DateTimeOriginal": date_string}]),
            )

            dt, _ = read_exif_combined(Path("test.jpg"))
            assert dt is not None, f"Failed to parse: {date_string}"
            assert dt.year == expected[0], f"Year mismatch for {date_string}"
            assert dt.month == expected[1], f"Month mismatch for {date_string}"
            assert dt.day == expected[2], f"Day mismatch for {date_string}"
            assert dt.hour == expected[3], f"Hour mismatch for {date_string}"
            assert dt.minute == expected[4], f"Minute mismatch for {date_string}"
            assert dt.second == expected[5], f"Second mismatch for {date_string}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
