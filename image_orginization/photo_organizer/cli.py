#!/usr/bin/env python3
"""
CLI entry point for Photo Organizer.

Pipeline:
 1) ingest: walk input folder, make thumbnails, extract EXIF time/GPS, compute pHash
 2) classify: batch multi-image classification with ChatGPT Vision (Structured Outputs)
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

from .config import IMAGE_DIR, SCRIPT_DIR
from .ingestion import ingest
from .classification import classify_batches
from .clustering import cluster_gps_only, fused_cluster
from .organization import organize
from .utils.filename import name_features


def main():
    """Main CLI entry point."""
    ap = argparse.ArgumentParser(
        description="Batch classify, cluster, and organize construction photos."
    )
    ap.add_argument(
        "--site-distance-feet",
        type=float,
        default=300.0,
        help="GPS-only site merge radius; images within this distance form one project, regardless of time",
    )

    ap.add_argument("run", nargs="?", help="Execute full pipeline")
    ap.add_argument("--input", required=True, help="Input folder with images")
    ap.add_argument(
        "--output", default=str(SCRIPT_DIR / "organized"), help="Output folder"
    )
    ap.add_argument("--brand", default="", help="Optional brand slug")
    ap.add_argument(
        "--time-gap-min",
        type=int,
        default=20,
        help="Max minutes to keep photos in same cluster",
    )
    ap.add_argument(
        "--hash-threshold",
        type=int,
        default=6,
        help="Max pHash distance to keep in same cluster",
    )
    ap.add_argument(
        "--classify", action="store_true", help="Use ChatGPT multi-image classification"
    )
    ap.add_argument("--model", default="gpt-4o", help="OpenAI vision model")
    ap.add_argument("--batch-size", type=int, default=12, help="Images per API batch")
    ap.add_argument(
        "--rotate-cities", action="store_true", help="Rotate cities if GPS missing"
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Do everything except copy originals"
    )
    args = ap.parse_args()

    input_dir = Path(args.input).expanduser()
    out_dir = Path(args.output).expanduser()
    work_dir = out_dir / "_work"
    work_dir.mkdir(parents=True, exist_ok=True)

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
    print("=" * 60)

    # Split items by GPS presence
    with_gps = [it for it in items if it.gps]
    without_gps = [it for it in items if not it.gps]

    # GPS-only clusters: same site within X feet = same project (ignore time)
    site_meters = args.site_distance_feet * 0.3048
    gps_groups = cluster_gps_only(with_gps, max_meters=site_meters)

    # For items without GPS, use fused clustering
    th_groups = fused_cluster(
        without_gps, name_map, fuse_threshold=0.75, max_edges_per_node=20
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
    with open(work_dir / "fused_explain.json", "w", encoding="utf-8") as f:
        json.dump(explain, f, indent=2)

    # Combine
    groups = gps_groups + th_groups

    # Write cluster summary
    summary = [
        {
            "cluster": i + 1,
            "count": len(g),
            "has_gps": any(x.gps for x in g),
            "example": g[0].path.name,
        }
        for i, g in enumerate(groups)
    ]
    with open(work_dir / "clusters.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(
        f"Clusters formed: {len(groups)} (GPS groups: {len(gps_groups)}, non-GPS groups: {len(th_groups)})"
    )

    # 3) Classification
    print("\n" + "=" * 60)
    print("STEP 3: CLASSIFICATION")
    print("=" * 60)

    labels: Dict[str, Dict] = {
        i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""} for i in items
    }
    if args.classify:
        labels = classify_batches(items, args.batch_size, args.model)
        with open(work_dir / "labels.json", "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2)
    else:
        print("Classification disabled, using 'unknown' labels.")

    # 4) Organization
    print("\n" + "=" * 60)
    print("STEP 4: ORGANIZATION")
    print("=" * 60)

    if not args.dry_run:
        organize(groups, labels, out_dir, args.brand, args.rotate_cities)
    else:
        print("Dry run complete. See _work folder for JSON outputs.")

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    # Inline defaults so you can press Run without typing CLI args
    if len(sys.argv) == 1:
        sys.argv.extend(
            shlex.split(
                f"run --input '{IMAGE_DIR}' --output '{(SCRIPT_DIR/'organized').as_posix()}' --rotate-cities "
                "--time-gap-min 600 "  # 10 hours between photos
                "--batch-size 12 "  # 12 photos per batch
                "--hash-threshold 8 "  # 8 bits difference
                "--model gpt-4o "  # OpenAI model
                # "--classify"  # Use ChatGPT multi-image classification
                "--dry-run "  # Do everything except copy originals
                "--rotate-cities "  # Rotate cities if GPS missing
            )
        )
    main()
