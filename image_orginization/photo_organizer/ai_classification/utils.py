"""Utility functions for AI classification."""

import base64
import json
from pathlib import Path
from typing import Dict, Any


def b64(path: Path) -> str:
    """Encode file as base64 string.

    Args:
        path: Path to file

    Returns:
        Base64-encoded string
    """
    return base64.b64encode(path.read_bytes()).decode()


def parse_json_response(response_content: str) -> Dict[str, Any]:
    """Parse JSON response from OpenAI API.

    Args:
        response_content: Raw response content string

    Returns:
        Parsed JSON dictionary
    """
    return json.loads(response_content)


def create_image_message(image_id: str, thumb_path: Path) -> Dict:
    """Create an OpenAI message with image content.

    Args:
        image_id: Identifier for the image
        thumb_path: Path to thumbnail image

    Returns:
        Message dictionary for OpenAI API
    """
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": f"id={image_id}"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64(thumb_path)}"},
            },
        ],
    }


def create_singleton_image_message(singleton_id: str, thumb_path: Path) -> Dict:
    """Create a singleton image message for cluster matching.

    Args:
        singleton_id: Identifier for the singleton image
        thumb_path: Path to thumbnail image

    Returns:
        Message dictionary for OpenAI API
    """
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": f"SINGLETON id={singleton_id}"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64(thumb_path)}"},
            },
        ],
    }


def create_cluster_sample_message(thumb_path: Path) -> Dict:
    """Create a cluster sample image message.

    Args:
        thumb_path: Path to thumbnail image

    Returns:
        Message dictionary for OpenAI API
    """
    return {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64(thumb_path)}"},
            }
        ],
    }
