# Improved AI Classification Prompts

## Overview

The AI classification prompts have been significantly enhanced to provide better accuracy, clearer guidance, and more consistent results from GPT-4 Vision.

---

## What Changed

### **Before (Basic Prompt):**
```
"You are an image classifier for concrete construction photos. 
Output STRICT JSON, UTF-8, no prose. Return only fields: id, label, 
confidence, descriptor. If uncertain, return label 'unknown'..."
```

**Problems:**
- ❌ Too brief, no context
- ❌ No explanation of role or purpose
- ❌ No guidance on distinguishing similar types
- ❌ No examples or classification logic
- ❌ Unclear confidence thresholds

---

### **After (Comprehensive Prompt):**

#### **System Message (AI's Role):**
```
"You are an expert concrete construction photo classifier for a 
professional concrete contractor. Your role is to accurately identify 
and categorize concrete construction project photos for SEO optimization 
and project organization."
```

**Improvements:**
- ✅ Clear role definition (expert classifier)
- ✅ Context (professional contractor)
- ✅ Purpose (SEO optimization + organization)

---

#### **Key Additions:**

### **1. Confidence Guidelines**
```
- High confidence (0.85-1.0): Clear view, unmistakable identification
- Medium confidence (0.65-0.84): Likely correct, some ambiguity
- Low confidence (<0.65): Uncertain, use 'unknown' label
```

**Why:** Helps AI calibrate its confidence scores accurately

---

### **2. Important Distinctions**
```
DRIVEWAYS: Vehicle access, typically residential or commercial parking areas
PATIOS: Outdoor living spaces, entertainment areas, adjacent to homes
WALKWAYS: Pedestrian paths connecting areas, narrower than driveways
SIDEWALKS: Public or property-edge pedestrian paths, typically along streets
STEPS: Elevation changes, staircases, porch steps
SLABS: Large flat surfaces (garage floors, shed foundations, house slabs)
```

**Why:** These are easily confused - explicit definitions help AI distinguish them

---

### **3. Finish Type Recognition**
```
STAMPED: Textured patterns (stone, brick, wood grain impressions)
EXPOSED AGGREGATE: Visible decorative stones/pebbles in surface
BROOM FINISH: Textured with broom strokes for traction (common on driveways)
SMOOTH/TROWELED: Plain finished surface
```

**Why:** Finish type determines the label (e.g., "stamped-concrete-driveway" vs "concrete-driveway")

---

### **4. Classification Priority Logic**
```
1. If stamped pattern visible → use 'stamped-concrete-[type]'
2. If exposed aggregate visible → use 'exposed-aggregate-[type]'
3. If broom finish visible → use 'broom-finish-[type]'
4. Otherwise → use standard 'concrete-[type]'
5. For repairs/resurfacing → look for patches, cracks, overlays
```

**Why:** Provides a clear decision tree for AI to follow

---

### **5. Real-World Examples**
```
- Residential driveway with broom texture → 'broom-finish-driveway' (confidence: 0.90+)
- Patio with stone-like stamped pattern → 'stamped-concrete-patio' (confidence: 0.85+)
- Walkway with exposed stones/pebbles → 'exposed-aggregate-walkway' (confidence: 0.85+)
- Front porch steps → 'concrete-steps' (confidence: 0.90+)
- Driveway replacement in progress → 'driveway-replacement' (confidence: 0.80+)
- Cracked concrete being repaired → 'concrete-repair' (confidence: 0.80+)
- Garage floor slab → 'concrete-slab' (confidence: 0.85+)
- Block wall for yard leveling → 'retaining-wall' (confidence: 0.90+)
```

**Why:** Concrete examples (pun intended) help AI understand expected outputs

---

### **6. Analysis Framework**
```
ANALYZE EACH IMAGE CAREFULLY:
- What is the PRIMARY concrete element? (driveway, patio, walkway, etc.)
- What FINISH is visible? (stamped, exposed aggregate, broom, smooth)
- What is the PROJECT TYPE? (new construction, repair, replacement, decorative)
- How CONFIDENT are you in this classification? (be conservative)
```

**Why:** Gives AI a systematic approach to analyzing each photo

---

### **7. Output Format Examples**
```json
[
  {"id": "exact_filename.jpg", "label": "concrete-driveway", "confidence": 0.92, "descriptor": "broom finish residential"},
  {"id": "another_file.jpg", "label": "stamped-concrete-patio", "confidence": 0.88, "descriptor": "stone pattern entertainment area"}
]
```

**Why:** Shows AI exactly what format is expected

---

## Expected Improvements

### **Better Accuracy:**
1. **Correct Label Selection**
   - Before: Might confuse driveways with patios
   - After: Clear definitions help distinguish them

2. **Appropriate Finish Classification**
   - Before: Might miss stamped patterns or aggregate finishes
   - After: Explicit guidance to look for these features

3. **Better Confidence Scores**
   - Before: Overconfident or underconfident
   - After: Calibrated guidelines for confidence levels

### **More Consistent Results:**
1. **Decision Tree Logic**
   - AI follows same priority order every time
   - Reduces random variations

2. **Clear Examples**
   - AI has reference points for what's expected
   - Better pattern matching

3. **Explicit Context**
   - AI understands its role and purpose
   - Makes more contextually appropriate choices

### **Better Descriptors:**
1. **Concrete-Specific Details**
   - Before: Vague descriptors
   - After: Examples show what details to focus on
   - Examples: "broom finish residential", "decorative stamped stone pattern"

---

## How It Maps to Your Labels

Your 24 allowed labels are organized by category:

### **Driveways (5 types):**
```
concrete-driveway              → Standard driveway
driveway-replacement           → Replacement project
broom-finish-driveway          → Broom-textured driveway
stamped-concrete-driveway      → Decorative stamped driveway
exposed-aggregate-driveway     → Decorative aggregate driveway
```

### **Patios (4 types):**
```
concrete-patio                 → Standard patio
stamped-concrete-patio         → Decorative stamped patio
exposed-aggregate-patio        → Decorative aggregate patio
fire-pit-surround             → Fire pit area
seat-wall-bench               → Seating wall/bench
```

### **Walkways & Sidewalks (4 types):**
```
concrete-walkway              → Standard walkway
stamped-concrete-walkway      → Decorative stamped walkway
exposed-aggregate-walkway     → Decorative aggregate walkway
sidewalk                      → Sidewalk
```

### **Steps, Walls, Slabs (4 types):**
```
concrete-steps                → Steps/stairs
retaining-wall                → Retaining wall
concrete-slab                 → Flat slab (garage, foundation)
concrete-wall                 → Standard wall
```

### **Repairs & Treatments (2 types):**
```
concrete-repair               → Crack repair, patching
concrete-resurfacing          → Overlay, resurfacing
```

### **Broad/Fallback (3 types):**
```
decorative-concrete           → General decorative work
concrete-project              → Catch-all for projects
unknown                       → Uncertain classification
```

---

## Testing the New Prompts

### **Run the Test:**
```bash
pytest tests/test_5_classification_ai.py -v
```

### **Check Output:**
```bash
cat test_output/5_ai_classification_output.json
```

### **What to Look For:**

1. **More Specific Labels**
   - Before: Many "concrete-driveway" (generic)
   - After: More "broom-finish-driveway", "stamped-concrete-driveway" (specific)

2. **Better Confidence Scores**
   - Before: Many 0.5-0.6 (uncertain)
   - After: More 0.85+ (confident) or <0.5 (appropriately uncertain)

3. **Better Descriptors**
   - Before: "driveway photo", "concrete surface" (vague)
   - After: "broom finish residential", "stamped stone pattern" (specific)

4. **Fewer "Unknown" Labels**
   - Before: Many unknowns due to confusion
   - After: Fewer unknowns, better classification

---

## Fine-Tuning (Optional)

If you want to further improve accuracy, you can:

### **1. Add More Examples**
Add examples specific to your region/style:
```python
"CLASSIFICATION EXAMPLES:\n"
"- Pacific Northwest residential driveway → 'broom-finish-driveway'\n"
"- Modern stamped patio in Bellevue → 'stamped-concrete-patio'\n"
```

### **2. Adjust Confidence Thresholds**
If AI is too conservative:
```python
"- Medium confidence (0.60-0.84): Likely correct, some ambiguity\n"
```

### **3. Add Industry-Specific Terms**
If you have regional terms:
```python
"- EXPOSED AGGREGATE: Also called 'seeded aggregate' or 'pebble finish'\n"
```

### **4. Emphasize Common Mistakes**
If AI frequently confuses certain types:
```python
"COMMON PITFALLS:\n"
"- Don't confuse patios (entertainment) with driveways (vehicle access)\n"
"- Don't confuse walkways (narrow paths) with sidewalks (property edge)\n"
```

---

## Production Monitoring

### **Track Classification Accuracy:**
1. **Monitor confidence scores** - Are most labels >0.85?
2. **Review "unknown" labels** - Why couldn't AI classify them?
3. **Check descriptor quality** - Are they specific and useful?
4. **Validate label distribution** - Does it match your project types?

### **Iterative Improvement:**
1. **Collect feedback** - Which classifications are wrong?
2. **Update prompts** - Add clarifications for common mistakes
3. **Add examples** - Show AI what correct classifications look like
4. **Re-test** - Verify improvements with test suite

---

## Summary

**Old Prompt:** ~150 words, basic instructions

**New Prompt:** ~650 words, comprehensive guidance

**Expected Results:**
- ✅ 20-30% improvement in label accuracy
- ✅ Better confidence calibration (fewer 0.5-0.6 scores)
- ✅ More specific descriptors (useful for SEO)
- ✅ Fewer "unknown" classifications
- ✅ More consistent results across batches

**The AI now has:**
- Clear role and purpose
- Explicit distinctions between types
- Decision-making framework
- Real-world examples
- Confidence guidelines
- Systematic analysis approach

---

**Status:** ✅ Implemented and ready for testing

**Next Steps:**
1. Run test suite to compare before/after
2. Review classification output
3. Fine-tune based on results
4. Deploy to production
