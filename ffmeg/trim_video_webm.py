# video_webm_optimizer.py – 2025 FIXED VERSION (input‑order bug resolved)
"""
VP9 / WebM compressor for modern web delivery.
• Trim, crop, FPS, duplicate‑frame removal
• Smart: single‑pass CRF or two‑pass VBR
• Row‑mt + multithread
NOTE: -vf must follow the *input* file in FFmpeg. This version fixes the order‑of‑arguments error you hit.
"""

import os
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Optional, Tuple


def get_video_dimensions(input_path: str) -> Tuple[int, int]:
    """Get video width and height using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        "-select_streams",
        "v:0",
        str(input_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        width = int(stream["width"])
        height = int(stream["height"])
        return width, height
    except (
        subprocess.CalledProcessError,
        KeyError,
        IndexError,
        json.JSONDecodeError,
    ) as e:
        raise RuntimeError(f"Failed to get video dimensions: {e}")


def optimize_to_webm(
    input_path: str,
    output_path: str,
    *,
    start_time: str = "00:00:00",  # HH:MM:SS.xx
    duration: Optional[str] = None,  # None = full clip
    width: int = 900,
    height: int = 620,
    fps: int = 30,
    crop: bool = False,
    remove_duplicates: bool = True,
    smart_remove_duplicates: bool = True,
    # quality
    crf: Optional[int] = 28,  # if set ⇒ single‑pass CRF max 51 min 0
    target_bitrate: str = "400k",  # used only if crf is None
    preset: str = "best",  #  good|realtime|best…
    threads: int = 0,  # 0 = auto
):
    input_path, output_path = Path(input_path), Path(output_path)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    # ► Build filter string ---------------------------------------------
    filters = []
    if crop:
        # Get source video dimensions
        src_width, src_height = get_video_dimensions(str(input_path))

        # Only crop dimensions that are smaller than source
        crop_width = min(width, src_width)
        crop_height = min(height, src_height)

        # Only apply crop filter if at least one dimension needs cropping
        if crop_width < src_width or crop_height < src_height:
            filters.append(
                f"crop={crop_width}:{crop_height}:(iw-{crop_width})/2:(ih-{crop_height})/2"
            )
            print(
                f"Cropping from {src_width}x{src_height} to {crop_width}x{crop_height}"
            )
        else:
            print(
                f"No cropping needed: target {width}x{height} >= source {src_width}x{src_height}"
            )
    if fps:
        filters.append(f"fps={fps}")
    if smart_remove_duplicates:
        filters.append(f"mpdecimate,setpts=N/({fps}*TB)")
    elif remove_duplicates:
        filters.append("mpdecimate")
    vf_filter = ",".join(filters) if filters else None

    # ► Common I/O params ----------------------------------------------
    io_opts = ["-y", "-hide_banner", "-loglevel", "error"]
    if start_time != "00:00:00":
        io_opts += ["-ss", start_time]
    if duration:
        io_opts += ["-t", duration]

    codec_base = [
        "-c:v",
        "libvpx-vp9",
        "-row-mt",
        "1",
        "-threads",
        str(max(1, threads)),
        "-speed",
        "2" if preset == "realtime" else "1",
        "-deadline",
        preset,
        "-pix_fmt",
        "yuv420p",
        "-an",
    ]
    if vf_filter:
        vf_param = ["-vf", vf_filter]
    else:
        vf_param = []

    # ► Single‑pass CRF -------------------------------------------------
    if crf is not None:
        cmd = [
            "ffmpeg",
            *io_opts,
            "-i",
            str(input_path),
            *vf_param,
            *codec_base,
            "-b:v",
            "0",
            "-crf",
            str(crf),
            str(output_path),
        ]
        subprocess.run(cmd, check=True)
        return

    # ► Two‑pass VBR ----------------------------------------------------
    stats = tempfile.NamedTemporaryFile(suffix=".log", delete=False).name

    first_pass = [
        "ffmpeg",
        *io_opts,
        "-i",
        str(input_path),
        *vf_param,
        *codec_base,
        "-b:v",
        target_bitrate,
        "-pass",
        "1",
        "-passlogfile",
        stats,
        "-f",
        "null",
        "-",
    ]
    second_pass = [
        "ffmpeg",
        *io_opts,
        "-i",
        str(input_path),
        *vf_param,
        *codec_base,
        "-b:v",
        target_bitrate,
        "-pass",
        "2",
        "-passlogfile",
        stats,
        str(output_path),
    ]
    subprocess.run(first_pass, check=True)
    subprocess.run(second_pass, check=True)
    try:
        os.remove(stats + ".log")
    except OSError:
        pass


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))

    input_path = current_dir + "/image_input" + "/solar-overview.mp4"
    output_path = current_dir + "/optimized_output" + "/solar-overview.mp4"

    optimize_to_webm(
        input_path=input_path,
        output_path=output_path,
        start_time="00:00:00.00",
        # duration="00:00:11.00",
        crop=False,
        width=881,
        height=720,
        fps=30,
        crf=20,
        preset="good",  #  good|realtime|best…
        target_bitrate="1.5M",  # used only if crf is None
    )
