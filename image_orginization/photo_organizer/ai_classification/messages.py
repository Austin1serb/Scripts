"""Message builders for OpenAI API calls."""

from typing import List, Dict


def build_classification_messages(base_messages: List[Dict]) -> List[Dict]:
    """Build messages for classification API call.

    Args:
        base_messages: Base system/user messages from config

    Returns:
        Copy of messages ready for image appending
    """
    if not base_messages:
        raise ValueError(
            "Base messages list is empty; at least one message is required."
        )
    return base_messages.copy()


def build_singleton_assignment_messages(
    num_singletons: int, num_clusters: int
) -> List[Dict]:
    """Build messages for singleton assignment API call.

    Args:
        num_singletons: Number of singleton photos in this batch
        num_clusters: Number of clusters to compare against

    Returns:
        List of initial messages for singleton assignment
    """
    return [
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
                f"I have {num_singletons} singleton photos and {num_clusters} existing clusters. "
                f"For each singleton, return the cluster_id it belongs to (or -1 for no match)."
            ),
        },
    ]


def build_singleton_assignment_messages_with_labels(
    num_singletons: int, num_clusters: int
) -> List[Dict]:
    """Build messages for singleton assignment with label context (cascading).

    Args:
        num_singletons: Number of singleton photos in this batch
        num_clusters: Number of clusters to compare against

    Returns:
        List of initial messages for singleton assignment with label guidance
    """
    return [
        {
            "role": "system",
            "content": (
                "You are an expert at matching construction photos to labeled project clusters. "
                "Each cluster has already been classified with a specific label (e.g., 'stamped-concrete-driveway'). "
                "For each singleton photo, determine which labeled cluster (if any) it belongs to. "
                "Consider: visual similarity, materials, construction type, label semantics, and context. "
                "Return cluster_id=-1 if no good match exists."
            ),
        },
        {
            "role": "user",
            "content": (
                f"I have {num_singletons} singleton photos and {num_clusters} labeled clusters. "
                f"For each singleton, return the cluster_id it belongs to (or -1 for no match). "
                f"Use both visual matching AND label semantics to make accurate assignments."
            ),
        },
    ]


def add_cluster_label_message(
    messages: List[Dict], cluster_id: int, label: str, num_samples: int
):
    """Add cluster label message to messages list (with label).

    Args:
        messages: Messages list to append to
        cluster_id: ID of the cluster
        label: Classification label for this cluster (e.g., "stamped-concrete-driveway")
        num_samples: Number of sample photos in this cluster
    """
    messages.append(
        {
            "role": "user",
            "content": f"CLUSTER {cluster_id}: {label} ({num_samples} sample photos):",
        }
    )
