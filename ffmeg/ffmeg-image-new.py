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
            ]

            # Handle transparency first
            self._handle_transparency(command, input_path, "png")

            command.extend(
                [
                    "-resize",
                    f"{self.config['target_width']}x>",
                    "-strip",  # Remove metadata
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

            # Add color reduction if specified
            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])
                # For PNG with limited colors, use PNG8 format if not preserving transparency
                if not self.config.get("preserve_transparency", True):
                    command.extend(["-type", "Palette"])
                else:
                    # Use PNG32 to preserve transparency with color reduction
                    command.extend(["-define", "png:color-type=6"])

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
            command = [
                "magick",
                input_path,
            ]

            # JPEG doesn't support transparency, so we must remove it
            bg_color = self.config.get("background_color", "white")
            command.extend(["-background", bg_color, "-alpha", "remove"])

            command.extend(
                [
                    "-resize",
                    f"{self.config['target_width']}x>",
                    "-strip",
                    "-quality",
                    str(self.config.get("jpeg_quality", 85)),
                    "-sampling-factor",
                    "4:2:0",  # Chroma subsampling
                    "-interlace",
                    "Plane",  # Progressive JPEG
                    "-colorspace",
                    "sRGB",  # Ensure sRGB color space
                ]
            )

            # Optional color reduction
            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])

            # Ensure output is JPEG
            command.extend(["-format", "jpeg"])
            command.append(output_path)

            subprocess.run(command, check=True)
            return True

        except subprocess.CalledProcessError as e:
            print(f"Error compressing JPEG: {e}")
            return False

    def compress_webp(self, input_path: str, output_path: str) -> bool:
        """Compress WebP images with lossy or lossless compression."""
        try:
            command = [
                "magick",
                input_path,
            ]

            # Handle transparency
            self._handle_transparency(command, input_path, "webp")

            command.extend(
                [
                    "-resize",
                    f"{self.config['target_width']}x>",
                    "-strip",
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

            # WebP-specific transparency settings
            if self.config.get("preserve_transparency", True):
                command.extend(["-define", "webp:alpha-quality=100"])

            if self.config.get("max_colors"):
                command.extend(["-colors", str(self.config["max_colors"])])

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
                    f"{self.config['target_width']}x>",
                    "-strip",
                    "-layers",
                    "Optimize",  # Optimize GIF frames
                    "-colors",
                    str(
                        self.config.get("gif_colors", 128)
                    ),  # GIFs benefit from color reduction
                ]
            )

            # Apply dithering for better quality with fewer colors
            command.extend(["-dither", "FloydSteinberg"])

            # GIF transparency handling
            if self.config.get("preserve_transparency", True):
                command.extend(["-dispose", "Background"])

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
                    f"{self.config['target_width']}x>",
                    "-strip",
                    "-quality",
                    str(self.config.get("avif_quality", 50)),
                    "-define",
                    "heic:speed=0",  # Slowest but best compression
                ]
            )

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
                        f"{self.config['target_width']}x>",
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

    def extract_video_frame(
        self, input_path: str, output_path: str, frame_number: int = 1
    ) -> bool:
        """Extract and compress a frame from video."""
        try:
            output_format = os.path.splitext(output_path)[1][1:].lower()

            ffmpeg_command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vf",
                f"select='eq(n\\,{frame_number})',scale={self.config['target_width']}:-1",
                "-vframes",
                "1",
            ]

            # Format-specific settings
            if output_format == "png":
                ffmpeg_command.extend(
                    [
                        "-compression_level",
                        str(self.config.get("png_compression_level", 9)),
                    ]
                )
                # PNG transparency is preserved by default in ffmpeg
            elif output_format in ["jpg", "jpeg"]:
                ffmpeg_command.extend(
                    ["-q:v", str(self.config.get("jpeg_quality", 85) // 10)]
                )
            elif output_format == "webp":
                ffmpeg_command.extend(
                    ["-quality", str(self.config.get("webp_quality", 80))]
                )
                if self.config.get("webp_lossless", False):
                    ffmpeg_command.extend(["-lossless", "1"])

            ffmpeg_command.append(output_path)
            subprocess.run(ffmpeg_command, check=True)

            # Apply format-specific post-processing
            if output_format == "png" and self.config.get("use_pngquant", True):
                self.compress_png(output_path, output_path)

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error extracting video frame: {e}")
            return False

    def process_image(self, input_path: str, output_format: str) -> bool:
        """Process a single image file."""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(self.output_dir, f"{base_name}.{output_format}")

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
        if handler:
            success = handler(input_path, output_path)
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
        else:
            print(f"Unsupported output format: {output_format}")
            return False

    def process_all(self):
        """Process all images and videos in the input directory."""
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

        # Setup output directory
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

        print(
            f"Processing images. Output format: {self.config['output_format'].upper()}"
        )
        print(f"Output directory: {self.output_dir}")
        print(
            f"Transparency: {'Preserved' if self.config.get('preserve_transparency', True) else f'Removed (background: {self.config.get('background_color', 'white')})'}"
        )

        for filename in os.listdir(self.image_input_dir):
            file_path = os.path.join(self.image_input_dir, filename)

            if filename.lower().endswith(image_extensions):
                self.process_image(file_path, self.config["output_format"])

            elif filename.lower().endswith(video_extensions):
                base_name = os.path.splitext(filename)[0]
                for i in range(self.config.get("frames_to_extract", 1)):
                    output_path = os.path.join(
                        self.output_dir,
                        f"{base_name}-frame-{i+1}.{self.config['output_format']}",
                    )
                    self.extract_video_frame(
                        file_path,
                        output_path,
                        i * self.config.get("frame_interval", 25),
                    )


def main():
    # Configuration
    config = {
        # General settings
        "target_width": 881,
        "output_format": "webp",
        "max_colors": None,  # Set to None for no color reduction
        # Transparency handling
        "preserve_transparency": False,
        # PNG specific
        "png_compression_level": 4,  # 0-9
        "use_pngquant": False,  # pngquant is a lossy compression tool
        "pngquant_quality": "65-80",  # 0-100
        # JPEG/JPG specific
        "jpeg_quality": 60,  # 0-100
        # WebP specific
        "webp_quality": 80,  # 0-100 higher is better
        "webp_lossless": False,
        # GIF specific
        "gif_colors": 128,
        # AVIF specific
        "avif_quality": 100,  # 0-100
        # SVG specific
        "convert_svg_to_png": False,
        # Video frame extraction
        "frames_to_extract": 1,
        "frame_interval": 25,  # frames
    }

    compressor = ImageCompressor(config)
    compressor.process_all()


if __name__ == "__main__":
    main()
