#!/usr/bin/env python3
"""
V1 Photo Organizer CLI

Pipeline:
 1) ingest: walk input folder, make thumbnails, extract EXIF time/GPS, compute pHash
 2) classify: batch multi-image classification with ChatGPT Vision (Structured Outputs)
 3) cluster: time + pHash centroid with AND logic
 4) label: majority vote per cluster, optional API refinement for ambiguous clusters
 5) organize: assign city, generate SEO filenames, write manifest, copy/move originals

Quick start:
  export OPENAI_API_KEY=sk-...
  pip install pillow pillow-heif imagehash tqdm python-slugify
  # Optional if using --classify
  pip install openai

Examples:
  python v1_photo_cli.py run
    --input "/path/to/photos"
    --output "/path/to/organized"
    --brand "bespoke-concrete"
    --time-gap-min 20 --hash-threshold 6
    --classify --batch-size 12

Notes:
 - For API classification, thumbnails are base64-encoded and sent in batches.
 - Keep batch-size to ~10-20 depending on image dimensions to avoid token limits.
 - If --classify is omitted, step 2 is skipped and labels default to "project".
"""
from __future__ import annotations
from collections import deque
import argparse, base64, hashlib, json, shlex, sys, shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import radians, sin, cos, asin, sqrt
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import numpy as np

from PIL import Image, ExifTags
from slugify import slugify
import imagehash
from tqdm import tqdm


import re
from collections import defaultdict, deque
import exifread


NAME_TOKEN_RE = re.compile(r"([A-Za-z]+)?(?:[_-])?(\d{2,})(.*)", re.ASCII)


# --- Optional import of OpenAI client only if classify is requested ---
try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

SUPPORTED_EXTS = {
    ".jpg",
    ".JPG",
    ".JPEG",
    ".jpeg",
    ".PNG",
    ".WEBP",
    ".BMP",
    ".TIF",
    ".TIFF",
    ".HEIC",
    ".HEIF",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".heic",
    ".heif",
}

CITIES = {
    "puyallup": (47.1854, -122.2929),
    "bellevue": (47.6101, -122.2015),
    "tacoma": (47.2529, -122.4443),
}

LABELS = [
    "stamped-concrete-patio",
    "concrete-patio",
    "concrete-walkway",
    "concrete-steps",
    "concrete-driveway",
    "exposed-aggregate",
    "retaining-wall",
    "concrete-slab",
    "concrete-repair",
    "decorative-concrete",
    "unknown",
]

SURFACE_CANON = {
    "stamped-concrete-patio": ("stamped-concrete-patio", "patio"),
    "concrete-patio": ("concrete-patio", "patio"),
    "decorative-concrete": ("decorative-concrete", "decorative"),
    "exposed-aggregate": ("exposed-aggregate-concrete", "exposed-aggregate"),
    "concrete-walkway": ("concrete-walkway", "walkway"),
    "concrete-steps": ("porch-concrete", "steps"),
    "concrete-driveway": ("concrete-driveway", "driveway"),
    "retaining-wall": ("retaining-wall-contractor", "retaining-wall"),
    "concrete-slab": ("concrete-contractor-residential", "slab"),
    "concrete-repair": ("concrete-repair", "repair"),
    "unknown": ("concrete-company", "project"),
}

SCRIPT_DIR = Path(__file__).resolve().parent


IMAGE_DIR = "/Users/austinserb/Desktop/RC Photos"


class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def cluster_gps_only(items: list[Item], max_meters: float) -> list[list[Item]]:
    # Cluster strictly by location threshold; ignore time completely.
    gps_items = [(idx, it) for idx, it in enumerate(items) if it.gps]
    if not gps_items:
        return []
    n = len(gps_items)
    dsu = DSU(n)
    for i in range(n):
        gi, it_i = gps_items[i]
        for j in range(i + 1, n):
            gj, it_j = gps_items[j]
            if meters_between(it_i.gps, it_j.gps) <= max_meters:
                dsu.union(i, j)
    comps: dict[int, list[Item]] = {}
    for i in range(n):
        r = dsu.find(i)
        comps.setdefault(r, []).append(gps_items[i][1])
    return list(comps.values())


@dataclass
class NameFeat:
    prefix: str
    num: Optional[int]
    suffix: str
    raw: str


def name_features(p: Path) -> NameFeat:
    base = p.stem  # without extension
    m = NAME_TOKEN_RE.fullmatch(base)
    if not m:
        # fallback: longest numeric group anywhere
        nums = re.findall(r"\d{2,}", base)
        num = int(nums[-1]) if nums else None
        # common prefix heuristic
        pref = base.split(nums[-1])[0] if nums else base[:3].lower()
        return NameFeat(prefix=pref.lower(), num=num, suffix="", raw=base.lower())
    pref, num, suf = m.groups()
    return NameFeat(
        prefix=(pref or "").lower(),
        num=int(num),
        suffix=(suf or "").lower(),
        raw=base.lower(),
    )


@dataclass
class Item:
    id: str
    path: Path
    thumb: Path
    dt: Optional[datetime]
    gps: Optional[Tuple[float, float]]
    h: Optional[imagehash.ImageHash]


# --------------------
# Helpers
# --------------------


def register_heif():
    try:
        from pillow_heif import register_heif_opener  # type: ignore

        register_heif_opener()
    except Exception:
        pass


def read_exif_dt(p: Path) -> Optional[datetime]:
    try:
        # Try exifread first (better EXIF support)
        with open(p, "rb") as f:
            tags = exifread.process_file(f, details=False)

        date_keys = [
            "EXIF DateTimeOriginal",
            "EXIF DateTimeDigitized",
            "Image DateTime",
            "EXIF DateTime",
            "CreateDate",
            "Image DateTimeOriginal",
        ]

        for key in date_keys:
            if key in tags:
                raw = str(tags[key])
                raw = raw.strip()

                # Handle different formats
                for fmt in [
                    "%Y:%m:%d %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y/%m/%d %H:%M:%S",
                ]:
                    try:
                        return datetime.strptime(raw, fmt)
                    except:
                        continue

        # Fallback to Pillow method if exifread fails
        img = Image.open(p)
        exif = img.getexif()
        if exif:
            # ... rest of your original code
            pass

    except Exception:
        pass
    return None


def read_exif_gps(p: Path) -> Optional[Tuple[float, float]]:
    try:
        img = Image.open(p)
        exif = img.getexif()
        if not exif:
            return None

        # Try to get GPS IFD directly
        gps_ifd = exif.get_ifd(0x8825)  # 0x8825 is the GPS IFD tag
        if not gps_ifd:
            # Fallback to old method
            tag_map = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
            gps = tag_map.get("GPSInfo")
            if not gps:
                return None
            gps_map = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps.items()}
        else:
            gps_map = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}

        def norm_ref(v):
            if isinstance(v, bytes):
                v = v.decode("ascii", "ignore")
            if not isinstance(v, str):
                return v
            v = v.strip().upper()
            if v.startswith("NORTH"):
                return "N"
            if v.startswith("SOUTH"):
                return "S"
            if v.startswith("EAST"):
                return "E"
            if v.startswith("WEST"):
                return "W"
            return v

        def rat_to_float(x):
            try:
                return float(x.numerator) / float(x.denominator)
            except Exception:
                pass
            if isinstance(x, (tuple, list)) and len(x) == 2:
                return float(x[0]) / float(x[1])
            try:
                return float(x)
            except Exception:
                return None

        def to_deg(values):
            if values is None:
                return None
            if isinstance(values, (int, float)):
                return float(values)
            if isinstance(values, str):
                try:
                    return float(values)
                except Exception:
                    return None
            try:
                d = rat_to_float(values[0])
                m = rat_to_float(values[1])
                s = rat_to_float(values[2])
                if None in (d, m, s):
                    return None
                return d + m / 60.0 + s / 3600.0
            except Exception:
                return None

        lat = to_deg(gps_map.get("GPSLatitude"))
        lon = to_deg(gps_map.get("GPSLongitude"))
        if lat is None or lon is None:
            return None

        lat_ref = norm_ref(gps_map.get("GPSLatitudeRef"))
        lon_ref = norm_ref(gps_map.get("GPSLongitudeRef"))
        if lat_ref == "S":
            lat = -lat
        if lon_ref == "W":
            lon = -lon
        return (lat, lon)
    except Exception as e:
        # print(f"GPS extraction error for {p.name}: {e}")  # Uncomment to debug
        return None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


def meters_between(a: tuple[float, float], b: tuple[float, float]) -> float:
    # haversine in meters
    return haversine(a[0], a[1], b[0], b[1]) * 1000.0


def nearest_city(
    gps: Optional[Tuple[float, float]], fallback_cycle: List[str], idx: int
) -> str:
    if gps:
        lat, lon = gps
        best = None
        best_city = None
        for c, (clat, clon) in CITIES.items():
            d = haversine(lat, lon, clat, clon)
            if best is None or d < best:
                best, best_city = d, c
        if best_city:
            print("best_city: ", best_city)
            return best_city
    print("fallback_cycle: ", fallback_cycle[idx % len(fallback_cycle)])
    return fallback_cycle[idx % len(fallback_cycle)]


def ensure_thumb(src: Path, dst: Path, max_px: int = 768):
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail((max_px, max_px))
        im.save(dst, "JPEG", quality=50, optimize=True)


def phash(path_or_image) -> Optional[imagehash.ImageHash]:
    try:
        if isinstance(path_or_image, Path):
            im = Image.open(path_or_image).convert("RGB")
        else:
            im = path_or_image.convert("RGB")
        return imagehash.phash(im, hash_size=16)
    except Exception:
        return None


def short_hash(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()[:8]


# --------------------
# Ingest
# --------------------


def ingest(input_dir: Path, work_dir: Path) -> List[Item]:
    register_heif()
    thumbs_dir = work_dir / "thumbs"
    thumbs_dir.mkdir(parents=True, exist_ok=True)

    items: List[Item] = []
    files = [
        p
        for p in input_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS
    ]
    for p in tqdm(files, desc="Ingest", unit="img"):
        thumb = thumbs_dir / f"{p.stem}.jpg"
        try:
            ensure_thumb(p, thumb)
        except Exception as e:
            print(f"[warn] thumb failed for {p.name}: {e}")
            continue
        items.append(
            Item(
                id=p.name,
                path=p,
                thumb=thumb,
                dt=read_exif_dt(p),
                gps=read_exif_gps(p),
                h=phash(thumb),
            )
        )
    return items


def lcp_len(a: str, b: str) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def filename_score(a: NameFeat, b: NameFeat) -> float:
    score = 0.0
    # strong if same prefix and close numbers
    if (
        a.num is not None
        and b.num is not None
        and a.prefix == b.prefix
        and a.prefix != ""
    ):
        d = abs(a.num - b.num)
        if d == 0:
            score += 1.0
        elif d <= 1:
            score += 0.9
        elif d <= 3:
            score += 0.7
        elif d <= 10:
            score += 0.4
    # common prefix of the whole stem helps even without numbers
    lcp = lcp_len(a.raw, b.raw)
    if lcp >= 6:
        score += 0.4
    elif lcp >= 4:
        score += 0.2
    # edited copies "(1)", "copy", "edited" should not break ties
    edits = ["(1)", "copy", "edited", "final", "export"]
    if any(e in a.raw for e in edits) and any(e in b.raw for e in edits):
        score += 0.1
    return min(score, 1.0)


def phash_score(
    ha: Optional[imagehash.ImageHash], hb: Optional[imagehash.ImageHash]
) -> float:
    if ha is None or hb is None:
        return 0.0
    # smaller distance = higher score
    d = ha - hb
    if d <= 4:
        return 1.0
    if d <= 6:
        return 0.8
    if d <= 8:
        return 0.6
    if d <= 12:
        return 0.3
    return 0.0


def time_score(da: Optional[datetime], db: Optional[datetime]) -> float:
    if not da or not db:
        return 0.0
    dt = abs((da - db).total_seconds()) / 60.0  # minutes
    if dt <= 5:
        return 1.0
    if dt <= 15:
        return 0.7
    if dt <= 30:
        return 0.5
    if dt <= 120:
        return 0.2
    return 0.0


def fuse_score(it_a: Item, it_b: Item, nf: Dict[str, NameFeat]) -> float:
    a, b = nf[it_a.id], nf[it_b.id]
    s_name = filename_score(a, b)
    s_hash = phash_score(it_a.h, it_b.h)
    s_time = time_score(it_a.dt, it_b.dt)
    # weighted sum; filename and hash carry more than time
    return 0.5 * s_name + 0.35 * s_hash + 0.15 * s_time


def fused_cluster(
    items: List[Item],
    nf: Dict[str, NameFeat],
    fuse_threshold: float = 0.75,
    max_edges_per_node: int = 20,
) -> List[List[Item]]:
    """
    Build a similarity graph using the fused score and return connected components.
    To keep it fast on hundreds of images, only connect each node to its top-K neighbors.
    """
    if not items:
        return []
    # index by simple buckets to prune comparisons: same prefix bucket
    buckets = defaultdict(list)
    for it in items:
        buckets[nf[it.id].prefix].append(it)

    adj: Dict[str, List[str]] = defaultdict(list)

    def consider(pool: List[Item]):
        # compute pairwise scores in a pruned way
        for i, a in enumerate(pool):
            # pick candidates: nearest numbers by absolute diff if numeric exists
            candidates = sorted(
                pool,
                key=lambda x: (
                    abs((nf[a.id].num or 10**9) - (nf[x.id].num or 10**9)),
                    lcp_len(nf[a.id].raw, nf[x.id].raw),
                ),
            )[: max_edges_per_node * 4]
            scored = []
            for b in candidates:
                if a.id == b.id:
                    continue
                s = fuse_score(a, b, nf)
                scored.append((s, b))
            scored.sort(reverse=True, key=lambda x: x[0])
            for s, b in scored[:max_edges_per_node]:
                if s >= fuse_threshold:
                    adj[a.id].append(b.id)
                    adj[b.id].append(a.id)

    for pref, pool in buckets.items():
        # light heuristic: also try a global pool for empty/short prefixes
        consider(pool)

    # connected components over adj; include isolated nodes
    id_to_item = {it.id: it for it in items}
    seen = set()
    groups: List[List[Item]] = []
    for it in items:
        if it.id in seen:
            continue
        comp = []
        q = deque([it.id])
        seen.add(it.id)
        while q:
            u = q.popleft()
            comp.append(id_to_item[u])
            for v in adj.get(u, []):
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        groups.append(comp)
    return groups


# --------------------
# Classify via ChatGPT API (multi-image batches)
# --------------------


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def classify_batches(items: List[Item], batch_size: int, model: str) -> Dict[str, Dict]:
    if OpenAI is None:
        print("[warn] openai package not installed, skipping classification")
        return {
            i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""}
            for i in items
        }
    client = OpenAI()

    out: Dict[str, Dict] = {}
    schema = {
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
                            "label": {"type": "string", "enum": LABELS},
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                            },
                            "descriptor": {"type": "string"},
                        },
                        "required": ["id", "label", "confidence"],
                    },
                }
            },
            "required": ["images"],
        },
    }

    def do_batch(batch: List[Item]):
        messages = [
            {
                "role": "system",
                "content": "You are an image classifier for concrete construction photos. Return strict JSON only.",
            },
            {
                "role": "user",
                "content": (
                    "Allowed labels: "
                    + ", ".join(LABELS)
                    + ". For each image return id, label, confidence (0-1), and a short descriptor."
                ),
            },
        ]
        for it in batch:
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"id={it.id}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64(it.thumb)}"
                            },
                        },
                    ],
                }
            )
        resp = client.chat.completions.create(
            model=model,
            response_format={"type": "json_schema", "json_schema": schema},
            messages=messages,
        )
        data = json.loads(resp.choices[0].message.content)
        for row in data.get("images", []):
            out[row["id"]] = {
                "label": row.get("label", "unknown"),
                "confidence": float(row.get("confidence", 0)),
                "descriptor": row.get("descriptor", ""),
            }

    for i in range(0, len(items), batch_size):
        do_batch(items[i : i + batch_size])
    return out


# --------------------
# Clustering: time + pHash centroid (AND logic)
# --------------------


def phash_median(hashes):

    hashes = [h for h in hashes if h is not None]
    if not hashes:
        return None
    ref = hashes[0]
    bit_count = ref.hash.size  # 256 for 16x16
    acc = np.zeros(bit_count, dtype=int)
    for h in hashes:
        flat = h.hash.flatten().astype(bool)
        acc += np.where(flat, 1, -1)
    arr = (acc >= 0).reshape(ref.hash.shape)  # (16,16)
    return imagehash.ImageHash(arr)


def cluster(
    items: List[Item], time_gap_min: int, hash_threshold: int
) -> List[List[Item]]:
    items_sorted = sorted(items, key=lambda x: (x.dt or datetime.min, x.path.name))
    clusters: List[List[Item]] = []
    current: List[Item] = []

    for itm in items_sorted:
        if not current:
            current = [itm]
            continue
        latest_dt = max((x.dt for x in current if x.dt), default=None)
        dt_ok = True
        if itm.dt and latest_dt:
            dt_ok = (itm.dt - latest_dt) <= timedelta(minutes=time_gap_min)
        centroid = phash_median([x.h for x in current])
        hash_ok = True
        if centroid is not None and itm.h is not None:
            try:
                hash_ok = (itm.h - centroid) <= hash_threshold
            except Exception:
                hash_ok = True
        # AND logic: require both
        if dt_ok and hash_ok:
            current.append(itm)
        else:
            clusters.append(current)
            current = [itm]
    if current:
        clusters.append(current)
    return clusters


# --------------------
# Organize/rename
# --------------------


def organize(
    groups: List[List[Item]],
    labels: Dict[str, Dict],
    out_dir: Path,
    brand: str,
    rotate_cities: bool,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    cycle = ["puyallup", "bellevue", "tacoma"]

    manifest = []
    for gi, grp in enumerate(groups, start=1):
        # pick surface by majority vote over classified labels
        votes: Dict[str, int] = {}
        for it in grp:
            lab = labels.get(it.id, {}).get("label", "unknown")
            votes[lab] = votes.get(lab, 0) + 1
        label = max(votes, key=votes.get) if votes else "unknown"
        primary, surface = SURFACE_CANON.get(
            label, SURFACE_CANON["unknown"]
        )  # canonicalize

        # city
        gps_any = next((it.gps for it in grp if it.gps), None)
        city = nearest_city(gps_any, cycle if rotate_cities else ["bellevue"], gi - 1)

        # folder name
        rep_dt = next((it.dt for it in grp if it.dt), None)
        date_part = rep_dt.strftime("%Y-%m-%d") if rep_dt else f"cluster-{gi:02d}"
        folder = out_dir / f"{date_part}-{surface}-{city}"
        folder.mkdir(parents=True, exist_ok=True)

        for it in grp:
            pieces = []
            if brand:
                pieces.append(slugify(brand, lowercase=True))
            pieces += [primary, surface, city, short_hash(it.path)]
            base = "-".join([slugify(x, lowercase=True) for x in pieces if x])
            ext = it.path.suffix.lower()
            if ext in {".heic", ".heif"}:
                ext = ".jpg"
            dst = folder / f"{base}{ext}"
            try:
                shutil.copy2(it.path, dst)
            except Exception as e:
                print(f"[warn] copy failed {it.path.name}: {e}")
                continue
            manifest.append(
                {
                    "src": str(it.path),
                    "dst": str(dst),
                    "cluster": gi,
                    "label": label,
                    "city": city,
                }
            )
    # write manifest
    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Wrote {len(manifest)} files. Manifest at {out_dir/'manifest.json'}")


# --------------------
# CLI
# --------------------


def main():
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

    # 1) ingest
    items = ingest(input_dir, work_dir)

    name_map: Dict[str, NameFeat] = {it.id: name_features(it.path) for it in items}

    print(f"Ingested: {len(items)} images")
    gps_ct = sum(1 for it in items if it.gps)
    print(f"With GPS: {gps_ct}  Without GPS: {len(items)-gps_ct}")
    # peek at first 5 with GPS
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

        # Split items by GPS presence
    with_gps = [it for it in items if it.gps]
    without_gps = [it for it in items if not it.gps]

    # 1) GPS-only clusters: same site within X feet = same project (ignore time)
    site_meters = args.site_distance_feet * 0.3048
    gps_groups = cluster_gps_only(with_gps, max_meters=site_meters)

    # 2) For items without GPS, use your existing time ∧ pHash clustering
    th_groups = fused_cluster(
        without_gps, name_map, fuse_threshold=0.75, max_edges_per_node=20
    )
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

    # (Optional) Write a quick summary to _work
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

    # 2) classify
    labels: Dict[str, Dict] = {
        i.id: {"label": "unknown", "confidence": 0.0, "descriptor": ""} for i in items
    }
    if args.classify:
        labels = classify_batches(items, args.batch_size, args.model)
        with open(work_dir / "labels.json", "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2)
    else:
        print("Classification disabled, using 'unknown' labels.")

    # 4 & 5) organize
    if not args.dry_run:
        organize(groups, labels, out_dir, args.brand, args.rotate_cities)
    else:
        print("Dry run complete. See _work folder for JSON outputs.")


if __name__ == "__main__":
    # Inline defaults so you can press Run without typing CLI args
    if len(sys.argv) == 1:
        sys.argv.extend(
            shlex.split(
                f"run --input '{(IMAGE_DIR)}' --output '{(SCRIPT_DIR/'organized').as_posix()}' --rotate-cities "
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
