(() => {
  // SEMANTIC DOM FLATTENER
  // Converts HTML into minimal, token-efficient text for LLM consumption.
  //
  // Pipeline:
  //   1. Collect text nodes + non-text elements (images, inputs, icon buttons)
  //   2. Find semantic owner for each, with absorption rules
  //   3. Build region tree (landmarks + lists)
  //   4. Serialize in DOM order

  // --- Constants ---

  const IGNORED = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "SVG", "PATH"]);
  const REGIONS = new Set(["NAV", "HEADER", "MAIN", "SECTION", "ARTICLE", "FOOTER", "ASIDE", "OL", "UL"]);
  const SEMANTIC = new Set(["H1", "H2", "H3", "H4", "H5", "H6", "P", "A", "BUTTON", "LABEL", "ADDRESS", "LI"]);
  const PROMOTABLE = new Set(["DIV", "SPAN"]);
  const BLOCK = new Set(["P", "H1", "H2", "H3", "H4", "H5", "H6"]);
  const INLINE = new Set(["A", "BUTTON"]);
  const LISTS = new Set(["UL", "OL"]);

  // LI children: semantic tags (minus LI) + SPAN for step numbers
  const LI_KIDS = new Set([...SEMANTIC].filter((t) => t !== "LI").concat("SPAN"));

  const IMPLICIT_MAIN = Symbol("implicit-main");

  // --- Helpers ---

  const clean = (s) => String(s || "").replace(/\s+/g, " ").trim();

  const cmpDOM = (a, b) => {
    if (a === b) return 0;
    return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
  };

  const sortDOM = (arr, fn) => arr.sort((a, b) => cmpDOM(fn(a), fn(b)));

  function ancestor(el, tags) {
    while (el) {
      if (el.nodeType === 1 && tags.has(el.tagName)) return el;
      el = el.parentElement;
    }
    return null;
  }

  function hasBetween(child, parent, tags) {
    let el = child.parentElement;
    while (el && el !== parent) {
      if (tags.has(el.tagName)) return true;
      el = el.parentElement;
    }
    return false;
  }

  // --- Stage 1: Collect Elements ---

  function collectText(root) {
    const nodes = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      if (n.parentElement && clean(n.textContent) && !ancestor(n.parentElement, IGNORED)) {
        nodes.push(n);
      }
    }
    return nodes;
  }

  function collectNonText(root) {
    const out = [];

    root.querySelectorAll("img[alt]").forEach((el) => {
      const alt = clean(el.getAttribute("alt"));
      if (alt && !ancestor(el, IGNORED)) out.push({ el, tag: "IMG", alt });
    });

    root.querySelectorAll("input[title], input[placeholder]").forEach((el) => {
      if (ancestor(el, IGNORED)) return;
      const title = clean(el.getAttribute("title") || el.getAttribute("placeholder"));
      if (title) out.push({ el, tag: "INPUT", title, type: el.getAttribute("type") || "text" });
    });

    root.querySelectorAll("button[aria-label], a[aria-label]").forEach((el) => {
      if (ancestor(el, IGNORED) || clean(el.textContent)) return;
      const label = clean(el.getAttribute("aria-label"));
      if (label) out.push({ el, tag: el.tagName, ariaLabel: label });
    });

    return out;
  }

  // --- Stage 2: Find Owners & Build Units ---

  function findOwner(textNode) {
    const parent = textNode.parentElement;
    if (!parent) return null;

    let owner = ancestor(parent, SEMANTIC);
    if (owner) {
      // LI absorbs its semantic children
      if (owner.tagName !== "LI") {
        const li = ancestor(owner.parentElement, new Set(["LI"]));
        if (li) return li;
      }
      // Block tags absorb inline children
      if (INLINE.has(owner.tagName)) {
        const block = ancestor(owner.parentElement, BLOCK);
        if (block) return block;
      }
      return owner;
    }

    // Fallback: promotable container
    let el = parent;
    while (el) {
      if (IGNORED.has(el.tagName)) return null;
      if (PROMOTABLE.has(el.tagName)) return el;
      el = el.parentElement;
    }
    return null;
  }

  function buildUnits(textNodes, nonText) {
    const map = new Map();

    for (const n of textNodes) {
      const owner = findOwner(n);
      if (owner && !map.has(owner)) map.set(owner, { el: owner, tag: owner.tagName });
    }

    for (const item of nonText) {
      if (!map.has(item.el)) map.set(item.el, item);
    }

    const units = sortDOM([...map.values()], (u) => u.el);

    // Filter absorbed units
    return units.filter((u) =>
      !units.some((o) => {
        if (o === u || !o.el.contains(u.el)) return false;
        // LI absorbs children unless there's a list between
        if (o.tag === "LI") return !hasBetween(u.el, o.el, LISTS);
        // Block absorbs inline
        if (BLOCK.has(o.tag) && INLINE.has(u.tag)) return true;
        return false;
      })
    );
  }

  // --- Stage 3: Build Region Tree ---

  function buildRegions(units) {
    const map = new Map();
    const roots = [];

    function getRegion(el, implicit = false) {
      if (map.has(el)) return map.get(el);
      const node = { el, tag: implicit ? "MAIN" : el.tagName, implicit, children: [], units: [] };
      map.set(el, node);
      return node;
    }

    function ensureChain(el) {
      const node = getRegion(el);
      const parentEl = ancestor(el.parentElement, REGIONS);
      if (!parentEl) {
        if (!roots.includes(node)) roots.push(node);
        return node;
      }
      const parent = ensureChain(parentEl);
      if (!parent.children.includes(node)) parent.children.push(node);
      return node;
    }

    let implicitMain = null;

    for (const u of units) {
      const region = ancestor(u.el, REGIONS);
      if (region) {
        ensureChain(region).units.push(u);
      } else {
        if (!implicitMain) {
          implicitMain = getRegion(IMPLICIT_MAIN, true);
          roots.push(implicitMain);
        }
        implicitMain.units.push(u);
      }
    }

    // Sort
    function sortRegion(r) {
      r.children = sortDOM(r.children.filter((c) => !c.implicit), (c) => c.el);
      r.units = sortDOM(r.units, (u) => u.el);
      r.children.forEach(sortRegion);
    }
    roots.sort((a, b) => (a.implicit ? 1 : b.implicit ? -1 : cmpDOM(a.el, b.el)));
    roots.forEach(sortRegion);

    return roots;
  }

  // --- Stage 4: Serialize ---

  function serializeInlines(el) {
    let out = "";
    for (const c of el.childNodes) {
      if (c.nodeType === Node.TEXT_NODE) {
        out += c.textContent;
      } else if (c.nodeType === Node.ELEMENT_NODE) {
        if (INLINE.has(c.tagName)) {
          const t = clean(c.textContent);
          if (t) out += `<${c.tagName.toLowerCase()}>${t}</${c.tagName.toLowerCase()}>`;
        } else {
          out += serializeInlines(c);
        }
      }
    }
    return clean(out);
  }

  function getTextExcluding(el, exclude) {
    let out = "";
    for (const c of el.childNodes) {
      if (c.nodeType === Node.TEXT_NODE) {
        out += c.textContent;
      } else if (c.nodeType === Node.ELEMENT_NODE && !exclude.has(c.tagName)) {
        out += getTextExcluding(c, exclude);
      }
    }
    return clean(out);
  }

  function serializeLI(el) {
    const kids = sortDOM(
      [...el.querySelectorAll([...LI_KIDS].join(","))].filter(
        (k) => !hasBetween(k, el, LI_KIDS) && !hasBetween(k, el, LISTS)
      ),
      (k) => k
    );

    if (kids.length) {
      const lines = kids
        .map((k) => {
          const t = clean(k.textContent);
          return t ? `  <${k.tagName.toLowerCase()}>${t}</${k.tagName.toLowerCase()}>` : null;
        })
        .filter(Boolean);
      if (lines.length) return `<li>\n${lines.join("\n")}\n</li>`;
    }

    const text = getTextExcluding(el, LISTS);
    return text ? `<li>${text}</li>` : null;
  }

  function serializeUnit(u) {
    const { el, tag } = u;
    const t = tag.toLowerCase();

    if (tag === "IMG") return `<img alt="${u.alt}"/>`;
    if (tag === "INPUT") return `<input title="${u.title}" type="${u.type}"/>`;
    if (u.ariaLabel) return `<${t} aria-label="${u.ariaLabel}"/>`;
    if (tag === "LI") return serializeLI(el);
    if (BLOCK.has(tag)) return serializeInlines(el) ? `<${t}>${serializeInlines(el)}</${t}>` : null;

    const text = clean(el.textContent);
    return text ? `<${t}>${text}</${t}>` : null;
  }

  function serializeRegion(r) {
    const items = [
      ...r.children.map((c) => ({ type: "r", data: c, el: c.el })),
      ...r.units.map((u) => ({ type: "u", data: u, el: u.el })),
    ];

    items.sort((a, b) =>
      a.el === IMPLICIT_MAIN ? 1 : b.el === IMPLICIT_MAIN ? -1 : cmpDOM(a.el, b.el)
    );

    const pieces = items
      .map((i) => (i.type === "r" ? serializeRegion(i.data) : serializeUnit(i.data)))
      .filter(Boolean);

    if (!pieces.length) return null;

    const body = pieces.map((p) => "  " + p.replace(/\n/g, "\n  ")).join("\n\n");
    return `<${r.tag.toLowerCase()}>\n${body}\n</${r.tag.toLowerCase()}>`;
  }

  // --- Entry ---

  function flatten(root) {
    const text = collectText(root);
    const nonText = collectNonText(root);
    const units = buildUnits(text, nonText);
    const regions = buildRegions(units);
    return regions.map(serializeRegion).filter(Boolean).join("\n\n");
  }

  if (typeof window !== "undefined") window.__flattenDOM = flatten;

  const result = flatten(document.body);
  console.log(result);
  return result;
})();
