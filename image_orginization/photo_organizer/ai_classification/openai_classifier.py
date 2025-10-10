"""OpenAI GPT Vision-based image ai_classification and singleton assignment."""

import base64
import json
from pathlib import Path
from typing import List, Dict
from ..models import Item
from ..config import (
    LABELS,
    MESSAGES,
    SINGLETON_BATCH_SIZE,
    CLUSTER_SAMPLES_PER_CLUSTER,
    MAX_CLUSTERS_PER_CALL,
    MAX_SINGLETONS_TO_ASSIGN,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Load .env from project root (parent directory of photo_organizer)
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / ".env", override=True)
except ImportError:  # pragma: no cover
    pass  # python-dotenv not installed, continue without it

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
        Dictionary mapping item IDs to ai_classification results containing:
            - label: Classification label
            - confidence: Confidence score (0-1)
            - descriptor: Short description
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping ai_classification")
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
                        "required": ["id", "label", "confidence", "descriptor"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["images"],
            "additionalProperties": False,
        },
    }

    def do_batch(batch: List[Item]):
        """Process a single batch of images."""
        messages = MESSAGES.copy()

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


def assign_singletons_batched(
    singleton_items: List[Item],
    multi_photo_clusters: List[List[Item]],
    model: str = "gpt-4o",
) -> Dict[str, int]:
    """Match singleton photos to existing clusters using AI vision (BATCHED).

    Processes singletons in batches to reduce API costs. For each singleton,
    AI determines which cluster (if any) it belongs to based on visual similarity,
    materials, construction context, and lighting.

    Args:
        singleton_items: List of single-photo items to assign
        multi_photo_clusters: List of clusters (each cluster is a list of Items)
        model: OpenAI model to use (e.g., 'gpt-4o')

    Returns:
        Dictionary mapping singleton item IDs to cluster indices:
        - {singleton_id: cluster_index} for matched singletons
        - cluster_index = -1 means "no match found"

    Example:
        >>> assignments = assign_singletons_batched(singletons, clusters)
        >>> # {"img_55.jpg": 3, "img_72.jpg": -1, "img_88.jpg": 1}
        >>> # → img_55 matches cluster 3, img_72 has no match, img_88 matches cluster 1
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping singleton assignment")
        return {item.id: -1 for item in singleton_items}

    # Limit processing for cost control (configured in config.py)
    if len(singleton_items) > MAX_SINGLETONS_TO_ASSIGN:
        print(
            f"[info] Limiting singleton assignment to first {MAX_SINGLETONS_TO_ASSIGN} "
            f"of {len(singleton_items)} singletons"
        )
        singleton_items = singleton_items[:MAX_SINGLETONS_TO_ASSIGN]

    client = OpenAI()
    assignments: Dict[str, int] = {}

    # Prepare cluster samples (first N photos from each cluster)
    cluster_samples = []
    for idx, cluster in enumerate(multi_photo_clusters):
        if len(cluster) > 1:  # Only include multi-photo clusters
            cluster_samples.append(
                {
                    "cluster_id": idx,
                    "samples": cluster[:CLUSTER_SAMPLES_PER_CLUSTER],
                }
            )

    if not cluster_samples:
        print("[warn] No multi-photo clusters available for singleton assignment")
        return {item.id: -1 for item in singleton_items}

    # Limit clusters per API call to avoid token limits
    clusters_to_show = cluster_samples[:MAX_CLUSTERS_PER_CALL]

    # JSON schema for structured output
    schema = {
        "name": "singleton_assignment",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "assignments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "singleton_id": {"type": "string"},
                            "cluster_id": {"type": "integer"},
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "reason": {"type": "string"},
                        },
                        "required": ["singleton_id", "cluster_id", "confidence"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["assignments"],
            "additionalProperties": False,
        },
    }

    def do_batch(batch: List[Item]):
        """Process a batch of singletons."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert at matching construction photos to project clusters. "
                    "For each singleton photo, determine which existing cluster (if any) it belongs to. "
                    "Consider: visual similarity, materials, construction phase, lighting, and context. "
                    "Return cluster_id=-1 if no good match exists."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"I have {len(batch)} singleton photos and {len(clusters_to_show)} existing clusters. "
                    f"For each singleton, return the cluster_id it belongs to (or -1 for no match)."
                ),
            },
        ]

        # Add singleton photos
        for singleton in batch:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"SINGLETON id={singleton.id}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64(singleton.thumb)}"
                            },
                        },
                    ],
                }
            )

        # Add cluster sample photos
        for cluster_info in clusters_to_show:
            cluster_id = cluster_info["cluster_id"]
            samples = cluster_info["samples"]

            # Add text label for cluster
            messages.append(
                {
                    "role": "user",
                    "content": f"CLUSTER {cluster_id} ({len(samples)} sample photos):",
                }
            )

            # Add sample images from this cluster
            for sample_item in samples:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{b64(sample_item.thumb)}"
                                },
                            }
                        ],
                    }
                )

        # Call OpenAI API
        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_schema", "json_schema": schema},
            messages=messages,
        )

        # Parse response
        data = json.loads(resp.choices[0].message.content)
        print("raw_response: ", data)
        for assignment in data.get("assignments", []):
            singleton_id = assignment["singleton_id"]
            cluster_id = assignment["cluster_id"]
            assignments[singleton_id] = cluster_id

    # Process singletons in batches
    print(
        f"🤖 AI Singleton Assignment: Processing {len(singleton_items)} singletons "
        f"in batches of {SINGLETON_BATCH_SIZE}"
    )
    for i in range(0, len(singleton_items), SINGLETON_BATCH_SIZE):
        batch = singleton_items[i : i + SINGLETON_BATCH_SIZE]
        batch_num = (i // SINGLETON_BATCH_SIZE) + 1
        total_batches = (
            len(singleton_items) + SINGLETON_BATCH_SIZE - 1
        ) // SINGLETON_BATCH_SIZE
        print(f"  Processing batch {batch_num}/{total_batches}...")
        do_batch(batch)

    # Count assignments
    matched = sum(1 for cid in assignments.values() if cid != -1)
    print(
        f"✅ Singleton assignment complete: {matched}/{len(singleton_items)} matched to clusters"
    )

    return assignments
