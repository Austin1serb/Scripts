"""OpenAI GPT Vision-based image classification and singleton assignment."""

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
    DEFAULT_MODEL,
)

from .utils import (
    parse_json_response,
    create_image_message,
    create_singleton_image_message,
    create_cluster_sample_message,
)
from .schemas import get_classification_schema, get_singleton_assignment_schema
from .messages import (
    build_classification_messages,
    build_singleton_assignment_messages,
    add_cluster_label_message,
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / ".env", override=True)
except ImportError:  # pragma: no cover
    pass  # python-dotenv not installed, continue without it

# Optional import of OpenAI client only if classify is requested
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


def classify_batches(
    items: List[Item],
    batch_size: int,
    model: str,
    messages: List[Dict] = None,
    schema: Dict = None,
) -> Dict[str, Dict]:
    """Classify images in batches using OpenAI Vision API with structured outputs.

    Args:
        items: List of items to classify
        batch_size: Number of images per API batch
        model: OpenAI model to use (e.g., 'gpt-4o')
        messages: Optional custom messages for the API call
        schema: Optional custom JSON schema for response format

    Returns:
        Dictionary mapping item IDs to classification results
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping classification")
        return {
            i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""}
            for i in items
        }

    client = OpenAI()
    out: Dict[str, Dict] = {}

    # Use custom schema if provided, otherwise use default classification schema
    if schema is None:
        schema = get_classification_schema(LABELS)

    def do_batch(batch: List[Item]):
        """Process a single batch of images."""
        # Build base messages
        if messages is not None:
            batch_messages = messages.copy()
            if not batch_messages:
                raise ValueError(
                    "Custom messages list is empty; at least one message is required."
                )
        else:
            batch_messages = build_classification_messages(MESSAGES)

        # Append each image from the batch to the messages
        for it in batch:
            batch_messages.append(create_image_message(it.id, it.thumb))

        # Call OpenAI API
        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_schema", "json_schema": schema},
            messages=batch_messages,
        )

        # Parse response
        data = parse_json_response(resp.choices[0].message.content)
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
    model: str = DEFAULT_MODEL,
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

    # Get JSON schema for structured output
    schema = get_singleton_assignment_schema()

    def do_batch(batch: List[Item]):
        """Process a batch of singletons."""
        # Build initial messages
        messages = build_singleton_assignment_messages(
            len(batch), len(clusters_to_show)
        )

        # Add singleton photos
        for singleton in batch:
            messages.append(
                create_singleton_image_message(singleton.id, singleton.thumb)
            )

        # Add cluster sample photos
        for cluster_info in clusters_to_show:
            cluster_id = cluster_info["cluster_id"]
            samples = cluster_info["samples"]

            # Add text label for cluster
            add_cluster_label_message(messages, cluster_id, len(samples))

            # Add sample images from this cluster
            for sample_item in samples:
                messages.append(create_cluster_sample_message(sample_item.thumb))

        # Call OpenAI API
        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_schema", "json_schema": schema},
            messages=messages,
        )

        # Parse response
        data = parse_json_response(resp.choices[0].message.content)
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
