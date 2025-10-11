# AI Classification Module

Clean, modular structure for OpenAI Vision API integration.

## Structure

```
ai_classification/
├── __init__.py              # Public API exports
├── openai_classifier.py     # Main classification logic (CORE)
├── utils.py                 # Image encoding & message builders
├── schemas.py               # JSON schemas for structured outputs
├── messages.py              # Message templates for API calls
└── README.md                # This file
```

## Core Module: `openai_classifier.py`

Contains only the essential classification logic:

- `classify_batches()` - Batch image classification
- `assign_singletons_batched()` - Singleton cluster assignment

Both functions are clean, focused on the AI logic, and delegate utilities to helper modules.

## Supporting Modules

### `utils.py`
- `b64()` - Base64 encoding for images
- `parse_json_response()` - JSON parsing
- `create_image_message()` - Format images for classification
- `create_singleton_image_message()` - Format singletons for matching
- `create_cluster_sample_message()` - Format cluster samples

### `schemas.py`
- `get_classification_schema()` - JSON schema for classification
- `get_singleton_assignment_schema()` - JSON schema for cluster matching

### `messages.py`
- `build_classification_messages()` - Build classification prompt
- `build_singleton_assignment_messages()` - Build matching prompt
- `add_cluster_label_message()` - Add cluster labels to messages

## Usage

```python
from photo_organizer.ai_classification import classify_batches, assign_singletons_batched

# Classify images
labels = classify_batches(items, batch_size=12, model="gpt-4o")

# Assign singletons to clusters
assignments = assign_singletons_batched(singletons, clusters, model="gpt-4o")
```

## Design Principles

1. **Single Responsibility** - Each module has one clear purpose
2. **Testability** - Pure functions, easy to test
3. **Reusability** - Message builders and schemas are reusable
4. **Maintainability** - Changes to prompts/schemas don't affect core logic
5. **Readability** - Core classifier is <250 lines, easy to understand

## Extension Points

To add new classification types:
1. Add schema to `schemas.py`
2. Add message builder to `messages.py`
3. Use existing utilities in `utils.py`
4. Create new function in `openai_classifier.py` using the helpers
