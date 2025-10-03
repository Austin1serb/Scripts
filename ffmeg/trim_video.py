import subprocess
import os
import tempfile

current_dir = os.path.dirname(os.path.abspath(__file__))


def trim_and_optimize_video(
    input_path,
    output_path,
    start_time,
    duration,
    preset="veryfast",
    target_bitrate="500K",
    max_bitrate="1000K",
    bufsize="1M",
    width=1200,
    height=720,
    fps=30,
    remove_duplicates=False,
    smart_remove_duplicates=False,
    codec="libx264",
):
    """
    Trims and optimizes a video using FFmpeg with two-pass encoding.

    Parameters:
      input_path (str): Path to the input video file.
      output_path (str): Path for the output video file.
      start_time (str): Start time for trimming (e.g., "00:00:10").
      duration (str): Duration of the output segment (e.g., "00:00:30").
       preset (str): Encoding preset for H.265 (e.g., "slow", "veryslow").
    """
    # Create temp file for log
    stats_file = tempfile.NamedTemporaryFile(suffix=".log", delete=False).name

    fps_param = f", fps={fps}" if fps is not None else ""

    if smart_remove_duplicates:
        decimate_param = f", mpdecimate, setpts=N/({fps}*TB)"
    elif remove_duplicates:
        decimate_param = ", mpdecimate"
    else:
        decimate_param = ""

    # Common parameters
    common_params = [
        "-ss",
        start_time,  # Start time for trimming
        "-t",
        duration,  # Duration of the output
        "-vf",
        f"crop={width}:{height}:(iw-{width})/2:(ih-{height})/2{fps_param}{decimate_param}",
        # crop to top
        # f"crop={width}:{height}:(iw-{width})/2:0{fps_param}{decimate_param}",
    ]

    # Set pass parameters based on codec
    if codec == "libx265":
        # For H.265/HEVC
        first_pass_params = [
            "-x265-params",
            f"pass=1:stats={stats_file}",
        ]
        second_pass_params = [
            "-x265-params",
            f"pass=2:stats={stats_file}",
        ]
    else:
        # For H.264 and other codecs
        first_pass_params = [
            "-pass",
            "1",
            "-passlogfile",
            stats_file,
        ]
        second_pass_params = [
            "-pass",
            "2",
            "-passlogfile",
            stats_file,
        ]

    # First pass - analyze the video
    print("Starting first pass...")
    first_pass_cmd = (
        ["ffmpeg", "-y", "-i", input_path]
        + common_params
        + [
            "-c:v",
            codec,
            "-b:v",
            target_bitrate,
            "-maxrate",
            max_bitrate,
            "-bufsize",
            bufsize,
            "-preset",
            preset,
        ]
        + first_pass_params
        + [
            "-an",
            "-f",
            "null",
            "/dev/null",
        ]
    )

    # Second pass - encode with the analysis
    second_pass_cmd = (
        ["ffmpeg", "-y", "-i", input_path]
        + common_params
        + [
            "-c:v",
            codec,  # Video codec
            "-b:v",
            target_bitrate,
            "-maxrate",
            max_bitrate,
            "-bufsize",
            bufsize,
            "-preset",
            preset,  # Encoding preset
        ]
        + second_pass_params
        + [
            "-pix_fmt",
            "yuv420p",  # Pixel format for compatibility
            "-tag:v",
            (
                "hvc1" if codec == "libx265" else "avc1"
            ),  # Use hvc1 tag for better Mac compatibility
            "-movflags",
            "+faststart",  # Move metadata to beginning for faster start
            # "-an",  # Remove audio stream
            output_path,
        ]
    )

    # Run the commands
    try:
        # First pass
        subprocess.run(first_pass_cmd, check=True)
        print("First pass completed successfully.")

        # Second pass
        subprocess.run(second_pass_cmd, check=True)
        print(f"Second pass completed. Successfully processed: {output_path}")

        # Clean up stats file
        os.remove(stats_file)
    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    # Change these paths to match your file locations
    input_video = current_dir + "/image_input/solar-overview.mp4"
    output_video = current_dir + "/optimized_output/solar-overview-2.mp4"

    # Set the trimming parameters (e.g., start at 10 seconds, output 30 seconds long)
    start_time = "00:00:00"
    duration = "01:00:11"
    # start_time = "00:00:09.11"
    # duration = "00:00:9"

    trim_and_optimize_video(
        input_video,
        output_video,
        start_time,
        duration,
    )
