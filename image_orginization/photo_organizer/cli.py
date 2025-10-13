#!/usr/bin/env python3
"""
CLI entry point for Photo Organizer.

Pipeline:
 1) ingest: walk input folder, make thumbnails, extract EXIF time/GPS, compute pHash
 2) classify: batch multi-image ai_classification with ChatGPT Vision (Structured Outputs)
 3) cluster: time + pHash centroid with AND logic
 4) label: majority vote per cluster, optional API refinement for ambiguous clusters
 5) organize: assign city, generate SEO filenames, write manifest, copy/move originals

Quick start:
  export OPENAI_API_KEY=sk-...
  pip install -r requirements.txt

Examples:
  python -m photo_organizer.cli run
    --input "/path/to/photos"
    --output "/path/to/organized"
    --brand "bespoke-concrete"
    --time-gap-min 20 --hash-threshold 6
    --classify --batch-size 12
"""

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Dict

from .config import (
    IMAGE_DIR,
    DEFAULT_SITE_DISTANCE_FEET,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_BRAND,
    DEFAULT_TIME_GAP_MINUTES,
    DEFAULT_HASH_THRESHOLD,
    DEFAULT_FUSE_THRESHOLD,
    DEFAULT_MAX_EDGES,
    DEFAULT_MODEL,
    DEFAULT_BATCH_SIZE,
    DEFAULT_ROTATE_CITIES,
    DEFAULT_DRY_RUN,
    DEFAULT_AI_CLASSIFY,
    DEFAULT_ASSIGN_SINGLETONS,
    USE_SEMANTIC_KEYWORDS,
)
from .ingestion import ingest
from .ai_classification import (
    classify_cluster_examples,
    match_uncertain_items_with_collage,
    separate_confident_uncertain_clusters,
    apply_matches_to_groups,
)
from .clustering import cluster_gps_only, fused_cluster, cluster_phash_only
from .organization import organize
from .utils.filename import name_features
from .utils.stats import print_clustering_stats


def get_thumb_path(original_filename: str, work_dir: Path) -> str:
    """Construct full absolute path to thumbnail file.

    Args:
        original_filename: Original image filename (e.g., IMG_1234.HEIC)
        work_dir: Working directory path (e.g., .../organized/_work)

    Returns:
        Full absolute path to thumbnail (e.g., .../organized/_work/thumbs/IMG_1234.jpg)
    """
    stem = Path(original_filename).stem  # Get filename without extension
    thumb_path = work_dir / "thumbs" / f"{stem}.jpg"
    return str(thumb_path.resolve())


def main():
    """Main CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Batch classify, cluster, and organize construction photos."
    )
    ap.add_argument(
        "--site-distance-feet",
        type=float,
        default=DEFAULT_SITE_DISTANCE_FEET,
        help="GPS-only site merge radius; images within this distance form one project, regardless of time",
    )

    ap.add_argument("run", nargs="?", help="Execute full pipeline")
    ap.add_argument("--input", required=True, help="Input folder with images")
    ap.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output folder")
    ap.add_argument("--brand", default=DEFAULT_BRAND, help="Optional brand slug")
    ap.add_argument(
        "--time-gap-min",
        type=int,
        default=DEFAULT_TIME_GAP_MINUTES,
        help="Max minutes to keep photos in same cluster",
    )
    ap.add_argument(
        "--hash-threshold",
        type=int,
        default=DEFAULT_HASH_THRESHOLD,
        help="Max pHash distance to keep in same cluster",
    )
    ap.add_argument(
        "--classify",
        action="store_true",
        default=DEFAULT_AI_CLASSIFY,
        help="Use ChatGPT multi-image ai_classification",
    )
    ap.add_argument(
        "--assign-singletons",
        action="store_true",
        default=DEFAULT_ASSIGN_SINGLETONS,
        help="Use AI to match singleton clusters to existing multi-photo clusters",
    )
    ap.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI vision model")
    ap.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Images per API batch",
    )
    ap.add_argument(
        "--rotate-cities",
        action="store_true",
        dest="rotate_cities",
        default=DEFAULT_ROTATE_CITIES,
        help="Rotate cities if GPS missing",
    )
    ap.add_argument(
        "--semantic-keywords",
        action="store_true",
        dest="use_semantic_keywords",
        default=USE_SEMANTIC_KEYWORDS,
        help="Enable semantic keyword rotation for SEO (cycles through related terms)",
    )
    ap.add_argument(
        "--no-semantic-keywords",
        action="store_false",
        dest="use_semantic_keywords",
        help="Disable semantic keyword rotation (use only primary label)",
    )
    ap.add_argument(
        "--no-rotate-cities",
        action="store_false",
        dest="rotate_cities",
        help="Don't rotate cities",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        default=DEFAULT_DRY_RUN,
        help="Do everything except copy originals",
    )
    ap.add_argument(
        "--no-dry-run",
        action="store_false",
        dest="dry_run",
        help="Actually move files (not just simulate)",
    )
    ap.add_argument(
        "--phash-only",
        action="store_true",
        help="TEST MODE: Cluster using only pHash (visual similarity), ignore filename/time",
    )
    args = ap.parse_args()

    input_dir = Path(args.input).expanduser()
    out_dir = Path(args.output).expanduser()
    work_dir = out_dir / "_work"
    organized_dir = out_dir / "organized_photos"  # Separate folder for final output
    work_dir.mkdir(parents=True, exist_ok=True)
    organized_dir.mkdir(parents=True, exist_ok=True)

    # 1) Ingest
    print("=" * 60)
    print("STEP 1: INGESTION")
    print("=" * 60)
    items = ingest(input_dir, work_dir)

    name_map: Dict[str, any] = {it.id: name_features(it.path) for it in items}

    print(f"Ingested: {len(items)} images")
    gps_ct = sum(1 for it in items if it.gps)
    print(f"With GPS: {gps_ct}  Without GPS: {len(items)-gps_ct}")

    # Peek at first 5 with GPS
    for it in list(x for x in items if x.gps)[:5]:
        print("GPS sample:", it.path.name, it.gps)

    if not items:
        print("No images found.")
        return

    # Persist ingest info
    ingest_json = [
        {
            "id": it.id,
            "path": str(it.path),
            "thumb": str(it.thumb),
            "dt": it.dt.isoformat() if it.dt else None,
            "gps": it.gps,
            "phash": str(it.h) if it.h else None,
            "name": name_map[it.id].raw,
        }
        for it in items
    ]
    with open(work_dir / "ingest.json", "w", encoding="utf-8") as f:
        json.dump(ingest_json, f, indent=2)

    # 2) Clustering
    print("\n" + "=" * 60)
    print("STEP 2: CLUSTERING")
    if args.phash_only:
        print("🧪 TEST MODE: pHash-only clustering")
    print("=" * 60)

    # Split items by GPS presence
    with_gps = [it for it in items if it.gps]
    without_gps = [it for it in items if not it.gps]

    # GPS-only clustering: returns (multi_photo_clusters, singletons)
    # Singletons get re-clustered using full hierarchical strategy
    site_meters = args.site_distance_feet * 0.3048
    gps_groups, gps_singletons = cluster_gps_only(with_gps, max_meters=site_meters)

    if gps_singletons:
        print(
            f"📍 Found {len(gps_singletons)} GPS singletons → re-clustering via hierarchical strategy"
        )

    # Combine GPS singletons with non-GPS photos for fused clustering
    items_for_fused = without_gps + gps_singletons

    # For items without GPS (+ GPS singletons), choose clustering strategy
    if args.phash_only:
        # TEST MODE: Use only pHash for clustering (visual similarity)
        print(f"Using pHash-only clustering (threshold: {args.hash_threshold})")
        th_groups = cluster_phash_only(
            items_for_fused, hash_threshold=args.hash_threshold
        )
    else:
        # NORMAL MODE: Full hierarchical fused clustering
        # Strategy 1: time+filename+hash (if datetime available)
        # Strategy 2: filename+hash (if strong filename match)
        # Strategy 3: hash only (fallback)
        th_groups = fused_cluster(
            items_for_fused,
            name_map,
            fuse_threshold=DEFAULT_FUSE_THRESHOLD,
            max_edges_per_node=DEFAULT_MAX_EDGES,
        )

    # Save fused clustering explanation
    explain = []
    for gi, g in enumerate(th_groups, 1):
        rows = []
        for it in g:
            nf = name_map[it.id]
            rows.append(
                {
                    "id": it.id,
                    "prefix": nf.prefix,
                    "num": nf.num,
                    "dt": it.dt.isoformat() if it.dt else None,
                }
            )
        explain.append({"cluster": gi, "count": len(g), "items": rows})
    with open(work_dir / "fused_explain_no_gps.json", "w", encoding="utf-8") as f:
        json.dump(explain, f, indent=2)

    # Combine
    groups = gps_groups + th_groups

    # Tag each item with its clustering strategy for later separation
    for group in gps_groups:
        for item in group:
            item.strategy = "gps_location"

    for group in th_groups:
        # Determine strategy based on cluster characteristics
        has_datetime_count = sum(1 for item in group if item.dt is not None)
        if has_datetime_count >= len(group) / 2:
            strategy = "time+filename+hash"
        else:
            # Check if filename similarity was strong
            # For now, default to hash_only for non-GPS, non-time clusters
            strategy = "hash_only"

        for item in group:
            item.strategy = strategy

    # NOTE: Singleton assignment moved to after classification (unified matching flow)
    # Cluster summary will be written after classification when groups are finalized

    # 3) Classification (OPTIMIZED: classify only cluster examples)
    print("\n" + "=" * 60)
    print("STEP 3: CLASSIFICATION (Unified Matching)")
    print("=" * 60)

    labels: Dict[str, Dict] = {
        i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""} for i in items
    }

    if args.classify:
        from .config import (
            ENABLE_UNIFIED_MATCHING,
            CONFIDENT_STRATEGIES,
            UNCERTAIN_STRATEGIES,
        )

        if args.assign_singletons and ENABLE_UNIFIED_MATCHING:
            # UNIFIED MATCHING: Simplified 3-phase approach
            print("🔄 Using unified matching (singletons + hash_only clusters)")

            # Convert groups to (cluster_id, items) format
            indexed_groups = [(idx, g) for idx, g in enumerate(groups)]

            # Phase 1: Separate confident vs uncertain clusters
            print("\n📊 Phase 1: Separating confident vs uncertain clusters...")
            confident_clusters, uncertain_items = separate_confident_uncertain_clusters(
                indexed_groups,
                CONFIDENT_STRATEGIES,
                UNCERTAIN_STRATEGIES,
            )

            print(f"  ✅ Confident clusters: {len(confident_clusters)}")
            print(f"  ⚠️  Uncertain items: {len(uncertain_items)}")

            # Phase 2: Classify confident clusters FIRST
            print("\n🎯 Phase 2: Classifying confident clusters...")
            confident_labels = {}
            if confident_clusters:
                # Extract just the items (not the cluster_id) for classification
                confident_groups_only = [items for _, items in confident_clusters]

                print(
                    f"  🖼️  Classifying {len(confident_groups_only)} confident clusters..."
                )
                confident_labels = classify_cluster_examples(
                    confident_groups_only, args.batch_size, args.model
                )
                labels.update(confident_labels)

                # Map cluster_id -> label for uncertain matching
                cluster_id_to_label = {}
                for cluster_id, items in confident_clusters:
                    # Get label for first item in cluster (all items get same label)
                    first_item_label = confident_labels.get(items[0].id, {})
                    cluster_id_to_label[cluster_id] = first_item_label

            # Phase 3: Match uncertain items against confident clusters
            print("\n🔗 Phase 3: Matching uncertain items...")
            if uncertain_items and confident_clusters:
                assignments = match_uncertain_items_with_collage(
                    uncertain_items,
                    confident_clusters,
                    cluster_id_to_label,
                    model=args.model,
                )

                # Apply matches to groups
                groups_updated = apply_matches_to_groups(indexed_groups, assignments)

                # Extract just the items (remove cluster_ids)
                groups = [items for _, items in groups_updated]

                matched = sum(1 for cid in assignments.values() if cid != -1)
                print(
                    f"  ✅ Matched {matched}/{len(uncertain_items)} uncertain items to confident clusters"
                )
            else:
                # Just extract items from indexed groups
                groups = [items for _, items in indexed_groups]

            # Phase 4: Classify any remaining unclassified clusters
            print("\n🔍 Phase 4: Classifying remaining clusters...")
            remaining_groups = [g for g in groups if g[0].id not in labels]
            if remaining_groups:
                print(f"  🖼️  Classifying {len(remaining_groups)} remaining clusters...")
                remaining_labels = classify_cluster_examples(
                    remaining_groups, args.batch_size, args.model
                )
                labels.update(remaining_labels)

            total_images = sum(len(g) for g in groups)
            savings_pct = (
                ((total_images - len(groups)) / total_images * 100)
                if total_images
                else 0
            )
            print(f"\n💰 Total Cost Savings: {savings_pct:.0f}% fewer API requests!")

        else:
            # ORIGINAL FLOW: No unified matching, just classify all clusters
            print(f"🖼️  Classifying all {len(groups)} clusters...")
            labels = classify_cluster_examples(groups, args.batch_size, args.model)

            total_images = sum(len(g) for g in groups)
            savings_pct = (
                ((total_images - len(groups)) / total_images * 100)
                if total_images
                else 0
            )
            print(f"💰 Cost Savings: {savings_pct:.0f}% fewer API requests!")

        with open(work_dir / "labels.json", "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2)
    else:
        print("Classification disabled, using 'unknown' labels.")

    # Write cluster summary with full file lists and thumbnail paths
    # AFTER classification, when groups are finalized
    print("\n📝 Writing final cluster summary...")
    summary = []
    cluster_num = 1
    final_gps_count = 0
    final_non_gps_count = 0

    for g in groups:
        # Determine if this is a GPS or non-GPS cluster
        has_gps = any(item.gps for item in g)

        if has_gps:
            strategy = "gps_location"
            final_gps_count += 1
        else:
            # Determine which fused strategy was used
            if args.phash_only:
                strategy = "phash_only_test"
            else:
                # Determine which fused strategy was likely used
                has_datetime_count = sum(1 for item in g if item.dt is not None)
                if has_datetime_count >= len(g) / 2:
                    strategy = "time+filename+hash"
                else:
                    # Check filename similarity strength
                    name_feats = [name_map[item.id] for item in g]
                    has_same_prefix = len(set(nf.prefix for nf in name_feats)) == 1
                    has_close_numbers = all(nf.num is not None for nf in name_feats)

                    if has_same_prefix and has_close_numbers:
                        strategy = "filename+hash"
                    else:
                        strategy = "hash_only"
            final_non_gps_count += 1

        summary.append(
            {
                "cluster": cluster_num,
                "count": len(g),
                "strategy": strategy,
                "has_gps": has_gps,
                "example": g[0].path.name,
                "files": [
                    {
                        "name": item.path.name,
                        "thumb": get_thumb_path(item.path.name, work_dir),
                    }
                    for item in g
                ],
            }
        )
        cluster_num += 1
    with open(work_dir / "clusters.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # 4) Organization
    print("\n" + "=" * 60)
    print("STEP 4: ORGANIZATION")
    print("=" * 60)

    if not args.dry_run:
        organize(
            groups,
            labels,
            organized_dir,  # Use separate organized_photos directory
            args.brand,
            args.rotate_cities,
            args.use_semantic_keywords,
        )
    else:
        print("Dry run complete. See _work folder for JSON outputs.")

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)

    # Print clustering statistics at the end (using final counts after singleton assignment)
    print_clustering_stats(summary, final_gps_count, final_non_gps_count)


if __name__ == "__main__":
    # Inline defaults so you can press Run without typing CLI args
    if len(sys.argv) == 1:
        sys.argv.extend(
            shlex.split(
                f"run --input '{IMAGE_DIR}' --output '{DEFAULT_OUTPUT_DIR}' --rotate-cities "
                f"--time-gap-min {DEFAULT_TIME_GAP_MINUTES} "
                f"--batch-size {DEFAULT_BATCH_SIZE} "
                f"--hash-threshold {DEFAULT_HASH_THRESHOLD} "
                f"--model {DEFAULT_MODEL} "
                # "--classify"  # Use ChatGPT multi-image ai_classification
                "--dry-run "  # Do everything except copy originals
                "--rotate-cities "  # Rotate cities if GPS missing
            )
        )
    main()
