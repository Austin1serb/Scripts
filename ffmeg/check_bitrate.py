import subprocess
import os
import json
import re


def get_video_bitrate(input_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=bit_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                input_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        bitrate_str = result.stdout.strip()
        if bitrate_str:
            bitrate = int(bitrate_str)
            # Convert to megabits per second for convenience
            mbps = bitrate / 1_000_000
            return mbps, bitrate  # returns both in Mbps and bps
        else:
            return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None, None


def get_bitrate_per_second(input_path):
    """Get the bitrate for each second of the video using ffprobe."""
    try:
        # Get video duration first
        duration_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_path,
        ]
        duration_result = subprocess.run(
            duration_cmd, capture_output=True, text=True, check=True
        )
        duration = float(duration_result.stdout.strip())

        # Use ffprobe with the -f segment_frames option to analyze the video
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-hide_banner",
            "-select_streams",
            "v:0",
            "-show_entries",
            "packet=pts_time,size",
            "-of",
            "csv=p=0",
            input_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse the output to get bitrate per second
        lines = result.stdout.strip().split("\n")

        # Create a dictionary to store packets by second
        packets_by_second = {}

        for line in lines:
            parts = line.split(",")
            if len(parts) == 2:
                try:
                    pts_time = float(parts[0])
                    size = int(parts[1])

                    # Round down to get the second
                    second = int(pts_time)

                    if second not in packets_by_second:
                        packets_by_second[second] = []

                    packets_by_second[second].append(size)
                except (ValueError, IndexError):
                    continue

        # Calculate bitrate for each second
        bitrates = {}
        for second, packets in packets_by_second.items():
            # Total bits for this second
            total_bits = sum(packets) * 8

            # Convert to Mbps
            mbps = total_bits / 1_000_000
            bitrates[second] = mbps

        # Fill in missing seconds with 0
        for second in range(int(duration) + 1):
            if second not in bitrates:
                bitrates[second] = 0

        return bitrates, duration

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None, None


# Example usage:
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_video = os.path.join(current_dir, "image_input/solar-overview.mp4")

    # Get average bitrate
    mbps, bps = get_video_bitrate(input_video)
    if mbps:
        print(f"Average bitrate: {mbps:.2f} Mbps ({bps} bps)")
    else:
        print("Bitrate information not found.")

    # Get bitrate per second
    print("\nAnalyzing bitrate per second...")
    bitrates, duration = get_bitrate_per_second(input_video)

    if bitrates:
        print(f"Video duration: {duration:.2f} seconds")
        print("\nBitrate per second (Mbps):")
        for second, bitrate in sorted(bitrates.items()):
            print(f"Second {second}: {bitrate:.2f} Mbps")
    else:
        print("Failed to analyze bitrate per second.")
