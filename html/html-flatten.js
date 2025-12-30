(() => {
  // SEMANTIC DOM FLATTENER
  // Converts arbitrary HTML into a minimal, token-efficient representation
  // that preserves all human-meaningful distinctions for LLM reasoning.
  //
  // Pipeline:
  //   1. Collect visible text nodes
  //   2. Find semantic owner for each text node
  //   3. Deduplicate owners (children of expanding tags handled by parent)
  //   4. Build region tree (landmarks + lists)
  //   5. Serialize in DOM order

  // --- Constants 

  const IGNORED_TAGS = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "SVG", "PATH"]);

  const SEMANTIC_TAGS = new Set([
    "H1", "H2", "H3", "H4", "H5", "H6",
    "P", "A", "BUTTON", "LABEL", "ADDRESS", "LI",
  ]);

  const REGION_TAGS = new Set([
    "NAV", "HEADER", "MAIN", "SECTION", "ARTICLE", "FOOTER", "ASIDE",
    "OL", "UL", // lists act as regions for structure
  ]);

  const PROMOTABLE_TAGS = new Set(["DIV", "SPAN"]);

  const IMPLICIT_MAIN = Symbol("implicit-main");

  // Cached set for LI child expansion (SEMANTIC_TAGS minus LI, plus SPAN)
  const LI_CHILD_TAGS = new Set([...SEMANTIC_TAGS].filter((t) => t !== "LI").concat("SPAN"));

  // --- Utilities 

  function cleanText(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function compareDOM(a, b) {
    if (a === b) return 0;
    const pos = a.compareDocumentPosition(b);
    return pos & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
  }

  function sortByDOM(arr, getEl) {
    return arr.sort((a, b) => compareDOM(getEl(a), getEl(b)));
  }

  function findAncestor(el, tagSet) {
    while (el) {
      if (el.nodeType === 1 && tagSet.has(el.tagName)) return el;
      el = el.parentElement;
    }
    return null;
  }

  function hasAncestorIn(el, tagSet) {
    return !!findAncestor(el, tagSet);
  }

  // --- Stage 1: Collect Visible Text Nodes -----------------------------------

  function collectTextNodes(root) {
    const nodes = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent || !cleanText(node.textContent)) continue;
      if (hasAncestorIn(parent, IGNORED_TAGS)) continue;
      nodes.push(node);
    }
    return nodes;
  }

  // Collect non-text semantic elements: images, inputs, icon-only buttons/links
  function collectNonTextElements(root) {
    const elements = [];

    // Images with alt text
    root.querySelectorAll("img[alt]").forEach((img) => {
      const alt = cleanText(img.getAttribute("alt"));
      if (alt && !hasAncestorIn(img, IGNORED_TAGS)) {
        elements.push({ el: img, tag: "IMG", alt });
      }
    });

    // Inputs with title or placeholder
    root.querySelectorAll("input[title], input[placeholder]").forEach((input) => {
      if (hasAncestorIn(input, IGNORED_TAGS)) return;
      const title = cleanText(input.getAttribute("title") || input.getAttribute("placeholder"));
      const type = input.getAttribute("type") || "text";
      if (title) {
        elements.push({ el: input, tag: "INPUT", title, type });
      }
    });

    // Buttons and links with aria-label but no visible text
    root.querySelectorAll("button[aria-label], a[aria-label]").forEach((el) => {
      if (hasAncestorIn(el, IGNORED_TAGS)) return;
      // Check if it has no meaningful text content (icon-only)
      if (cleanText(el.textContent)) return; // has text, will be handled normally
      const ariaLabel = cleanText(el.getAttribute("aria-label"));
      if (ariaLabel) {
        elements.push({ el, tag: el.tagName, ariaLabel });
      }
    });

    return elements;
  }

  // --- Stage 2: Find Semantic Owners -----------------------------------------

  function findOwner(textNode) {
    const parent = textNode.parentElement;
    if (!parent) return null;

    // First priority: any semantic ancestor (even if there's a SPAN/DIV in between)
    let semanticOwner = findAncestor(parent, SEMANTIC_TAGS);
    if (semanticOwner) {
      // LI absorbs all its semantic children (so LI always becomes the unit, not its children)
      if (semanticOwner.tagName !== "LI") {
        const containingLi = findAncestor(semanticOwner.parentElement, new Set(["LI"]));
        if (containingLi) semanticOwner = containingLi;
      }
      return semanticOwner;
    }

    // Fallback: nearest promotable container (SPAN/DIV) when no semantic owner exists
    let current = parent;
    while (current) {
      if (IGNORED_TAGS.has(current.tagName)) return null;
      if (PROMOTABLE_TAGS.has(current.tagName)) return current;
      current = current.parentElement;
    }
    return null;
  }

  // --- Stage 3: Build Semantic Units -----------------------------------------

  function buildUnits(textNodes, nonTextElements) {
    const ownerMap = new Map();

    // Units from text nodes
    for (const node of textNodes) {
      const owner = findOwner(node);
      if (owner && !ownerMap.has(owner)) {
        ownerMap.set(owner, { el: owner, tag: owner.tagName });
      }
    }

    // Add non-text elements (images, inputs, icon buttons)
    for (const item of nonTextElements) {
      if (!ownerMap.has(item.el)) {
        ownerMap.set(item.el, item);
      }
    }

    const units = sortByDOM(Array.from(ownerMap.values()), (u) => u.el);

    // Remove units nested inside LI (LI serializes its children inline)
    // But don't filter if there's a list (UL/OL) between them (nested list case)
    return units.filter((unit) =>
      !units.some((other) => {
        if (other === unit || other.tag !== "LI" || !other.el.contains(unit.el)) return false;
        // Check if there's a list between the containing LI and this unit
        let el = unit.el.parentElement;
        while (el && el !== other.el) {
          if (el.tagName === "UL" || el.tagName === "OL") return false; // nested list, don't filter
          el = el.parentElement;
        }
        return true;
      })
    );
  }

  // --- Stage 4: Build Region Tree --------------------------------------------

  function buildRegions(units) {
    const regionMap = new Map();
    const roots = [];

    function getRegion(el, isImplicit = false) {
      if (regionMap.has(el)) return regionMap.get(el);
      const node = {
        el,
        tag: isImplicit ? "MAIN" : el.tagName,
        isImplicit,
        children: [],
        units: [],
      };
      regionMap.set(el, node);
      return node;
    }

    function ensureChain(el) {
      const node = getRegion(el);
      const parentEl = findAncestor(el.parentElement, REGION_TAGS);

      if (!parentEl) {
        if (!roots.includes(node)) roots.push(node);
        return node;
      }

      const parent = ensureChain(parentEl);
      if (!parent.children.includes(node)) parent.children.push(node);
      return node;
    }

    let implicitMain = null;

    for (const unit of units) {
      const regionEl = findAncestor(unit.el, REGION_TAGS);
      if (regionEl) {
        ensureChain(regionEl).units.push(unit);
      } else {
        implicitMain ??= (roots.push(getRegion(IMPLICIT_MAIN, true)), roots[roots.length - 1]);
        implicitMain.units.push(unit);
      }
    }

    // Sort all regions and units by DOM order (implicit last)
    function sortRegion(r) {
      r.children = sortByDOM(r.children.filter((c) => !c.isImplicit), (c) => c.el);
      r.units = sortByDOM(r.units, (u) => u.el);
      r.children.forEach(sortRegion);
    }
    roots.sort((a, b) => {
      if (a.isImplicit) return 1;
      if (b.isImplicit) return -1;
      return compareDOM(a.el, b.el);
    });
    roots.forEach(sortRegion);

    return roots;
  }

  // --- Stage 5: Serialize ----------------------------------------------------

  function getTopDescendants(container, tagSet) {
    const selector = [...tagSet].join(",");
    // Get matching descendants, but exclude those nested under another match
    return sortByDOM(
      [...container.querySelectorAll(selector)].filter((el) => {
        let parent = el.parentElement;
        while (parent && parent !== container) {
          if (tagSet.has(parent.tagName)) return false; // nested under another match
          parent = parent.parentElement;
        }
        return true;
      }),
      (el) => el
    );
  }

  // Get text content excluding nested lists (UL/OL)
  function getDirectText(el) {
    let text = "";
    for (const child of el.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) {
        text += child.textContent;
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        if (child.tagName !== "UL" && child.tagName !== "OL") {
          text += getDirectText(child);
        }
      }
    }
    return cleanText(text);
  }

  function serializeUnit(unit) {
    const { el, tag } = unit;
    const tagLower = tag.toLowerCase();

    // Image with alt text
    if (tag === "IMG") {
      return `<img alt="${unit.alt}"/>`;
    }

    // Input with title/placeholder and type
    if (tag === "INPUT") {
      return `<input title="${unit.title}" type="${unit.type}"/>`;
    }

    // Button/link with aria-label (icon-only)
    if (unit.ariaLabel) {
      return `<${tagLower} aria-label="${unit.ariaLabel}"/>`;
    }

    // LI expansion
    if (tag === "LI") {
      // Get semantic children, but exclude anything inside nested lists
      const kids = getTopDescendants(el, LI_CHILD_TAGS).filter((k) => {
        let parent = k.parentElement;
        while (parent && parent !== el) {
          if (parent.tagName === "UL" || parent.tagName === "OL") return false;
          parent = parent.parentElement;
        }
        return true;
      });

      if (kids.length) {
        const lines = kids
          .map((k) => {
            const t = cleanText(k.textContent);
            return t ? `  <${k.tagName.toLowerCase()}>${t}</${k.tagName.toLowerCase()}>` : null;
          })
          .filter(Boolean);
        if (lines.length) return `<li>\n${lines.join("\n")}\n</li>`;
      }

      // Fallback: get direct text content (excluding nested lists)
      const text = getDirectText(el);
      return text ? `<li>${text}</li>` : null;
    }

    // Default: flatten text
    const text = cleanText(el.textContent);
    return text ? `<${tagLower}>${text}</${tagLower}>` : null;
  }

  function serializeRegion(region) {
    const items = [
      ...region.children.map((r) => ({ type: "r", data: r, el: r.el })),
      ...region.units.map((u) => ({ type: "u", data: u, el: u.el })),
    ];

    if (items.some((i) => i.el === IMPLICIT_MAIN)) {
      items.sort((a, b) => (a.el === IMPLICIT_MAIN ? 1 : b.el === IMPLICIT_MAIN ? -1 : compareDOM(a.el, b.el)));
    } else {
      sortByDOM(items, (i) => i.el);
    }

    const pieces = items
      .map((i) => (i.type === "r" ? serializeRegion(i.data) : serializeUnit(i.data)))
      .filter(Boolean);

    if (!pieces.length) return null;

    const tag = region.tag.toLowerCase();
    const body = pieces.map((p) => "  " + p.replace(/\n/g, "\n  ")).join("\n\n");
    return `<${tag}>\n${body}\n</${tag}>`;
  }

  // --- Entry Point -----------------------------------------------------------

  function flatten(root) {
    const textNodes = collectTextNodes(root);
    const nonTextElements = collectNonTextElements(root);
    const units = buildUnits(textNodes, nonTextElements);
    const regions = buildRegions(units);
    return regions.map(serializeRegion).filter(Boolean).join("\n\n");
  }

  // Expose for testing, run if not in test mode
  if (typeof window !== "undefined") {
    window.__flattenDOM = flatten;
  }
  
  const result = flatten(document.body);
  console.log(result);
  return result;
})();
