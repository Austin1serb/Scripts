
## 1) Script args to add or tighten

* `--business-slug rc-concrete`
* `--state wa`
* `--default-city puyallup`  fallback when GPS missing
* `--gps-radius-m 275`  tighter site-radius, reduces cross-street bleed
* `--time-window-min 180`  clamp “same-job” shots within 3 hours when GPS matches
* `--seq-gap-max 3`  cap for filename sequence adjacency
* `--similarity-threshold 0.87`  for fused pHash confirmations
* `--min-cluster-size 3`  avoid singletons unless GPS+time are near-identical
* `--rotate-cities false`  prefer real geo, not rotation
* `--finish-from-alt true`  let your classifier/ALT hints attach finishes (broom, stamped, exposed)

## 2) LABELS, minimal but complete

Keep your existing set, then **add** these to cover the brief’s service pages and common finishes:

* `stamped-concrete-driveway`
* `stamped-concrete-walkway`
* `exposed-aggregate-driveway`
* `exposed-aggregate-patio`
* `driveway-replacement`
* `sidewalk`
* `foundation-slab`
* `resurfacing`  (for the Repair/Resurfacing page)
* `broom-finish-driveway`  (popular upsell on /concrete-driveways)

> Keep “unknown” as a sink; never delete it. It protects recall when confidence dips.

## 3) SURFACE_CANON, additions only

Add these canonical pairs to your existing dict. Do **not** remove what you already have.

* `"stamped-concrete-driveway": ("stamped-concrete-driveway", "driveway")`
* `"stamped-concrete-walkway": ("stamped-concrete-walkway", "walkway")`
* `"exposed-aggregate-driveway": ("exposed-aggregate-concrete", "driveway")`
* `"exposed-aggregate-patio": ("exposed-aggregate-concrete", "patio")`
* `"driveway-replacement": ("concrete-driveway-replacement", "driveway")`
* `"sidewalk": ("concrete-sidewalk", "sidewalk")`
* `"foundation-slab": ("foundation-concrete-slab", "slab")`
* `"resurfacing": ("concrete-resurfacing", "resurfacing")`
* `"broom-finish-driveway": ("broom-finish-concrete-driveway", "driveway")`

This mirrors the site’s service architecture and the “finishes” cross-links, so filenames naturally reinforce your money pages.

## 4) Optional modifiers to enrich filenames, not new labels

Don’t explode your LABELS with cosmetic variants. Instead expose two **secondary fields** your filename builder can append when present:

**FINISH_CANON**
`{"stamped":"stamped-concrete","exposed":"exposed-aggregate-concrete","broom":"broom-finish"}`

**FEATURE_CANON**
`{"tearout":"tear-out-and-repour","colored":"integral-color","sealed":"sealer-applied"}`

These are appended only when confidently detected, so you avoid bloat and keyword spam.

## 5) Filename recipe, deterministic and compact

Use this exact order, drop empties, hyphenate, lowercase:

```
{primary-surface-or-finish}-{city}-wa-{business}-{index}.jpg
```

Examples your pipeline will emit:

* `stamped-concrete-patio-bellevue-wa-rc-concrete-01.jpg`
* `exposed-aggregate-driveway-tacoma-wa-rc-concrete-03.jpg`
* `driveway-replacement-puyallup-wa-rc-concrete-02.jpg`
* `broom-finish-concrete-driveway-bellevue-wa-rc-concrete-05.jpg`

Rules:

* Service first, then finish if it exists, then city, then state, then brand.
* Never include dates or hashes in the filename. Keep hashes only in `manifest.json` for uniqueness tracking.
* Keep tokens 6 to 10 words, avoid stopwords.
* City must be one of `puyallup | bellevue | tacoma`. If GPS absent, fall back to `--default-city`.

## 6) Where this maps to the brief

* Money services emphasized: Stamped, Driveways, Patios, Exposed Aggregate, Retaining Walls, Repair/Resurfacing.
* City pages fed with city-specific filenames for tacoma and bellevue galleries.
* Visualizer images, if you export them, can use `concrete-visualizer` as the surface key with the same geo+brand tail.

## 7) Guardrails that improve clustering accuracy

* When GPS clusters match but timestamps differ by more than `--time-window-min`, split the cluster.
* If `driveway-replacement` is detected, prefer that over `concrete-driveway`. Replacement is higher intent and fits your “tear-out and re-pour” copy on the driveway page.
* If label confidence is low but FINISH is high (e.g., “exposed”), fall back to `exposed-aggregate-<generic>` plus the correct city.

## 8) Which keywords you’re actually operationalizing

From your list, these are the ones directly expressed by labels or canon slugs, so filenames and ALT text reinforce them without spam:
`concrete contractors, stamped concrete, concrete driveway contractors, concrete driveway, decorative concrete, exposed aggregate concrete, retaining wall contractor, concrete repair, stamped concrete patio, driveway concreters`
The geo pages capture the rest through on-page copy and internal links, not filenames.

---

If you want, I’ll produce a **change-only patch**: additions to `LABELS`, `SURFACE_CANON`, and a short `build_filename()` signature that consumes `{label, city, business, finish, index}` and enforces the rules above.
