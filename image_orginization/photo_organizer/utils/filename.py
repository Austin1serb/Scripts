"""Filename parsing and comparison utilities.

Handles various filename formats:
    - IMG_751, IMAGE_751, DSC_751 → normalized to 'img' prefix
    - 751.jpg (no prefix) → empty prefix
    - Photo-123, photo_123 → 'photo' prefix

Number proximity scoring:
    - Same number: 1.0
    - ±1-3: 0.9-0.7 (likely same burst/sequence)
    - ±4-10: 0.4 (possibly related)
    - ±11-50: 0.2 (weak relation)
    - >50: 0.0 (likely unrelated, different time/project)
"""

import re
from pathlib import Path
from ..models import NameFeat

try:
    from rapidfuzz import fuzz

    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

# Regex for extracting filename components: prefix, number, suffix
NAME_TOKEN_RE = re.compile(r"([A-Za-z]+)?(?:[_-])?(\d{2,})(.*)", re.ASCII)

# Common camera/device filename prefixes to normalize
COMMON_PREFIXES = {
    "dsc": "img",
    "dscf": "img",
    "dscn": "img",
    "image": "img",
    "img": "img",
    "p": "img",
    "photo": "img",
    "pic": "img",
    "pict": "img",
}


def name_features(p: Path) -> NameFeat:
    """Extract features from filename for similarity comparison.

    Args:
        p: Path to file

    Returns:
        NameFeat object with extracted features
    """
    base = p.stem  # without extension
    m = NAME_TOKEN_RE.fullmatch(base)
    if not m:
        # Fallback: longest numeric group anywhere
        nums = re.findall(r"\d{2,}", base)
        num = int(nums[-1]) if nums else None
        # Common prefix heuristic
        pref = base.split(nums[-1])[0] if nums else base[:3].lower()
        normalized_prefix = COMMON_PREFIXES.get(pref.lower(), pref.lower())
        return NameFeat(prefix=normalized_prefix, num=num, suffix="", raw=base.lower())

    pref, num, suf = m.groups()
    prefix_lower = (pref or "").lower()
    normalized_prefix = COMMON_PREFIXES.get(prefix_lower, prefix_lower)
    return NameFeat(
        prefix=normalized_prefix,
        num=int(num),
        suffix=(suf or "").lower(),
        raw=base.lower(),
    )


def lcp_len(a: str, b: str) -> int:
    """Calculate length of longest common prefix.

    Args:
        a, b: Strings to compare

    Returns:
        Length of common prefix
    """
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def filename_score(a: NameFeat, b: NameFeat) -> float:
    """Calculate similarity score between two filename features.

    Uses a weighted combination approach:
        1. Structured number proximity (0.0-0.6 weight)
        2. String similarity via RapidFuzz or LCP (0.0-0.3 weight)
        3. Edit marker bonus (0.0-0.1 weight)

    Args:
        a, b: NameFeat objects to compare

    Returns:
        Similarity score between 0.0 and 1.0
    """
    score = 0.0

    # COMPONENT 1: Structured number proximity (primary signal)
    if a.num is not None and b.num is not None:
        number_gap = abs(a.num - b.num)

        # Same normalized prefix (IMG, IMAGE, DSC all → 'img')
        if a.prefix == b.prefix and a.prefix != "":
            # Exponential decay for number gap scoring
            if number_gap == 0:
                score += 0.6  # Perfect match
            elif number_gap == 1:
                score += 0.55  # Adjacent (likely burst)
            elif number_gap <= 3:
                score += 0.45  # Very close sequence
            elif number_gap <= 10:
                score += 0.30  # Close sequence
            elif number_gap <= 30:
                score += 0.15  # Moderate gap
            elif number_gap <= 50:
                score += 0.05  # Weak relation
            # >50 gap: 0.0 (likely different project/time)

        # No prefix or different prefix - reduced weight
        else:
            if number_gap == 0:
                score += 0.3
            elif number_gap <= 3:
                score += 0.2
            elif number_gap <= 10:
                score += 0.1

    # COMPONENT 2: String similarity (fallback/enhancement signal)
    if HAS_RAPIDFUZZ:
        # RapidFuzz: better handles variations, typos, different separators
        # ratio: general similarity (0-100), normalized to 0-1
        ratio = fuzz.ratio(a.raw, b.raw) / 100.0
        # partial_ratio: best matching substring
        partial = fuzz.partial_ratio(a.raw, b.raw) / 100.0
        # token_sort: ignores word order
        token_sort = fuzz.token_sort_ratio(a.raw, b.raw) / 100.0

        # Weighted average favoring exact and partial matches
        string_similarity = 0.5 * ratio + 0.3 * partial + 0.2 * token_sort
        score += 0.3 * string_similarity
    else:
        # Fallback to LCP if RapidFuzz not available
        lcp = lcp_len(a.raw, b.raw)
        max_len = max(len(a.raw), len(b.raw))
        if max_len > 0:
            lcp_ratio = lcp / max_len
            score += 0.3 * lcp_ratio

    # COMPONENT 3: Edit marker bonus
    edit_markers = [
        "(1)",
        "(2)",
        "(3)",
        "(4)",
        "(5)",
        "(6)",
        "(7)",
        "(8)",
        "copy",
        "edited",
        "final",
        "export",
        " copy",
        " edited",
    ]
    if any(marker in a.raw for marker in edit_markers) and any(
        marker in b.raw for marker in edit_markers
    ):
        score += 0.1

    return min(score, 1.0)
