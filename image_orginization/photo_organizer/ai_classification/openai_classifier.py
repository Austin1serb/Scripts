"""OpenAI GPT Vision-based image classification and singleton assignment."""

import time
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
    API_RATE_LIMIT_DELAY,
    MAX_RETRIES,
    RETRY_DELAY,
)
from ..utils.loading_spinner import Spinner

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
    from openai import OpenAI, RateLimitError  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore
    RateLimitError = None  # type: ignore


def call_openai_with_retry(
    client,
    model: str,
    messages: List[Dict],
    schema: Dict,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY,
) -> Dict:
    """Call OpenAI API with automatic retry on rate limit errors.

    Args:
        client: OpenAI client instance
        model: OpenAI model name
        messages: List of messages to send
        schema: JSON schema for structured output
        max_retries: Maximum number of retry attempts
        retry_delay: Seconds to wait before retrying

    Returns:
        API response

    Raises:
        Exception: If all retries fail
    """
    last_error = None
    spinner = Spinner("🤖 Waiting for AI response")

    for attempt in range(max_retries):
        try:
            spinner.start()
            resp = client.chat.completions.create(
                model=model,
                response_format={"type": "json_schema", "json_schema": schema},
                messages=messages,
            )
            spinner.stop()
            return resp

        except Exception as e:
            spinner.stop()

            # Check if it's a rate limit error (handle both old and new SDK versions)
            is_rate_limit = (
                RateLimitError and isinstance(e, RateLimitError)
            ) or "rate_limit" in str(e).lower()

            if is_rate_limit:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                    print(
                        f"⚠️  Rate limit hit. Waiting {wait_time:.1f}s before retry {attempt + 2}/{max_retries}..."
                    )
                    time.sleep(wait_time)
                else:
                    print(f"❌ Rate limit error after {max_retries} attempts")
                    raise
            else:
                # Non-rate-limit error, raise immediately
                print(f"❌ API error: {e}")
                raise

    # Should never reach here, but just in case
    spinner.stop()
    raise last_error or Exception("API call failed")


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

        # Call OpenAI API with retry logic
        resp = call_openai_with_retry(
            client=client, model=model, messages=batch_messages, schema=schema
        )

        # Parse response
        data = parse_json_response(resp.choices[0].message.content)
        for row in data.get("images", []):
            out[row["id"]] = {
                "label": row.get("label", "unknown"),
                "confidence": float(row.get("confidence", 0)),
                "descriptor": row.get("descriptor", ""),
            }

    # Process all items in batches with rate limiting
    total_batches = (len(items) + batch_size - 1) // batch_size
    for batch_num, i in enumerate(range(0, len(items), batch_size), start=1):
        print(f"Processing batch {batch_num}/{total_batches}...")
        do_batch(items[i : i + batch_size])

        # Rate limit delay between batches (skip after last batch)
        if i + batch_size < len(items) and API_RATE_LIMIT_DELAY > 0:
            print(f"⏳ Waiting {API_RATE_LIMIT_DELAY}s before next batch...")
            time.sleep(API_RATE_LIMIT_DELAY)

    return out


def get_best_example(group: List[Item]) -> Item:
    """Select the best representative image from a cluster.

    Strategy (hybrid approach for best results):
    1. Single image: use it
    2. Multiple images with GPS: prefer GPS-tagged photos (on-site)
    3. Multiple images with timestamps: select middle image (best lighting/setup)
    4. Fallback: largest file size (best quality/least compression)

    Rationale:
    - First image is often a test shot
    - Last image might be rushed
    - Middle image = photographer warmed up but not rushed
    - GPS images = definitely on-site (not office/reference photos)

    Args:
        group: List of Items in the cluster

    Returns:
        Best representative Item from the cluster
    """
    # Single image: use it
    if len(group) == 1:
        return group[0]

    # Prefer images with GPS (on-site photos are more representative)
    with_gps = [item for item in group if item.gps]
    candidates = with_gps if with_gps else group

    # Select middle image by timestamp (best lighting/setup)
    with_time = [item for item in candidates if item.dt]
    if with_time:
        sorted_items = sorted(with_time, key=lambda x: x.dt)
        middle_idx = len(sorted_items) // 2
        return sorted_items[middle_idx]

    # Fallback: largest file size (best quality)
    try:
        return max(candidates, key=lambda item: item.path.stat().st_size)
    except (OSError, AttributeError):
        # If file doesn't exist or path is invalid, use first candidate
        return candidates[0]


def classify_cluster_examples(
    groups: List[List[Item]],
    batch_size: int,
    model: str,
) -> Dict[str, Dict]:
    """Classify only cluster example images, then propagate labels to all images.

    This is 90% more efficient than classifying every image individually.

    Strategy:
    1. Select best representative image from each cluster (middle by time, GPS preferred)
    2. Classify all examples in a single batch (or multiple batches if needed)
    3. Propagate each cluster's label to ALL images in that cluster

    Args:
        groups: List of clusters (each cluster is a list of Items)
        batch_size: Number of images per API batch
        model: OpenAI model to use (e.g., 'gpt-4o')

    Returns:
        Dictionary mapping ALL item IDs to classification results

    Example:
        >>> groups = [[img1, img2, img3], [img4, img5], [img6]]
        >>> # 3 clusters = 3 API requests instead of 6
        >>> labels = classify_cluster_examples(groups, batch_size=12, model='gpt-4o')
        >>> # Returns labels for img1-img6, where img1/img2/img3 have same label
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping classification")
        all_items = [item for group in groups for item in group]
        return {
            i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""}
            for i in all_items
        }

    # Select best representative example from each cluster
    examples = [get_best_example(group) for group in groups]

    # Build mapping: example_id -> group for propagation
    example_to_group = {get_best_example(group).id: group for group in groups}

    print(
        f"🚀 Optimized Classification: {len(examples)} examples from {len(groups)} clusters"
    )
    print(f"   (selecting best representative from each cluster)")
    print(f"   (instead of classifying all {sum(len(g) for g in groups)} images)")

    # Classify only the examples
    example_labels = classify_batches(examples, batch_size, model)

    # Propagate labels to all images in each cluster
    all_labels: Dict[str, Dict] = {}
    for example_id, group in example_to_group.items():
        cluster_label = example_labels.get(
            example_id, {"label": "unknown", "confidence": 0.0, "descriptor": ""}
        )

        # Apply the same label to all images in this cluster
        for item in group:
            all_labels[item.id] = cluster_label.copy()

    return all_labels


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

        # Call OpenAI API with retry logic
        resp = call_openai_with_retry(
            client=client, model=model, messages=messages, schema=schema
        )

        # Parse response
        data = parse_json_response(resp.choices[0].message.content)
        print("raw_response: ", data)
        for assignment in data.get("assignments", []):
            singleton_id = assignment["singleton_id"]
            cluster_id = assignment["cluster_id"]
            assignments[singleton_id] = cluster_id

    # Process singletons in batches with rate limiting
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

        # Rate limit delay between batches (skip after last batch)
        if i + SINGLETON_BATCH_SIZE < len(singleton_items) and API_RATE_LIMIT_DELAY > 0:
            print(f"  ⏳ Waiting {API_RATE_LIMIT_DELAY}s before next batch...")
            time.sleep(API_RATE_LIMIT_DELAY)

    # Count assignments
    matched = sum(1 for cid in assignments.values() if cid != -1)
    print(
        f"✅ Singleton assignment complete: {matched}/{len(singleton_items)} matched to clusters"
    )

    return assignments
