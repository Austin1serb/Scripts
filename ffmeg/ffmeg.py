import subprocess
import os

# Directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))


def process_videos(
    video_format="mp4",
    image_format="webp",
    video_extensions=(".mp4", ".mov", ".avi", ".mkv", ".webm"),
    target_width=4000,
    crf=18,
    preset="veryfast",
    image_quality=20,
    overwrite=False,
    fps=30,
):
    """
    Process and optimize videos in the current directory, then extract a poster image.
    Uses two-pass encoding for WebM (VP9), single-pass for MP4 (H.264).
    :param video_format: Output video format ("mp4" or "webm")
    :param image_format: Output image format ("jpg", "png", "webp", etc.)
    :param video_extensions: Tuple of video extensions to process
    :param target_width: Target width for output videos (height is computed)
    :param crf: 4-51, 18 nearly lossless, 28 sweet spot lower = better quality
    :param preset: Preset for H.264 encoding (e.g., "veryslow")
    :param image_quality: Quality for poster image (0-100)
    :param overwrite: Overwrite existing files (True) or skip (False)
    :param fps: Target frames per second (optional)
    """

    # Scale filter: Keep width at target_width, compute height so aspect is preserved
    scale_filter = f"scale={target_width}:trunc(ow/a/2)*2" if target_width else ""

    # Add fps to filter chain if specified
    if fps:
        filter_chain = f"{scale_filter},fps={fps}" if scale_filter else f"fps={fps}"
    else:
        filter_chain = scale_filter

    for filename in os.listdir(current_dir):
        if filename.lower().endswith(video_extensions):
            input_video = os.path.join(current_dir, filename)
            base_name, _ = os.path.splitext(filename)

            output_video = os.path.join(
                current_dir, f"{base_name}-mobile.{video_format}"
            )
            output_image = os.path.join(
                current_dir, f"{base_name}-poster-mobile.{image_format}"
            )

            # Skip if already processed (unless overwrite=True)
            if (
                not overwrite
                and os.path.exists(output_video)
                and os.path.exists(output_image)
            ):
                print(f"Skipping {filename} - output files exist.")
                continue

            # Decide on encoding approach based on format
            if video_format.lower() == "mp4":
                # ------------------------ MP4: Single-pass H.264 ------------------------
                video_cmd = [
                    "ffmpeg",
                    "-i",
                    input_video,
                    "-vf",
                    filter_chain,
                    "-c:v",
                    "libx264",
                    "-crf",
                    str(crf),
                    "-preset",
                    preset,
                    "-movflags",
                    "+faststart",
                    "-pix_fmt",
                    "yuv420p",
                ]

                if overwrite:
                    video_cmd += ["-y"]  # Overwrite
                else:
                    video_cmd += ["-n"]  # No overwrite

                video_cmd.append(output_video)

                # Run single-pass H.264 encode
                try:
                    subprocess.run(video_cmd, check=True)
                    print(
                        f"[MP4/H.264 single-pass] {filename} -> {output_video} "
                        f"(CRF={crf}, preset={preset})"
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error processing MP4 video {filename}: {e}")
                    continue

            elif video_format.lower() == "webm":
                # ------------------------ WebM: Two-pass VP9 ------------------------
                # We'll store pass log files with a unique name (base_name_log)
                passlogfile = os.path.join(current_dir, f"{base_name}_passlog")

                # -- First Pass --
                # We use -f null /dev/null to discard output but gather stats
                pass1_cmd = [
                    "ffmpeg",
                    "-i",
                    input_video,
                    "-vf",
                    filter_chain,
                    "-c:v",
                    "libvpx-vp9",
                    "-b:v",
                    "0",  # CRF-based, no target bitrate
                    "-crf",
                    str(crf),
                    "-pix_fmt",
                    "yuv420p",
                    "-deadline",
                    "best",
                    "-cpu-used",
                    "0",
                    "-lag-in-frames",
                    "40",
                    "-pass",
                    "1",
                    "-passlogfile",
                    passlogfile,
                    "-an",  # No audio in first pass
                    "-f",
                    "null",  # Output goes nowhere
                    "-",
                ]

                # Overwrite logic
                if overwrite:
                    pass1_cmd.insert(1, "-y")
                else:
                    pass1_cmd.insert(1, "-n")

                # First pass run
                try:
                    subprocess.run(pass1_cmd, check=True)
                    print(f"[WebM/VP9 1st pass] {filename}")
                except subprocess.CalledProcessError as e:
                    print(f"Error in 1st pass for {filename}: {e}")
                    continue

                # -- Second Pass --
                pass2_cmd = [
                    # Command-line utility: ffmpeg
                    "ffmpeg",
                    # Specify the input video file path
                    "-i",
                    input_video,
                    # Apply the scale filter to resize video (maintains aspect ratio, even dimensions)
                    "-vf",
                    filter_chain,
                    # Specify the VP9 video codec
                    "-c:v",
                    "libvpx-vp9",
                    # Set the target bitrate to 0 for CRF-based (variable) bitrate
                    "-b:v",
                    "0",
                    # Use CRF mode to control quality (0–63 range, lower = better quality)
                    "-crf",
                    str(crf),
                    # Set pixel format to 8-bit 4:2:0 for broad compatibility
                    "-pix_fmt",
                    "yuv420p",
                    # Use the slowest preset for best compression
                    "-deadline",
                    "best",
                    # CPU efficiency level (0 = slowest but highest compression)
                    "-cpu-used",
                    "0",
                    # Indicate this is the second pass of two-pass encoding
                    "-pass",
                    "2",
                    # Specify the pass log file to use (generated in the first pass)
                    "-passlogfile",
                    passlogfile,
                    # Disable audio (video-only output)
                    "-an",
                ]

                if overwrite:
                    pass2_cmd += ["-y"]
                else:
                    pass2_cmd += ["-n"]

                pass2_cmd.append(output_video)

                # Second pass run
                try:
                    subprocess.run(pass2_cmd, check=True)
                    print(
                        f"[WebM/VP9 2nd pass] {filename} -> {output_video} "
                        f"(CRF={crf}, two-pass, best deadline)"
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error in 2nd pass for {filename}: {e}")
                    continue

                finally:
                    # Clean up passlog files if they exist
                    # Clean up FFmpeg-generated pass log files
                    for suffix in ("-0.log", "-0.log.mbtree"):
                        lf = f"{passlogfile}{suffix}"
                        if os.path.exists(lf):
                            os.remove(lf)

            else:
                # ------------------------ Fallback: MP4 Single-pass ------------------------
                video_cmd = [
                    "ffmpeg",
                    "-i",
                    input_video,
                    "-vf",
                    filter_chain,
                    "-c:v",
                    "libx264",
                    "-crf",
                    str(crf),
                    "-preset",
                    preset,
                    "-movflags",
                    "+faststart",
                    "-pix_fmt",
                    "yuv420p",
                ]

                if overwrite:
                    video_cmd += ["-y"]
                else:
                    video_cmd += ["-n"]

                video_cmd.append(output_video)
                try:
                    subprocess.run(video_cmd, check=True)
                    print(
                        f"[Fallback H.264] {filename} -> {output_video} "
                        f"(CRF={crf}, preset={preset})"
                    )
                except subprocess.CalledProcessError as e:
                    print(f"Error in fallback for {filename}: {e}")
                    continue

            # --- Poster Extraction ---
            # Use the newly created video for the poster image (1st frame)
            image_cmd = [
                "ffmpeg",
                "-i",
                output_video,
                "-vf",
                f"select=eq(n\\,0),{scale_filter}",
                "-q:v",
                str(image_quality),
                "-vframes",
                "1",
            ]
            if overwrite:
                image_cmd += ["-y"]
            else:
                image_cmd += ["-n"]

            image_cmd.append(output_image)

            try:
                subprocess.run(image_cmd, check=True)
                print(f"Extracted poster: {filename} -> {output_image}")
            except subprocess.CalledProcessError as e:
                print(f"Error extracting poster from {filename}: {e}")


if __name__ == "__main__":
    process_videos(
        video_format="webm",  # "mp4" -> single-pass H.264, "webm" -> two-pass VP9
        image_format="webp",
        target_width=1080,
        crf=25,
        preset="veryslow",  # Only affects H.264. For VP9, we use -deadline best
        image_quality=20,
        overwrite=False,
        fps=60,  # Set default output fps to 30
    )
