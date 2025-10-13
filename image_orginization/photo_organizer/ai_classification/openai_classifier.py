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
    build_singleton_assignment_messages_with_labels,
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


def assign_singletons_batched(
    singleton_items: List[Item],
    multi_photo_clusters: List[List[Item]],
    model: str = DEFAULT_MODEL,
    cluster_labels: Dict[str, Dict] = None,
) -> Dict[str, int]:
    """Match singleton photos to existing clusters using AI vision (BATCHED).

    Processes singletons in batches to reduce API costs. For each singleton,
    AI determines which cluster (if any) it belongs to based on visual similarity,
    materials, construction context, and lighting.

    NEW (Cascading Classification): If cluster_labels are provided, uses label-guided
    matching to filter clusters by semantic similarity, allowing unlimited clusters.

    Args:
        singleton_items: List of single-photo items to assign
        multi_photo_clusters: List of clusters (each cluster is a list of Items)
        model: OpenAI model to use (e.g., 'gpt-4o')
        cluster_labels: Optional dict mapping cluster example IDs to labels
                       (enables cascading classification with label filtering)

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

    # Determine if we're using cascading classification with labels
    use_labels = cluster_labels is not None

    # Prepare cluster samples (first N photos from each cluster)
    cluster_samples = []
    for idx, cluster in enumerate(multi_photo_clusters):
        if len(cluster) > 1:  # Only include multi-photo clusters
            example_id = cluster[0].id
            label = (
                cluster_labels.get(example_id, {}).get("label", "unknown")
                if use_labels
                else None
            )
            cluster_samples.append(
                {
                    "cluster_id": idx,
                    "samples": cluster[:CLUSTER_SAMPLES_PER_CLUSTER],
                    "label": label,  # Include label for cascading
                }
            )

    if not cluster_samples:
        print("[warn] No multi-photo clusters available for singleton assignment")
        return {item.id: -1 for item in singleton_items}

    # Get JSON schema for structured output
    schema = get_singleton_assignment_schema()

    def do_batch(batch: List[Item]):
        """Process a batch of singletons."""
        # CASCADING CLASSIFICATION: If labels provided, filter clusters per singleton
        if use_labels:
            # Classify each singleton first to get its label
            print("  🔍 Classifying singletons for label-guided matching...")
            singleton_labels = {}
            for singleton in batch:
                label_result = classify_singleton(singleton, model)
                singleton_labels[singleton.id] = label_result["label"]

            # For each singleton, filter clusters by matching label
            for singleton in batch:
                singleton_label = singleton_labels[singleton.id]

                # Filter clusters: prioritize matching labels, include top N as fallback
                matching_clusters = [
                    c for c in cluster_samples if c["label"] == singleton_label
                ]

                # If no matches, use all clusters (singleton might be unique)
                # Otherwise, limit to matching + top 5 largest clusters
                if matching_clusters:
                    # Use matching clusters + top 5 largest (for context)
                    largest_clusters = sorted(
                        cluster_samples, key=lambda c: len(c["samples"]), reverse=True
                    )[:5]
                    clusters_to_show = matching_clusters + [
                        c for c in largest_clusters if c not in matching_clusters
                    ]
                    clusters_to_show = clusters_to_show[:MAX_CLUSTERS_PER_CALL]
                else:
                    # No label match, show largest clusters
                    clusters_to_show = sorted(
                        cluster_samples, key=lambda c: len(c["samples"]), reverse=True
                    )[:MAX_CLUSTERS_PER_CALL]

                # Build messages with label context
                messages = build_singleton_assignment_messages_with_labels(
                    1, len(clusters_to_show)
                )

                # Add singleton photo
                messages.append(
                    create_singleton_image_message(singleton.id, singleton.thumb)
                )

                # Add cluster samples with labels
                for cluster_info in clusters_to_show:
                    cluster_id = cluster_info["cluster_id"]
                    samples = cluster_info["samples"]
                    label = cluster_info["label"]

                    # Add text label for cluster (with label name)
                    add_cluster_label_message(messages, cluster_id, label, len(samples))

                    # Add sample images from this cluster
                    for sample_item in samples:
                        messages.append(
                            create_cluster_sample_message(sample_item.thumb)
                        )

                # Call API for this single singleton
                resp = call_openai_with_retry(
                    client=client, model=model, messages=messages, schema=schema
                )

                # Parse response
                data = parse_json_response(resp.choices[0].message.content)
                for assignment in data.get("assignments", []):
                    singleton_id = assignment["singleton_id"]
                    cluster_id = assignment["cluster_id"]
                    assignments[singleton_id] = cluster_id

        else:
            # ORIGINAL LOGIC: No labels, batch process singletons
            clusters_to_show = cluster_samples[:MAX_CLUSTERS_PER_CALL]

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

                # Add text label for cluster (no label name)
                add_cluster_label_message(
                    messages, cluster_id, "unlabeled", len(samples)
                )

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


# ==============================================================================
# COLLAGE-BASED CLASSIFICATION (NEW - 75-90% cost reduction!)
# ==============================================================================


def classify_clusters_with_collage(
    groups: List[List[Item]],
    collage_size: int = 50,
    model: str = DEFAULT_MODEL,
) -> Dict[str, Dict]:
    """Classify clusters using collages instead of individual batching.

    OPTIMIZATION: Show 50+ clusters in a single collage image instead of
    sending them individually. Bypasses MAX_CLUSTERS_PER_CALL limitation.

    Cost Savings:
    - OLD: 100 clusters = 100 API calls
    - NEW: 100 clusters ÷ 50 per collage = 2 API calls (98% reduction!)

    Args:
        groups: List of clusters to classify
        collage_size: Max clusters per collage (default: 50)
        model: OpenAI model to use

    Returns:
        Dictionary mapping item IDs to classification results

    Example:
        >>> labels = classify_clusters_with_collage(groups, collage_size=50)
        >>> # 100 clusters → 2 API calls instead of 100!
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping classification")
        return {
            item.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""}
            for group in groups
            for item in group
        }

    from ..utils.collage import create_cluster_collage

    client = OpenAI()
    all_labels: Dict[str, Dict] = {}

    # Process clusters in collage batches
    total_collages = (len(groups) + collage_size - 1) // collage_size

    for collage_idx in range(total_collages):
        start_idx = collage_idx * collage_size
        end_idx = min(start_idx + collage_size, len(groups))
        batch_groups = groups[start_idx:end_idx]

        print(
            f"\n🖼️  Creating collage {collage_idx + 1}/{total_collages} "
            f"({len(batch_groups)} clusters)..."
        )

        # Create collage with cluster examples
        collage_path = create_cluster_collage(
            clusters=batch_groups,
            labels=None,  # No labels yet (we're classifying them)
            max_clusters=len(batch_groups),
            grid_cols=10,
        )

        print(f"  Calling AI to classify {len(batch_groups)} clusters in collage...")

        # Build messages
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an image classifier for concrete construction photos. "
                    "You will see a collage with multiple numbered clusters (each marked with #ID). "
                    "Classify each cluster by its number. Return strict JSON only."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Classify each of the {len(batch_groups)} numbered clusters in this collage. "
                    f"Available labels: {', '.join(LABELS)}. "
                    "For each cluster, return its #ID number, label, confidence (0.0-1.0), "
                    "and brief descriptor (max 6 words)."
                ),
            },
        ]

        # Add collage image
        messages.append(create_image_message("collage", collage_path))

        # Create schema for collage classification
        schema = {
            "name": "collage_classify",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "clusters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cluster_index": {"type": "integer"},
                                "label": {"type": "string", "enum": LABELS},
                                "confidence": {"type": "number"},
                                "descriptor": {"type": "string"},
                            },
                            "required": [
                                "cluster_index",
                                "label",
                                "confidence",
                                "descriptor",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["clusters"],
                "additionalProperties": False,
            },
        }

        # Call API
        resp = call_openai_with_retry(
            client=client, model=model, messages=messages, schema=schema
        )

        # Parse response
        data = parse_json_response(resp.choices[0].message.content)

        # Map cluster indices to actual groups and propagate labels
        for result in data.get("clusters", []):
            cluster_idx = result["cluster_index"]
            if 0 <= cluster_idx < len(batch_groups):
                group = batch_groups[cluster_idx]
                cluster_label = {
                    "label": result.get("label", "unknown"),
                    "confidence": float(result.get("confidence", 0)),
                    "descriptor": result.get("descriptor", ""),
                }

                # Propagate label to all images in cluster
                for item in group:
                    all_labels[item.id] = cluster_label.copy()

        # Rate limiting between collages
        if collage_idx < total_collages - 1 and API_RATE_LIMIT_DELAY > 0:
            print(f"  ⏳ Waiting {API_RATE_LIMIT_DELAY}s before next collage...")
            time.sleep(API_RATE_LIMIT_DELAY)

    print(f"\n✅ Classified {len(groups)} clusters using {total_collages} collages")
    return all_labels


def assign_singletons_with_collage(
    singleton_items: List[Item],
    multi_photo_clusters: List[List[Item]],
    cluster_labels: Dict[str, Dict],
    model: str = DEFAULT_MODEL,
    max_clusters_per_collage: int = 50,
) -> Dict[str, int]:
    """Match singletons to clusters using collage (UNLIMITED cluster comparison!).

    BREAKTHROUGH OPTIMIZATION: Create ONE collage with ALL cluster examples,
    then match each singleton against the entire collage. No more 10-cluster limit!

    Cost Savings:
    - OLD: Limited to 10 clusters per singleton
    - NEW: Show 50+ clusters in one collage!
    - Result: Can match against UNLIMITED clusters

    Args:
        singleton_items: List of singleton items to assign
        multi_photo_clusters: List of all available clusters
        cluster_labels: Dict of cluster labels from previous classification
        model: OpenAI model to use
        max_clusters_per_collage: Max clusters to show (default: 50)

    Returns:
        Dictionary mapping singleton IDs to cluster indices

    Example:
        >>> assignments = assign_singletons_with_collage(
        ...     singletons, all_60_clusters, labels, model="gpt-4o"
        ... )
        >>> # Each singleton compares against ALL 60 clusters (not just 10)!
    """
    if OpenAI is None:
        print("[warn] openai package not installed, skipping singleton assignment")
        return {item.id: -1 for item in singleton_items}

    from ..utils.collage import create_cluster_collage

    # Limit processing for cost control
    if len(singleton_items) > MAX_SINGLETONS_TO_ASSIGN:
        print(
            f"[info] Limiting singleton assignment to first {MAX_SINGLETONS_TO_ASSIGN} "
            f"of {len(singleton_items)} singletons"
        )
        singleton_items = singleton_items[:MAX_SINGLETONS_TO_ASSIGN]

    client = OpenAI()
    assignments: Dict[str, int] = {}

    # Limit clusters to max_clusters_per_collage
    clusters_to_show = multi_photo_clusters[:max_clusters_per_collage]

    print(f"\n🖼️  Creating cluster collage with {len(clusters_to_show)} clusters...")

    # Create ONE collage with ALL clusters
    collage_path = create_cluster_collage(
        clusters=clusters_to_show,
        labels=cluster_labels,
        max_clusters=len(clusters_to_show),
        grid_cols=10,
    )

    print(f"✅ Collage created: {len(clusters_to_show)} clusters in one image\n")

    # Get schema for singleton matching
    schema = {
        "name": "singleton_collage_match",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "cluster_id": {"type": "integer"},
                "confidence": {"type": "number"},
                "reasoning": {"type": "string"},
            },
            "required": ["cluster_id", "confidence", "reasoning"],
            "additionalProperties": False,
        },
    }

    # Match each singleton against the collage
    print(
        f"🤖 Matching {len(singleton_items)} singletons against collage "
        f"(batches of {SINGLETON_BATCH_SIZE})...\n"
    )

    for i in range(0, len(singleton_items), SINGLETON_BATCH_SIZE):
        batch = singleton_items[i : i + SINGLETON_BATCH_SIZE]
        batch_num = (i // SINGLETON_BATCH_SIZE) + 1
        total_batches = (
            len(singleton_items) + SINGLETON_BATCH_SIZE - 1
        ) // SINGLETON_BATCH_SIZE

        print(f"  Processing batch {batch_num}/{total_batches}...")

        for singleton in batch:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert at matching construction photos to project clusters. "
                        "You will see a collage of numbered clusters (marked with #ID) and their labels. "
                        "Determine which cluster the singleton belongs to based on visual similarity, "
                        "materials, construction type, and context. "
                        "Return the cluster #ID (0 to N-1), or -1 if no good match exists."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"I have a singleton photo and a collage with {len(clusters_to_show)} clusters. "
                        "Which cluster does the singleton belong to? "
                        "Consider the labeled cluster types and visual similarity."
                    ),
                },
                {"role": "user", "content": "Singleton photo:"},
            ]

            # Add singleton image
            messages.append(
                create_singleton_image_message(singleton.id, singleton.thumb)
            )

            # Add collage
            messages.append(
                {
                    "role": "user",
                    "content": f"Cluster collage ({len(clusters_to_show)} projects):",
                }
            )
            messages.append(create_image_message("collage", collage_path))

            # Call API
            resp = call_openai_with_retry(
                client=client, model=model, messages=messages, schema=schema
            )

            # Parse response
            data = parse_json_response(resp.choices[0].message.content)
            cluster_id = data.get("cluster_id", -1)
            confidence = data.get("confidence", 0.0)

            # Validate cluster_id
            if cluster_id < -1 or cluster_id >= len(clusters_to_show):
                cluster_id = -1

            assignments[singleton.id] = cluster_id

            # Show match result
            if cluster_id != -1:
                cluster_label = cluster_labels.get(
                    clusters_to_show[cluster_id][0].id, {}
                ).get("label", "unknown")
                print(
                    f"    {singleton.id} → cluster #{cluster_id} "
                    f"({cluster_label}, confidence: {confidence:.0%})"
                )
            else:
                print(f"    {singleton.id} → no match")

        # Rate limit between batches
        if i + SINGLETON_BATCH_SIZE < len(singleton_items) and API_RATE_LIMIT_DELAY > 0:
            print(f"  ⏳ Waiting {API_RATE_LIMIT_DELAY}s before next batch...")
            time.sleep(API_RATE_LIMIT_DELAY)

    # Summary
    matched = sum(1 for cid in assignments.values() if cid != -1)
    print(
        f"\n✅ Singleton assignment complete: {matched}/{len(singleton_items)} matched to clusters"
    )

    return assignments
