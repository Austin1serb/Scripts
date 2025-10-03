import subprocess
import os
import shutil


def process_images_and_videos():
    # Define file extensions for images and videos
    image_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".bmp",
        ".gif",
        "avif",
        "svg",
        "heic",
        ".ico",
    )
    video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".webm")

    # Settings for images
    target_width = 520  # Resize width (maintain aspect ratio)
    quality = 50  # lower = better quality
    output_format = "jpeg"  # Output image format
    max_colors = None  # Limit colors (None = no limit)
    grayscale_percentage = None  # Grayscale conversion percentage (None = no grayscale)
    icon = True
    # Settings for video frame extraction
    frames_to_extract = 1  # Number of frames to extract per video
    frame_interval = 1  # Time interval in seconds between frames (for multiple frames)
    lossless = False

    current_dir = os.path.dirname(os.path.abspath(__file__))

    image_input_dir = os.path.join(current_dir, "image_input")

    # Create output directory path
    output_dir = os.path.join(current_dir, "optimized_output")

    # Create or clean the output directory
    if os.path.exists(output_dir):
        # Delete all contents
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    else:
        # Create the directory if it doesn't exist
        os.makedirs(output_dir)

    print(f"Processing images and videos. Output format: {output_format.upper()}.")
    print(f"Optimized files will be saved to: {output_dir}")

    for filename in os.listdir(image_input_dir):
        file_path = os.path.join(image_input_dir, filename)
        base_name, extension = os.path.splitext(filename)

        # Process images
        if filename.lower().endswith(image_extensions):
            output_image = os.path.join(output_dir, f"{base_name}.{output_format}")
            try:
                # Build the ImageMagick command for image optimization
                command = [
                    "magick",
                    file_path,
                    "-resize",
                    f"{target_width}x>",  # Resize width
                    "-quality",
                    str(quality),  # Set compression quality
                ]
                if icon:
                    command.extend(["-define", f"webp:lossless={lossless}"])
                    command.extend(["-sampling-factor", "4:2:0"])
                    command.extend(["-strip"])

                # Add color reduction if specified
                if max_colors is not None:
                    command.extend(["-colors", str(max_colors)])

                # Add grayscale conversion if specified
                if grayscale_percentage is not None:
                    command.extend(
                        [
                            "-set",
                            "colorspace",
                            "Gray",
                            "-separate",
                            "-average",
                            "-evaluate",
                            "Multiply",
                            str(grayscale_percentage / 100),
                        ]
                    )

                # Specify the output file
                command.append(output_image)

                # Run the ImageMagick command
                subprocess.run(command, check=True)

                print(
                    f"Optimized image: {filename} -> {os.path.basename(output_image)} (Quality={quality}, Format={output_format.upper()})"
                )

            except subprocess.CalledProcessError as e:
                print(f"Error processing image {filename}: {e}")
                continue

        # Process videos
        elif filename.lower().endswith(video_extensions):
            for i in range(frames_to_extract):
                output_frame = os.path.join(
                    output_dir, f"{base_name}-frame-{i+1}.{output_format}"
                )
                try:
                    # Build the FFmpeg command for extracting video frames
                    ffmpeg_command = [
                        "ffmpeg",
                        "-i",
                        file_path,  # Input video
                        "-vf",
                        f"select=not(mod(n\\,{frame_interval * 25})),scale={target_width}:-1",  # Select frame and scale
                        "-vframes",
                        "1",  # Limit to 1 frame per command
                        "-compression_level",
                        "6",  # WebP compression level (0-6)
                        "-q:v",
                        str(quality),  # Set frame quality
                        output_frame,  # Output file
                    ]
                    # Run the FFmpeg command
                    subprocess.run(ffmpeg_command, check=True)

                    print(
                        f"Extracted frame {i+1} from video: {filename} -> {os.path.basename(output_frame)}"
                    )

                except subprocess.CalledProcessError as e:
                    print(f"Error extracting frame from video {filename}: {e}")
                    break


if __name__ == "__main__":
    process_images_and_videos()


# import os
# import base64


# def encode_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode("utf-8")


# image_input_dir = os.path.dirname(os.path.abspath(__file__))
# image_path = os.path.join(image_input_dir, "placeholder.webp")
# base64_string = encode_to_base64(image_path)
# print(f"data:image/webp;base64,{base64_string}")
