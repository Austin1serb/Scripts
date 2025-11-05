import os
import subprocess

from ffmeg_image_new import ImageCompressor


class BatchImageCompressor:
    def __init__(self, config: dict):
        self.config = config
        self.compressor = ImageCompressor(config)
        self.processed_count = 0
        self.failed_count = 0
        self.total_bytes_saved = 0

    def compress_folder(self, folder_path: str) -> None:
        """Compress all images in a single folder, overwriting originals."""
        image_extensions = (
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".bmp",
            ".gif",
            ".avif",
            ".svg",
            ".heic",
            ".ico",
        )
        video_extensions = (".mp4", ".mov", ".avi", ".mkv", ".flv")

        print(f"\nProcessing folder: {folder_path}")

        # Process images in this folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Skip if it's a directory (we handle those separately)
            if os.path.isdir(file_path):
                continue

            try:
                if filename.lower().endswith(image_extensions):
                    # Get the original file extension
                    file_ext = os.path.splitext(filename)[1].lower()
                    original_format = file_ext[1:]  # Remove the dot

                    # Check if file is actually HEIC (even if misnamed as .jpg)
                    is_heic = original_format == "heic"
                    if not is_heic:
                        # Check actual file type
                        try:
                            result = subprocess.run(
                                ["file", "-b", file_path],
                                capture_output=True,
                                text=True,
                                check=True,
                            )
                            if "HEIF" in result.stdout or "HEIC" in result.stdout:
                                is_heic = True
                        except Exception:
                            pass  # file command might not be available

                    # For HEIC files (detected or named), convert to configured output format
                    if is_heic:
                        output_format = self.config["output_format"]
                        base_name = os.path.splitext(filename)[0]
                        # Use proper extension for temp file (ffmpeg needs correct extension)
                        temp_path = os.path.join(
                            folder_path, f"{base_name}_temp.{output_format}"
                        )
                        final_path = os.path.join(
                            folder_path, f"{base_name}.{output_format}"
                        )
                    else:
                        # For non-HEIC files, keep the same format
                        output_format = original_format
                        temp_path = file_path + ".tmp"
                        final_path = file_path

                    # Route to appropriate compression function based on format
                    format_handlers = {
                        "png": self.compressor.compress_png,
                        "jpg": self.compressor.compress_jpeg,
                        "jpeg": self.compressor.compress_jpeg,
                        "webp": self.compressor.compress_webp,
                        "gif": self.compressor.compress_gif,
                        "avif": self.compressor.compress_avif,
                        "svg": self.compressor.compress_svg,
                        "heic": self.compressor.compress_jpeg,
                    }

                    # Use the handler for the detected format (HEIC uses JPEG handler)
                    handler_format = "heic" if is_heic else original_format
                    handler = format_handlers.get(handler_format.lower())

                    if handler:
                        success = handler(file_path, temp_path)
                        if success:
                            original_size = os.path.getsize(file_path)
                            compressed_size = os.path.getsize(temp_path)
                            reduction = (1 - compressed_size / original_size) * 100
                            bytes_saved = original_size - compressed_size

                            # Replace original with compressed version
                            os.remove(file_path)
                            os.rename(temp_path, final_path)

                            # Show output filename if it changed
                            if is_heic and final_path != file_path:
                                final_name = os.path.basename(final_path)
                                print(f"  ✓ {filename} → {final_name}")
                            else:
                                print(f"  ✓ {filename}")

                            print(
                                f"    Size: {original_size:,} -> {compressed_size:,} bytes ({reduction:.1f}% reduction)"
                            )
                            self.processed_count += 1
                            self.total_bytes_saved += bytes_saved
                        else:
                            print(f"  ✗ Failed to compress {filename}")
                            # Clean up temp file if it exists
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            self.failed_count += 1
                    else:
                        print(f"  ✗ Unsupported format: {handler_format}")
                        self.failed_count += 1

                elif filename.lower().endswith(video_extensions):
                    # For videos, extract frame and replace video with image
                    base_name = os.path.splitext(filename)[0]
                    output_format = self.config["output_format"]
                    temp_path = os.path.join(
                        folder_path, f"{base_name}_temp.{output_format}"
                    )

                    success = self.compressor.extract_video_frame(
                        file_path,
                        temp_path,
                        0,  # First frame
                    )
                    if success:
                        # Get original video size before removing it
                        original_size = os.path.getsize(file_path)
                        # Remove video and rename extracted frame
                        os.remove(file_path)
                        final_path = os.path.join(
                            folder_path, f"{base_name}.{output_format}"
                        )
                        os.rename(temp_path, final_path)
                        # Get the new image size
                        image_size = os.path.getsize(final_path)
                        bytes_saved = original_size - image_size

                        print(
                            f"  ✓ {filename} -> {base_name}.{output_format} (extracted frame)"
                        )
                        self.processed_count += 1
                        self.total_bytes_saved += bytes_saved
                    else:
                        print(f"  ✗ Failed to extract frame from {filename}")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        self.failed_count += 1

            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                self.failed_count += 1

    def process_directory_tree(self, root_path: str) -> None:
        """Recursively process all folders and subfolders, overwriting images in place."""
        print(f"Starting batch compression of: {root_path}")
        print(f"Output format: {self.config['output_format'].upper()}")
        print(
            f"EXIF metadata: {'Preserved' if self.config.get('preserve_exif', False) else 'Removed'}"
        )
        print(
            f"Transparency: {'Preserved' if self.config.get('preserve_transparency', True) else 'Removed'}"
        )
        print("-" * 80)

        # Walk through all directories
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Only process if there are files in this directory
            if filenames:
                self.compress_folder(dirpath)

        # Print summary
        print("\n" + "=" * 80)
        print("BATCH COMPRESSION COMPLETE")
        print(f"Successfully processed: {self.processed_count} files")
        print(f"Failed: {self.failed_count} files")
        print(f"Total: {self.processed_count + self.failed_count} files")

        # Format total bytes saved
        if self.total_bytes_saved >= 1024**3:  # >= 1 GB
            space_saved = self.total_bytes_saved / (1024**3)
            print(
                f"Total space saved: {space_saved:.2f} GB ({self.total_bytes_saved:,} bytes)"
            )
        elif self.total_bytes_saved >= 1024**2:  # >= 1 MB
            space_saved = self.total_bytes_saved / (1024**2)
            print(
                f"Total space saved: {space_saved:.2f} MB ({self.total_bytes_saved:,} bytes)"
            )
        elif self.total_bytes_saved >= 1024:  # >= 1 KB
            space_saved = self.total_bytes_saved / 1024
            print(
                f"Total space saved: {space_saved:.2f} KB ({self.total_bytes_saved:,} bytes)"
            )
        else:
            print(f"Total space saved: {self.total_bytes_saved:,} bytes")

        print("=" * 80)


def main():
    # Configuration - same as in image_compressor.py
    config = {
        # General settings
        "target_width": 1200,
        "output_format": "jpg",
        "max_colors": None,  # Set to None for no color reduction
        # Metadata handling
        "preserve_exif": True,  # Set to True to preserve EXIF metadata
        # Transparency handling
        "preserve_transparency": False,
        # PNG specific
        "png_compression_level": 4,  # 0-9
        "use_pngquant": False,  # pngquant is a lossy compression tool
        "pngquant_quality": "65-80",  # 0-100
        # JPEG/JPG specific
        "jpeg_quality": 75,  # 0-100
        # WebP specific
        "webp_quality": 40,  # 0-100 higher is better
        "webp_lossless": False,
        # GIF specific
        "gif_colors": 128,
        # AVIF specific
        "avif_quality": 10,  # 0-100
        # SVG specific
        "convert_svg_to_png": False,
        # Video frame extraction
        "frames_to_extract": 1,
        "frame_interval": 25,  # frames
    }

    # Set your input path here
    input_directory = "/Users/austinserb/Desktop/rc-concrete/public/projects/"  # Change this to your folder path

    # Validate paths
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist!")
        return

    # Run batch compression
    batch_compressor = BatchImageCompressor(config)
    batch_compressor.process_directory_tree(input_directory)


if __name__ == "__main__":
    main()
