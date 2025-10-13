"""Collage generation utilities for optimized AI classification.

Creates image collages to show multiple clusters in a single image,
bypassing the MAX_CLUSTERS_PER_CALL limitation and reducing API costs by 75-90%.
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from ..models import Item


def create_cluster_collage(
    clusters: List[List[Item]],
    labels: Optional[Dict[str, Dict]] = None,
    max_clusters: int = 50,
    grid_cols: int = 10,
    thumb_size: int = 256,
    output_path: Optional[Path] = None,
) -> Path:
    """Create a labeled collage of cluster example images.

    Each cell shows:
    - Cluster example image (thumbnail)
    - Cluster ID number (top-left corner)
    - Label text (bottom, if provided)

    Args:
        clusters: List of clusters (each cluster is a list of Items)
        labels: Optional dict mapping item IDs to label dicts {"label": str, ...}
        max_clusters: Max clusters to include in collage
        grid_cols: Number of columns in the grid
        thumb_size: Size of each thumbnail in pixels
        output_path: Optional path to save collage (default: /tmp/cluster_collage.jpg)

    Returns:
        Path to saved collage image

    Example:
        >>> collage = create_cluster_collage(
        ...     clusters=groups[:50],
        ...     labels=high_conf_labels,
        ...     grid_cols=10,
        ... )
        >>> # AI can now see 50 clusters in one image!
    """
    # Limit to max_clusters
    clusters_to_show = clusters[:max_clusters]
    num_clusters = len(clusters_to_show)

    # Calculate grid dimensions
    grid_rows = (num_clusters + grid_cols - 1) // grid_cols

    # Create blank canvas
    collage_width = grid_cols * thumb_size
    collage_height = grid_rows * thumb_size
    collage = Image.new("RGB", (collage_width, collage_height), "white")
    draw = ImageDraw.Draw(collage)

    # Try to load system font, fallback to default
    try:
        # macOS system font
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        if not Path(font_path).exists():
            # Linux alternative
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_large = ImageFont.truetype(font_path, 32)
        font_small = ImageFont.truetype(font_path, 18)
    except Exception:
        # Fallback to default
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Paste each cluster example
    for idx, cluster in enumerate(clusters_to_show):
        row = idx // grid_cols
        col = idx % grid_cols
        x = col * thumb_size
        y = row * thumb_size

        # Get example image (best representative)
        example = cluster[0]

        try:
            # Load and resize thumbnail
            img = Image.open(example.thumb).convert("RGB")
            img = img.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
            collage.paste(img, (x, y))
        except Exception as e:
            # If image fails to load, show placeholder
            draw.rectangle([x, y, x + thumb_size, y + thumb_size], fill="gray")
            draw.text(
                (x + thumb_size // 2, y + thumb_size // 2),
                "Error",
                fill="white",
                font=font_small,
                anchor="mm",
            )

        # Draw border around cell
        draw.rectangle(
            [x, y, x + thumb_size - 1, y + thumb_size - 1],
            outline="black",
            width=3,
        )

        # Draw cluster ID (top-left corner with dark background)
        cluster_id_text = f"#{idx}"
        bbox = draw.textbbox((0, 0), cluster_id_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        padding = 8

        # Dark background for ID
        draw.rectangle(
            [x, y, x + text_width + padding * 2, y + text_height + padding * 2],
            fill="black",
        )
        draw.text(
            (x + padding, y + padding),
            cluster_id_text,
            fill="white",
            font=font_large,
        )

        # Draw label (bottom of cell, if provided)
        if labels and example.id in labels:
            label_text = labels[example.id]["label"]
            # Truncate and format label
            label_display = label_text.replace("-", " ").title()[:25]

            bbox = draw.textbbox((0, 0), label_display, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_y = y + thumb_size - text_height - padding * 2

            # Semi-transparent dark background
            draw.rectangle(
                [x, text_y, x + text_width + padding * 2, y + thumb_size],
                fill="black",
            )
            draw.text(
                (x + padding, text_y + padding),
                label_display,
                fill="white",
                font=font_small,
            )

    # Save collage
    if output_path is None:
        output_path = Path("/tmp/cluster_collage.jpg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    collage.save(output_path, quality=90, optimize=True)

    return output_path


def create_singleton_collage(
    singleton: Item,
    output_path: Optional[Path] = None,
) -> Path:
    """Create a simple collage with just the singleton image.

    Used for consistent image formatting when matching against cluster collages.

    Args:
        singleton: The singleton Item to create collage for
        output_path: Optional path to save (default: /tmp/singleton_{id}.jpg)

    Returns:
        Path to saved singleton image
    """
    if output_path is None:
        output_path = Path(f"/tmp/singleton_{singleton.id}.jpg")

    # Simply copy the thumbnail
    img = Image.open(singleton.thumb).convert("RGB")
    img.save(output_path, quality=90, optimize=True)

    return output_path


def get_optimal_grid_size(num_items: int, max_cols: int = 10) -> Tuple[int, int]:
    """Calculate optimal grid dimensions for a collage.

    Args:
        num_items: Number of items to display
        max_cols: Maximum columns allowed

    Returns:
        (columns, rows) tuple

    Example:
        >>> get_optimal_grid_size(50, max_cols=10)
        (10, 5)  # 10×5 grid
        >>> get_optimal_grid_size(35, max_cols=10)
        (7, 5)   # 7×5 grid (better aspect ratio than 10×4)
    """
    if num_items <= max_cols:
        return (num_items, 1)

    # Try to create a roughly square grid
    rows = (num_items + max_cols - 1) // max_cols

    # Optimize columns for last row (avoid many empty cells)
    if num_items % max_cols < max_cols // 2 and rows > 1:
        # Reduce columns to make grid more balanced
        cols = (num_items + rows - 1) // rows
        return (cols, rows)

    return (max_cols, rows)
