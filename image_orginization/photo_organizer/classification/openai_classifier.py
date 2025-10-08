"""OpenAI GPT Vision-based image classification."""

import base64
import json
from pathlib import Path
from typing import List, Dict
from ..models import Item
from ..config import LABELS

# Optional import of OpenAI client only if classify is requested
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


def b64(path: Path) -> str:
    """Encode file as base64 string.

    Args:
        path: Path to file

    Returns:
        Base64-encoded string
    """
    return base64.b64encode(path.read_bytes()).decode()


def classify_batches(items: List[Item], batch_size: int, model: str) -> Dict[str, Dict]:
    """Classify images in batches using OpenAI Vision API with structured outputs.

    Args:
        items: List of items to classify
        batch_size: Number of images per API batch
        model: OpenAI model to use (e.g., 'gpt-4o')

    Returns:
        Dictionary mapping item IDs to classification results containing:
            - label: Classification label
            - confidence: Confidence score (0-1)
            - descriptor: Short description
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping classification")
        return {
            i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""}
            for i in items
        }

    client = OpenAI()
    out: Dict[str, Dict] = {}

    # JSON schema for structured output
    schema = {
        "name": "batch_classify_cluster",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "images": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string", "enum": LABELS},
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "descriptor": {"type": "string"},
                        },
                        "required": ["id", "label", "confidence"],
                    },
                }
            },
            "required": ["images"],
        },
    }

    def do_batch(batch: List[Item]):
        """Process a single batch of images."""
        messages = [
            {
                "role": "system",
                "content": "You are an image classifier for concrete construction photos. Return strict JSON only.",
            },
            {
                "role": "user",
                "content": (
                    "Allowed labels: "
                    + ", ".join(LABELS)
                    + ". For each image return id, label, confidence (0-1), and a short descriptor."
                ),
            },
        ]

        for it in batch:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"id={it.id}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64(it.thumb)}"
                            },
                        },
                    ],
                }
            )

        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_schema", "json_schema": schema},
            messages=messages,
        )

        data = json.loads(resp.choices[0].message.content)
        for row in data.get("images", []):
            out[row["id"]] = {
                "label": row.get("label", "unknown"),
                "confidence": float(row.get("confidence", 0)),
                "descriptor": row.get("descriptor", ""),
            }

    # Process all items in batches
    for i in range(0, len(items), batch_size):
        do_batch(items[i : i + batch_size])

    return out
