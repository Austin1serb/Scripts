import os

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

                    # Always use the configured output format
                    output_format = self.config["output_format"]

                    # Setup paths
                    base_name = os.path.splitext(filename)[0]

                    # Normalize jpg/jpeg for comparison (they're the same format)
                    normalized_original = (
                        "jpg" if original_format in ["jpg", "jpeg"] else original_format
                    )
                    normalized_output = (
                        "jpg" if output_format in ["jpg", "jpeg"] else output_format
                    )

                    # Check if format is actually changing
                    is_format_change = normalized_output != normalized_original

                    if is_format_change:
                        # Create new filename with new format
                        temp_path = os.path.join(
                            folder_path, f"{base_name}_temp.{output_format}"
                        )
                        final_path = os.path.join(
                            folder_path, f"{base_name}.{output_format}"
                        )
                    else:
                        # Keep same filename, use temp for processing
                        temp_path = file_path + ".tmp"
                        final_path = file_path

                    # Use the new auto-detect compression method
                    success = self.compressor.compress_with_auto_detect(
                        file_path, temp_path, output_format
                    )

                    if success:
                        original_size = os.path.getsize(file_path)
                        compressed_size = os.path.getsize(temp_path)
                        reduction = (1 - compressed_size / original_size) * 100
                        bytes_saved = original_size - compressed_size

                        # Replace original with compressed version
                        os.remove(file_path)
                        os.rename(temp_path, final_path)

                        # Show output filename if it changed
                        if is_format_change and final_path != file_path:
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

            except Exception as e:
                print(f"  ✗ Error processing {filename}: {e}")
                self.failed_count += 1

    def process_directory_tree(self, root_path: str) -> None:
        """Recursively process all folders and subfolders, overwriting images in place."""
        print(f"Starting batch compression of: {root_path}")
        print(f"Output format: {self.config['output_format'].upper()}")

        # Show which dimension is being used
        if self.config.get("target_width"):
            print(
                f"Target dimension: Width = {self.config['target_width']}px (maintaining aspect ratio)"
            )
        elif self.config.get("target_height"):
            print(
                f"Target dimension: Height = {self.config['target_height']}px (maintaining aspect ratio)"
            )

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
        # General settings - USE ONLY ONE: target_width OR target_height (not both)
        "target_width": None,  # Resize to this width, maintaining aspect ratio
        "target_height": 1080,  # OR use this for height (e.g., 800 for tall images)
        "output_format": "webp",
        "max_colors": 1028,  # Set to None for no color reduction
        # Metadata handling
        "preserve_exif": True,  # Set to True to preserve EXIF metadata
        # Transparency handling
        "preserve_transparency": False,
        # PNG specific
        "png_compression_level": 4,  # 0-9
        "use_pngquant": False,  # pngquant is a lossy compression tool
        "pngquant_quality": "65-80",  # 0-100
        # JPEG/JPG specific
        "jpeg_quality": 65,  # 0-100
        # WebP specific
        "webp_quality": 65,  # 0-100 higher is better
        "webp_lossless": False,
        # GIF specific
        "gif_colors": 128,
        # AVIF specific
        "avif_quality": 10,  # 0-100
        # SVG specific
        "convert_svg_to_png": False,
    }

    # Set your input path here
    input_directory = "/Users/austinserb/Desktop/rc-concrete/public/projects/beautiful-large-driveway"  # Change this to your folder path

    # Validate paths
    if not os.path.isdir(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist!")
        return

    # Run batch compression
    batch_compressor = BatchImageCompressor(config)
    batch_compressor.process_directory_tree(input_directory)


if __name__ == "__main__":
    main()
