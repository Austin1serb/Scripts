"""EXIF data extraction utilities."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def read_exif_combined(
    p: Path,
) -> Tuple[Optional[datetime], Optional[Tuple[float, float]]]:
    """Extract both datetime and GPS from EXIF in a single exiftool call.

    Args:
        p: Path to image file

    Returns:
        Tuple of (datetime, gps_coords) or (None, None) if not found
    """
    try:
        # Single exiftool call to get all data
        result = subprocess.run(
            ["exiftool", "-a", "-G", "-s", "-n", "-json", str(p)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return None, None

        data = json.loads(result.stdout)
        if not data or len(data) == 0:
            return None, None

        exif_data = data[0]

        # Extract datetime - ONLY from creation/capture tags, NOT modification
        dt = None

        # Priority order: When photo was TAKEN (not modified)
        # SubSec* tags include subseconds for higher precision
        date_keys = [
            "Composite:SubSecDateTimeOriginal",  # Most precise capture time
            "EXIF:SubSecDateTimeOriginal",  # EXIF version with subseconds
            "EXIF:DateTimeOriginal",  # Standard capture time (MOST COMMON)
            "EXIF:DateTimeDigitized",  # When digitized (for scanned photos)
            "Composite:SubSecCreateDate",  # Composite with subseconds
            "EXIF:SubSecCreateDate",  # EXIF with subseconds
            "EXIF:CreateDate",  # Fallback creation time
            # Note: Explicitly NOT including ModifyDate or FileModifyDate
        ]

        for key in date_keys:
            if key in exif_data:
                raw = str(exif_data[key]).strip()

                # Try human-readable format first (e.g., "April 21, 2021 12:47")
                # Format: Month DD, YYYY HH:MM or Month DD, YYYY HH:MM:SS
                human_match = re.match(
                    r"(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?",
                    raw,
                )
                if human_match:
                    month_name = human_match.group(1)
                    day = human_match.group(2)
                    year = human_match.group(3)
                    hour = human_match.group(4)
                    minute = human_match.group(5)
                    second = human_match.group(6) or "0"

                    month_map = {
                        "january": 1,
                        "jan": 1,
                        "february": 2,
                        "feb": 2,
                        "march": 3,
                        "mar": 3,
                        "april": 4,
                        "apr": 4,
                        "may": 5,
                        "june": 6,
                        "jun": 6,
                        "july": 7,
                        "jul": 7,
                        "august": 8,
                        "aug": 8,
                        "september": 9,
                        "sep": 9,
                        "sept": 9,
                        "october": 10,
                        "oct": 10,
                        "november": 11,
                        "nov": 11,
                        "december": 12,
                        "dec": 12,
                    }

                    month_num = month_map.get(month_name.lower())
                    if month_num:
                        try:
                            dt = datetime(
                                int(year),
                                month_num,
                                int(day),
                                int(hour),
                                int(minute),
                                int(second),
                            )
                            break
                        except ValueError:
                            pass

                # Try DD-MMM-YYYY format (e.g., "08-Oct-2025 14:30:45")
                dmy_match = re.match(
                    r"(\d{1,2})-(\w{3})-(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?", raw
                )
                if dmy_match:
                    day = dmy_match.group(1)
                    month_abbr = dmy_match.group(2)
                    year = dmy_match.group(3)
                    hour = dmy_match.group(4)
                    minute = dmy_match.group(5)
                    second = dmy_match.group(6) or "0"

                    month_map = {
                        "jan": 1,
                        "feb": 2,
                        "mar": 3,
                        "apr": 4,
                        "may": 5,
                        "jun": 6,
                        "jul": 7,
                        "aug": 8,
                        "sep": 9,
                        "oct": 10,
                        "nov": 11,
                        "dec": 12,
                    }

                    month_num = month_map.get(month_abbr.lower())
                    if month_num:
                        try:
                            dt = datetime(
                                int(year),
                                month_num,
                                int(day),
                                int(hour),
                                int(minute),
                                int(second),
                            )
                            break
                        except ValueError:
                            pass

                # Strip subseconds if present (e.g., .123 or .123456)
                # EXIF can have varying subsecond precision (3-6 digits)
                raw_no_subsec = re.sub(r"\.(\d+)", "", raw)

                # Try standard numeric formats (comprehensive list)
                formats = [
                    # EXIF standard with subseconds and timezone
                    "%Y:%m:%d %H:%M:%S.%f%z",  # 2025:10:08 14:30:45.123+0800
                    "%Y:%m:%d %H:%M:%S.%f",  # 2025:10:08 14:30:45.123
                    # EXIF standard with timezone
                    "%Y:%m:%d %H:%M:%S%z",  # 2025:10:08 14:30:45+0800
                    "%Y:%m:%d %H:%M:%S",  # 2025:10:08 14:30:45 (MOST COMMON)
                    "%Y:%m:%d %H:%M",  # 2025:10:08 14:30
                    # ISO 8601 formats
                    "%Y-%m-%dT%H:%M:%S.%f%z",  # 2025-10-08T14:30:45.123+08:00
                    "%Y-%m-%dT%H:%M:%S%z",  # 2025-10-08T14:30:45+08:00
                    "%Y-%m-%dT%H:%M:%SZ",  # 2025-10-08T14:30:45Z (UTC)
                    "%Y-%m-%dT%H:%M:%S",  # 2025-10-08T14:30:45
                    "%Y-%m-%d %H:%M:%S.%f%z",  # 2025-10-08 14:30:45.123+0800
                    "%Y-%m-%d %H:%M:%S%z",  # 2025-10-08 14:30:45+0800
                    "%Y-%m-%d %H:%M:%S.%f",  # 2025-10-08 14:30:45.123
                    "%Y-%m-%d %H:%M:%S",  # 2025-10-08 14:30:45
                    "%Y-%m-%d %H:%M",  # 2025-10-08 14:30
                    # Date only formats
                    "%Y:%m:%d",  # 2025:10:08
                    "%Y-%m-%d",  # 2025-10-08
                ]

                for fmt in formats:
                    try:
                        dt = datetime.strptime(raw_no_subsec, fmt)
                        # Convert timezone-aware to naive for consistency
                        if dt.tzinfo is not None:
                            dt = dt.replace(tzinfo=None)
                        break
                    except ValueError:
                        continue

                if dt:
                    break

        # Extract GPS
        gps = None
        if (
            "Composite:GPSLatitude" in exif_data
            and "Composite:GPSLongitude" in exif_data
        ):
            try:
                lat = float(exif_data["Composite:GPSLatitude"])
                lon = float(exif_data["Composite:GPSLongitude"])
                gps = (lat, lon)
            except (ValueError, TypeError):
                pass

        # Fallback to EXIF fields
        if gps is None:
            lat = None
            lon = None

            if "EXIF:GPSLatitude" in exif_data:
                print("EXIF:GPSLatitude: ", exif_data["EXIF:GPSLatitude"])
                try:
                    lat = float(exif_data["EXIF:GPSLatitude"])
                except (ValueError, TypeError):
                    pass

            if "EXIF:GPSLongitude" in exif_data:
                print("EXIF:GPSLongitude: ", exif_data["EXIF:GPSLongitude"])
                try:
                    lon = float(exif_data["EXIF:GPSLongitude"])
                except (ValueError, TypeError):
                    pass

            if lat is not None and lon is not None:
                lat_ref = exif_data.get("EXIF:GPSLatitudeRef", "")
                lon_ref = exif_data.get("EXIF:GPSLongitudeRef", "")

                if isinstance(lat_ref, str) and lat_ref.upper().startswith("S"):
                    lat = -lat
                if isinstance(lon_ref, str) and lon_ref.upper().startswith("W"):
                    lon = -lon

                gps = (lat, lon)

        return dt, gps

    except (
        subprocess.TimeoutExpired,
        subprocess.SubprocessError,
        json.JSONDecodeError,
        Exception,
    ):
        return None, None


def read_exif_batch(
    paths: List[Path], max_workers: int = 8
) -> Dict[Path, Dict[str, Optional[any]]]:
    """Extract EXIF data from multiple files concurrently using exiftool.

    This is much faster than sequential processing because it:
    1. Runs only ONE exiftool call per file
    2. Runs multiple exiftool processes in parallel

    Args:
        paths: List of image file paths
        max_workers: Maximum number of concurrent exiftool processes (default: 8)

    Returns:
        Dictionary mapping Path to dict with 'dt' and 'gps' keys
        Example: {path: {'dt': datetime_obj, 'gps': (lat, lon)}}
    """
    results = {p: {"dt": None, "gps": None} for p in paths}

    def process_single_file(
        p: Path,
    ) -> Tuple[Path, Optional[datetime], Optional[Tuple[float, float]]]:
        """Process a single file and return path, datetime, and GPS."""
        dt, gps = read_exif_combined(p)
        # print("p, dt, gps: ", p, dt, gps)
        return p, dt, gps

    # Use ThreadPoolExecutor to run exiftool calls concurrently
    # Threading works well here because exiftool is I/O-bound (external process)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_path = {
            executor.submit(process_single_file, path): path for path in paths
        }

        # Collect results as they complete
        for future in as_completed(future_to_path):
            try:
                path, dt, gps = future.result()
                results[path] = {"dt": dt, "gps": gps}
            except Exception as e:
                # If processing fails, keep the None values
                path = future_to_path[future]
                print(f"[warn] EXIF extraction failed for {path.name}: {e}")

    return results
