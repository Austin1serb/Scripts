import subprocess
import os
import shutil
from typing import Dict, Any


class ImageCompressor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.image_input_dir = os.path.join(self.current_dir, "image_input")
        self.output_dir = os.path.join(self.current_dir, "optimized_output")

        # Validate that only one dimension is specified
        self._validate_dimensions()

    def _validate_dimensions(self):
        """Validate that only one of target_width or target_height is specified."""
        has_width = self.config.get("target_width") is not None
        has_height = self.config.get("target_height") is not None

        if has_width and has_height:
            raise ValueError(
                "Cannot specify both target_width and target_height. Please choose only one."
            )

        if not has_width and not has_height:
            raise ValueError("Must specify either target_width or target_height.")

    def _get_resize_param(self) -> str:
        """Get the appropriate resize parameter based on config."""
        if self.config.get("target_width") is not None:
            # Resize by width, maintain aspect ratio, only if larger
            return f"{self.config['target_width']}x>"
        elif self.config.get("target_height") is not None:
            # Resize by height, maintain aspect ratio, only if larger
            return f"x{self.config['target_height']}>"
        else:
            # Fallback (should not reach here due to validation)
            return "1200x>"

    def _add_metadata_handling(self, command: list):
        """Add metadata handling based on config."""
        if self.config.get("preserve_exif", False):
            # Preserve EXIF and other profiles
            command.extend(["+profile", "!iptc"])  # Keep all profiles except IPTC
        else:
            command.append("-strip")

    def _detect_actual_format(self, input_path: str) -> str:
        """Detect the actual file format regardless of extension."""
        try:
            result = subprocess.run(
                ["file", "-b", "--mime-type", input_path],
                capture_output=True,
                text=True,
                check=True,
            )
            mime_type = result.stdout.strip()

            # Map MIME types to format names
            mime_map = {
                "image/heic": "heic",
                "image/heif": "heic",
                "image/jpeg": "jpeg",
                "image/png": "png",
                "image/webp": "webp",
                "image/gif": "gif",
                "image/avif": "avif",
                "image/svg+xml": "svg",
                "image/x-icon": "ico",
                "image/bmp": "bmp",
            }

            return mime_map.get(mime_type, "unknown")
        except Exception:
            # Fallback to extension-based detection
            ext = os.path.splitext(input_path)[1].lower().lstrip(".")
            return ext if ext else "unknown"

    def _handle_transparency(self, command: list, input_path: str, output_format: str):
        """Add transparency handling to ImageMagick command."""
        # Check if we need to handle transparency
        if self.config.get("preserve_transparency", True):
            # For formats that support transparency
            if output_format.lower() in ["png", "webp", "gif", "avif"]:
                command.extend(["-background", "none", "-alpha", "set"])
            else:
                # For formats that don't support transparency (JPEG)
                if self.config.get("background_color"):
                    # Use specified background color
                    command.extend(
                        [
                            "-background",
                            self.config["background_color"],
                            "-alpha",
                            "remove",
                        ]
                    )
                else:
                    # Default white background
                    command.extend(["-background", "white", "-alpha", "remove"])
        else:
            # Remove transparency with specified background
            bg_color = self.config.get("background_color", "white")
            command.extend(["-background", bg_color, "-alpha", "remove"])

    def compress_png(self, input_path: str, output_path: str) -> bool:
        """Compress PNG images with lossless and optional lossy compression."""
        try:
            command = [
                "magick",
                input_path,
                "-auto-orient",  # Preserve correct orientation from EXIF
            ]

            # Handle transparency first
            self._handle_transparency(command, input_path, "png")

            command.extend(
                [
                    "-resize",
                    self._get_resize_param(),
                    "-quality",
                    f"{self.config['png_compression_level']}9",
                    "-define",
                    f"png:compression-level={self.config['png_compression_level']}",
                    "-define",
                    "png:compression-strategy=1",
                    "-define",
                    "png:compression-filter=5",
                ]
            )

            # Add metadata handling
            self._add_metadata_handling(command)

            # Add color reduction if specified
            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])
                # For PNG with limited colors, use PNG8 format if not preserving transparency
                if not self.config.get("preserve_transparency", True):
                    command.extend(["-type", "Palette"])
                else:
                    # Use PNG32 to preserve transparency with color reduction
                    command.extend(["-define", "png:color-type=6"])

            # Force PNG output format (handles misnamed files)
            command.extend(["-format", "png"])
            command.append(output_path)
            subprocess.run(command, check=True)

            # Apply lossy compression with pngquant if enabled
            if self.config.get("use_pngquant", True):
                try:
                    pngquant_command = [
                        "pngquant",
                        "--quality",
                        self.config.get("pngquant_quality", "65-80"),
                        "--speed",
                        "1",
                        "--force",
                        "--output",
                        output_path,
                    ]

                    # Add transparency handling for pngquant
                    if not self.config.get("preserve_transparency", True):
                        pngquant_command.append("--strip")

                    pngquant_command.append(output_path)

                    subprocess.run(pngquant_command, check=True)
                    print(f"Applied pngquant lossy compression")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("pngquant not available, using lossless compression only")

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing PNG: {e}")
            return False

    def compress_jpeg(self, input_path: str, output_path: str) -> bool:
        """Compress JPEG images with lossy compression."""
        try:
            # Use ImageMagick for JPEG compression
            command = [
                "magick",
                input_path,
                "-auto-orient",  # CRITICAL: Preserve correct orientation from EXIF
                "-background",
                self.config.get("background_color", "white"),
                "-alpha",
                "remove",
                "-resize",
                self._get_resize_param(),
                "-quality",
                str(self.config.get("jpeg_quality", 85)),
                "-sampling-factor",
                "4:2:0",
                "-interlace",
                "Plane",
                "-colorspace",
                "sRGB",
            ]

            # Add metadata handling
            self._add_metadata_handling(command)

            # Optional color reduction
            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])

            # Force JPEG format output
            command.extend(["-format", "jpeg"])
            command.append(output_path)

            subprocess.run(command, check=True, capture_output=True, text=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing JPEG: {e}")
            if hasattr(e, "stderr") and e.stderr:
                error_msg = (
                    e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
                )
                print(f"Error details: {error_msg}")
            elif hasattr(e, "stdout") and e.stdout:
                error_msg = (
                    e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout
                )
                print(f"Output: {error_msg}")
            return False

    def compress_webp(self, input_path: str, output_path: str) -> bool:
        """Compress WebP images with lossy or lossless compression."""
        try:
            command = [
                "magick",
                input_path,
                "-auto-orient",  # Preserve correct orientation from EXIF
            ]

            # Handle transparency
            self._handle_transparency(command, input_path, "webp")

            command.extend(
                [
                    "-resize",
                    self._get_resize_param(),
                    "-quality",
                    str(self.config.get("webp_quality", 80)),
                    "-define",
                    f"webp:lossless={'true' if self.config.get('webp_lossless', False) else 'false'}",
                    "-define",
                    "webp:method=6",  # Slowest but best compression
                    "-define",
                    "webp:auto-filter=true",
                ]
            )

            # Add metadata handling
            self._add_metadata_handling(command)

            # WebP-specific transparency settings
            if self.config.get("preserve_transparency", True):
                command.extend(["-define", "webp:alpha-quality=100"])

            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])

            # Force WebP output format (handles misnamed files)
            command.extend(["-format", "webp"])
            command.append(output_path)
            subprocess.run(command, check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing WebP: {e}")
            return False

    def compress_gif(self, input_path: str, output_path: str) -> bool:
        """Compress GIF images with color reduction and optimization."""
        try:
            command = [
                "magick",
                input_path,
            ]

            # Handle transparency for GIF
            self._handle_transparency(command, input_path, "gif")

            command.extend(
                [
                    "-resize",
                    self._get_resize_param(),
                    "-layers",
                    "Optimize",  # Optimize GIF frames
                    "-colors",
                    str(
                        self.config.get("gif_colors", 128)
                    ),  # GIFs benefit from color reduction
                ]
            )

            # Add metadata handling
            self._add_metadata_handling(command)

            # Apply dithering for better quality with fewer colors
            command.extend(["-dither", "FloydSteinberg"])

            # GIF transparency handling
            if self.config.get("preserve_transparency", True):
                command.extend(["-dispose", "Background"])

            # Force GIF output format (handles misnamed files)
            command.extend(["-format", "gif"])
            command.append(output_path)
            subprocess.run(command, check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing GIF: {e}")
            return False

    def compress_avif(self, input_path: str, output_path: str) -> bool:
        """Compress AVIF images (requires ImageMagick with AVIF support)."""
        try:
            command = [
                "magick",
                input_path,
            ]

            # Handle transparency
            self._handle_transparency(command, input_path, "avif")

            command.extend(
                [
                    "-resize",
                    self._get_resize_param(),
                    "-quality",
                    str(self.config.get("avif_quality", 50)),
                    "-define",
                    "heic:speed=0",  # Slowest but best compression
                ]
            )

            # Add metadata handling
            self._add_metadata_handling(command)

            # Force AVIF output format (handles misnamed files)
            command.extend(["-format", "avif"])
            command.append(output_path)
            subprocess.run(command, check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing AVIF: {e}")
            return False

    def compress_svg(self, input_path: str, output_path: str) -> bool:
        """Optimize SVG files using svgo if available."""
        try:
            # First try svgo for better SVG optimization
            svgo_command = [
                "svgo",
                input_path,
                "-o",
                output_path,
                "--multipass",
                "--precision=2",
            ]
            subprocess.run(svgo_command, check=True)
            print("Optimized SVG using svgo")
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to simple copy or ImageMagick conversion
            try:
                if self.config.get("convert_svg_to_png", False):
                    # Convert SVG to PNG
                    command = [
                        "magick",
                        "-density",
                        "300",  # Higher density for better quality
                        "-background",
                        (
                            "none"
                            if self.config.get("preserve_transparency", True)
                            else self.config.get("background_color", "white")
                        ),
                        input_path,
                        "-resize",
                        self._get_resize_param(),
                        output_path.replace(".svg", ".png"),
                    ]
                    subprocess.run(command, check=True)
                    print("Converted SVG to PNG")
                else:
                    # Just copy the SVG
                    shutil.copy2(input_path, output_path)
                return True
            except Exception as e:
                print(f"Error processing SVG: {e}")
                return False

    def compress_with_auto_detect(
        self, input_path: str, output_path: str, output_format: str
    ) -> bool:
        """
        Compress an image with automatic format detection and intermediate conversion.
        This method is designed for batch processing where you provide custom paths.

        Args:
            input_path: Path to the input image file
            output_path: Path where the compressed output should be saved
            output_format: Desired output format (png, jpg, webp, etc.)

        Returns:
            bool: True if successful, False otherwise
        """
        # Detect actual file format
        file_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        actual_format = self._detect_actual_format(input_path)

        # Check if file format doesn't match extension (misnamed files only)
        needs_conversion = False
        if actual_format != file_ext and actual_format != "unknown":
            # Only do intermediate conversion for misnamed files
            needs_conversion = True
        # ImageMagick can handle HEIC directly - no intermediate conversion needed!

        # Convert to intermediate format if needed
        intermediate_path = None
        working_input = input_path

        if needs_conversion:
            try:
                # Use a temp location near the output file
                output_dir = os.path.dirname(output_path)
                base_name = os.path.splitext(os.path.basename(input_path))[0]

                # Determine intermediate format
                if self.config["output_format"].lower() in [
                    "png",
                    "webp",
                    "gif",
                    "avif",
                ]:
                    intermediate_ext = "png"
                else:
                    intermediate_ext = "jpg"

                intermediate_path = os.path.join(
                    output_dir, f"_temp_{base_name}.{intermediate_ext}"
                )

                # Convert to intermediate format
                print(
                    f"  Converting {actual_format.upper()} to intermediate {intermediate_ext.upper()} format..."
                )

                # Use ImageMagick for ALL conversions - SIMPLEST POSSIBLE COMMAND
                # Just: magick input output
                # This works for HEIC and all other formats without cropping
                command = ["magick", input_path, intermediate_path]

                subprocess.run(command, check=True, capture_output=True, text=True)

                working_input = intermediate_path

            except Exception as e:
                print(
                    f"Warning: Intermediate conversion failed ({e}), attempting direct compression"
                )
                working_input = input_path

        # Route to appropriate compression function
        format_handlers = {
            "png": self.compress_png,
            "jpg": self.compress_jpeg,
            "jpeg": self.compress_jpeg,
            "webp": self.compress_webp,
            "gif": self.compress_gif,
            "avif": self.compress_avif,
            "svg": self.compress_svg,
        }

        handler = format_handlers.get(output_format.lower())
        success = False

        if handler:
            success = handler(working_input, output_path)
        else:
            print(f"Unsupported output format: {output_format}")

        # Clean up intermediate file if it exists
        if intermediate_path and os.path.exists(intermediate_path):
            try:
                os.remove(intermediate_path)
            except Exception:
                pass

        return success

    def process_image(self, input_path: str, output_format: str) -> bool:
        """Process a single image file."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(self.output_dir, f"{base_name}.{output_format}")

        # Use the auto-detect method for processing
        success = self.compress_with_auto_detect(input_path, output_path, output_format)

        if success:
            # Print file size comparison
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            reduction = (1 - compressed_size / original_size) * 100
            print(
                f"Compressed: {os.path.basename(input_path)} -> {os.path.basename(output_path)}"
            )
            print(
                f"  Size: {original_size:,} -> {compressed_size:,} bytes ({reduction:.1f}% reduction)"
            )

        return success

    def process_all(self):
        """Process all images in the input directory."""
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

        # Setup output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

        print(
            f"Processing images. Output format: {self.config['output_format'].upper()}"
        )
        print(f"Output directory: {self.output_dir}")

        # Show which dimension is being used
        if self.config.get("target_width"):
            print(
                f"Target dimension: Width = {self.config['target_width']}px (maintaining aspect ratio)"
            )
        elif self.config.get("target_height"):
            print(
                f"Target dimension: Height = {self.config['target_height']}px (maintaining aspect ratio)"
            )

        transparency_status = (
            "Preserved"
            if self.config.get("preserve_transparency", True)
            else f"Removed (background: {self.config.get('background_color', 'white')})"
        )
        print(f"Transparency: {transparency_status}")

        exif_status = (
            "Preserved" if self.config.get("preserve_exif", False) else "Removed"
        )
        print(f"EXIF metadata: {exif_status}")

        for filename in os.listdir(self.image_input_dir):
            file_path = os.path.join(self.image_input_dir, filename)

            if filename.lower().endswith(image_extensions):
                self.process_image(file_path, self.config["output_format"])


def main():
    # Configuration
    config = {
        # General settings - USE ONLY ONE: target_width OR target_height (not both)
        "target_width": 1200,  # Resize to this width, maintaining aspect ratio
        "target_height": None,  # OR use this for height (e.g., 800 for tall images)
        "output_format": "webp",
        "max_colors": False,  # Set to None for no color reduction
        # Metadata handling
        "preserve_exif": False,  # Set to True to preserve EXIF metadata
        # Transparency handling
        "preserve_transparency": False,
        # PNG specific
        "png_compression_level": 9,  # 0-9
        "use_pngquant": True,  # pngquant is a lossy compression tool
        "pngquant_quality": "65-80",  # 0-100
        # JPEG/JPG specific
        "jpeg_quality": 60,  # 0-100
        # WebP specific
        "webp_quality": 75,  # 0-100 higher is better
        "webp_lossless": False,
        # GIF specific
        "gif_colors": 128,
        # AVIF specific
        "avif_quality": 10,  # 0-100
        # SVG specific
        "convert_svg_to_png": False,
    }

    compressor = ImageCompressor(config)
    compressor.process_all()


if __name__ == "__main__":
    main()
