"""OpenAI GPT Vision-based image classification and singleton assignment."""

import json
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Tuple

from ..models import Item
from ..config import (
    LABELS,
    MESSAGES,
    DEFAULT_MODEL,
    API_RATE_LIMIT_DELAY,
    MAX_RETRIES,
    RETRY_DELAY,
)
from ..utils.loading_spinner import Spinner

from .utils import (
    parse_json_response,
    create_image_message,
)
from .schemas import get_classification_schema
from .messages import (
    build_classification_messages,
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


def classify_singleton(item: Item, model: str = DEFAULT_MODEL) -> Dict:
    """Classify a single image using OpenAI Vision API.

    Used for cascading classification: classify singletons first, then
    filter clusters by matching labels for assignment.

    Args:
        item: Single Item to classify
        model: OpenAI model to use (e.g., 'gpt-4o')

    Returns:
        Classification result: {"label": str, "confidence": float, "descriptor": str}
    """
    if OpenAI is None:
        return {"label": "unknown", "confidence": 0.0, "descriptor": ""}

    # Use classify_batches with batch_size=1
    result = classify_batches([item], batch_size=1, model=model)
    return result.get(
        item.id, {"label": "unknown", "confidence": 0.0, "descriptor": ""}
    )


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


# ===============================================================
# UNIFIED MATCHING: Singletons + hash_only Clusters
# ===============================================================


def match_uncertain_items_with_collage(
    uncertain_items: List[Tuple[int, List[Item]]],
    confident_clusters: List[Tuple[int, List[Item]]],
    cluster_labels: Dict[int, Dict],
    model: str = DEFAULT_MODEL,
) -> Dict[int, int]:
    """
    Match uncertain items (singletons & hash_only clusters) against confident
    clusters using collage comparison.

    This is a unified approach that treats both singletons and hash_only clusters
    identically: both need validation and should be compared against all confident
    clusters to find the best match.

    Args:
        uncertain_items: List of (cluster_id, items) that need matching.
                        Can be singletons (1 item) or hash_only clusters (2+ items)
        confident_clusters: List of (cluster_id, items) to match against.
                           These are GPS/Time/Filename clusters (high confidence)
        cluster_labels: Dict mapping cluster_id -> {label, confidence, descriptor}
                       for already-classified confident clusters
        model: OpenAI model to use (default: gpt-4o)

    Returns:
        Dict mapping uncertain_cluster_id -> target_cluster_id
        Returns -1 if no match found (item stays separate)

    Example:
        uncertain_items = [(91, [singleton_item]), (23, [3 hash_only items])]
        confident_clusters = [(5, [gps_items]), (8, [time_items])]
        cluster_labels = {5: {"label": "driveway-repair", ...}, ...}

        Result: {91: 5, 23: -1}  # singleton merges, hash_only stays separate
    """
    from openai import OpenAI

    from ..config import API_RATE_LIMIT_DELAY
    from .collage import create_cluster_collage
    from .schemas import get_uncertain_match_schema
    from .utils import b64
    from ..utils.loading_spinner import Spinner

    if not uncertain_items:
        print("No uncertain items to match.")
        return {}

    if not confident_clusters:
        print("No confident clusters to match against.")
        return {cid: -1 for cid, _ in uncertain_items}

    client = OpenAI()
    assignments = {}

    print(
        f"\n🔍 Matching {len(uncertain_items)} uncertain items against "
        f"{len(confident_clusters)} confident clusters..."
    )

    # Create collage of all confident clusters (one-time operation)
    print("\n📸 Creating collage of confident clusters...")
    confident_cluster_ids = [cid for cid, _ in confident_clusters]
    confident_examples = {
        cid: get_best_example(items) for cid, items in confident_clusters
    }

    collage_path = Path(tempfile.gettempdir()) / "confident_clusters_collage.jpg"
    create_cluster_collage(
        clusters=confident_clusters,
        cluster_labels=cluster_labels,
        output_path=collage_path,
        include_labels=True,
        include_cluster_ids=True,
    )

    # Encode collage once
    collage_b64 = b64(collage_path)

    # Process each uncertain item
    for uncertain_id, uncertain_group in uncertain_items:
        # Get best example from uncertain item
        if len(uncertain_group) == 1:
            uncertain_example = uncertain_group[0]
            item_type = "singleton"
        else:
            uncertain_example = get_best_example(uncertain_group)
            item_type = f"hash_only cluster ({len(uncertain_group)} images)"

        print(
            f"\n  🔎 Matching {item_type} #{uncertain_id}: {uncertain_example.thumb.name}"
        )

        # Build prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are comparing an uncertain photo/cluster against known confident clusters. "
                    "Determine if the uncertain item belongs to any of the confident clusters based on "
                    "visual similarity, location features, materials, and context."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"CONFIDENT CLUSTERS (labeled collage):\n"
                            f"This collage shows {len(confident_clusters)} confident clusters with their labels.\n\n"
                            f"UNCERTAIN ITEM:\n"
                            f"Below is an uncertain item (ID: {uncertain_id}) that needs matching.\n\n"
                            f"Does this uncertain item belong to any of the confident clusters in the collage?\n"
                            f"Consider: same physical location, same materials, same surroundings, distinct features.\n\n"
                            f"If it matches, return the cluster_id and confidence (0.0-1.0).\n"
                            f"If no match, return cluster_id: -1 and confidence: 0.0.\n"
                            f"Provide a brief reason for your decision."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{collage_b64}"},
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64(uncertain_example.thumb)}"
                        },
                    },
                ],
            },
        ]

        # API call with retry logic
        try:
            with Spinner(f"Comparing {item_type} #{uncertain_id}..."):
                response = call_openai_with_retry(
                    client=client,
                    model=model,
                    messages=messages,
                    response_format=get_uncertain_match_schema(),
                )

            result = json.loads(response.choices[0].message.content)
            cluster_id = result.get("cluster_id", -1)
            confidence = result.get("confidence", 0.0)
            reason = result.get("reason", "")

            assignments[uncertain_id] = cluster_id

            # Show match result
            if cluster_id != -1 and cluster_id in cluster_labels:
                cluster_label = cluster_labels[cluster_id].get("label", "unknown")
                print(
                    f"    ✅ {item_type} #{uncertain_id} → cluster #{cluster_id} "
                    f"({cluster_label}, confidence: {confidence:.0%})"
                )
                if reason:
                    print(f"       Reason: {reason}")
            else:
                print(f"    ❌ {item_type} #{uncertain_id} → no match (stays separate)")
                if reason:
                    print(f"       Reason: {reason}")

        except Exception as e:
            print(f"    ⚠️  Error matching {item_type} #{uncertain_id}: {e}")
            assignments[uncertain_id] = -1  # Default to no match on error

        # Rate limit between items
        if API_RATE_LIMIT_DELAY > 0:
            time.sleep(API_RATE_LIMIT_DELAY)

    # Cleanup
    if collage_path.exists():
        collage_path.unlink()

    # Summary
    matched = sum(1 for cid in assignments.values() if cid != -1)
    print(
        f"\n✅ Unified matching complete: {matched}/{len(uncertain_items)} matched to confident clusters"
    )

    return assignments


def separate_confident_uncertain_clusters(
    groups: List[Tuple[int, List[Item]]],
    confident_strategies: List[str],
    uncertain_strategies: List[str],
) -> Tuple[List[Tuple[int, List[Item]]], List[Tuple[int, List[Item]]]]:
    """
    Separate clusters into confident and uncertain groups.

    Args:
        groups: List of (cluster_id, items) tuples
        confident_strategies: List of strategy names that are high-confidence
        uncertain_strategies: List of strategy names that are low-confidence

    Returns:
        Tuple of (confident_clusters, uncertain_items)
        - confident_clusters: Multi-image clusters with high-confidence strategies
        - uncertain_items: Singletons + multi-image clusters with uncertain strategies
    """
    confident_clusters = []
    uncertain_items = []

    for cluster_id, items in groups:
        # Get strategy from first item (all items in cluster have same strategy)
        strategy = items[0].strategy if items else "unknown"
        count = len(items)

        # Singletons are always uncertain (regardless of strategy)
        if count == 1:
            uncertain_items.append((cluster_id, items))
        # Multi-image clusters with uncertain strategies
        elif strategy in uncertain_strategies:
            uncertain_items.append((cluster_id, items))
        # Multi-image clusters with confident strategies
        elif strategy in confident_strategies:
            confident_clusters.append((cluster_id, items))
        else:
            # Unknown strategy - default to confident if multi-image
            print(
                f"  ⚠️  Unknown strategy '{strategy}' for cluster {cluster_id}, treating as confident"
            )
            confident_clusters.append((cluster_id, items))

    return confident_clusters, uncertain_items


def apply_matches_to_groups(
    groups: List[Tuple[int, List[Item]]],
    assignments: Dict[int, int],
) -> List[Tuple[int, List[Item]]]:
    """
    Apply matching assignments by merging uncertain items into target clusters.

    Args:
        groups: Original list of (cluster_id, items) tuples
        assignments: Dict mapping uncertain_cluster_id -> target_cluster_id
                    (-1 means no match, stay separate)

    Returns:
        Updated list of (cluster_id, items) with merged clusters
    """
    # Convert groups to dict for easier manipulation
    cluster_dict = {cid: items for cid, items in groups}

    # Apply assignments
    for uncertain_id, target_id in assignments.items():
        if target_id == -1:
            # No match - item stays separate
            continue

        if uncertain_id not in cluster_dict:
            print(f"  ⚠️  Uncertain cluster {uncertain_id} not found, skipping")
            continue

        if target_id not in cluster_dict:
            print(f"  ⚠️  Target cluster {target_id} not found, skipping merge")
            continue

        # Merge uncertain items into target cluster
        uncertain_items = cluster_dict[uncertain_id]
        cluster_dict[target_id].extend(uncertain_items)

        # Remove the now-empty uncertain cluster
        del cluster_dict[uncertain_id]

        print(
            f"  ✅ Merged cluster {uncertain_id} ({len(uncertain_items)} images) → cluster {target_id}"
        )

    # Convert back to list
    return [(cid, items) for cid, items in cluster_dict.items()]
