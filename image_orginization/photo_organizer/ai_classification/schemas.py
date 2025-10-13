"""JSON schemas for OpenAI structured outputs."""

from typing import Dict, List


def get_classification_schema(labels: List[str]) -> Dict:
    """Get JSON schema for batch image classification.

    Args:
        labels: List of allowed classification labels

    Returns:
        JSON schema dictionary for OpenAI structured outputs
    """
    return {
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
                            "label": {"type": "string", "enum": labels},
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


def get_singleton_assignment_schema() -> Dict:
    """Get JSON schema for singleton cluster assignment.

    Returns:
        JSON schema dictionary for OpenAI structured outputs
    """
    return {
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


def get_uncertain_match_schema() -> Dict:
    """Get JSON schema for uncertain item matching (singletons & hash_only clusters).

    Returns:
        JSON schema dictionary for OpenAI structured outputs
    """
    return {
        "name": "uncertain_match",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "cluster_id": {
                    "type": "integer",
                    "description": "Target cluster ID to merge into, or -1 for no match",
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Confidence score for the match",
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation for the match decision",
                },
            },
            "required": ["cluster_id", "confidence", "reason"],
            "additionalProperties": False,
        },
    }
