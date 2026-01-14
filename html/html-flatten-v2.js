// Toggle which attributes are preserved when options.keepAttributes === true
const KEEP_ATTRIBUTES = new Set(['id']);

function flattenDOM(options = {}) {
  const { keepAttributes = false, root = document.body } = options;

  const SEMANTIC_OWNERS = new Set([
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'p', 'blockquote', 'pre', 'code',
    'a', 'button', 'label',
    'li',
    'figcaption', 'caption',
    'time', 'abbr', 'cite', 'q', 'mark', 'address',
  ]);

  const GROUPING_ELEMENTS = new Set([
    'nav', 'header', 'main', 'section', 'article', 'aside', 'footer',
    'ul', 'ol', 'figure',
  ]);

  const SKIP_ELEMENTS = new Set([
    'script', 'style', 'noscript', 'template', 'iframe',
    'head', 'meta', 'link', 'title',
  ]);

  const PLACEHOLDER_ELEMENTS = new Set(['form', 'table', 'details', 'dl']);

  const STYLING_ELEMENTS = new Set([
    'span', 'strong', 'em', 'b', 'i', 'u', 's',
    'small', 'sub', 'sup', 'mark', 'del', 'ins', 'br', 'wbr',
  ]);

  function normalizeWhitespace(text) {
    return text.replace(/\s+/g, ' ').trim();
  }

  function getTagName(el) {
    return el?.tagName?.toLowerCase?.() || '';
  }

  function isSemanticOwner(el) {
    return SEMANTIC_OWNERS.has(getTagName(el));
  }

  function isGrouping(el) {
    return GROUPING_ELEMENTS.has(getTagName(el));
  }

  function shouldSkip(el) {
    return SKIP_ELEMENTS.has(getTagName(el));
  }

  function isPlaceholder(el) {
    return PLACEHOLDER_ELEMENTS.has(getTagName(el));
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function escapeAttr(text) {
    return String(text ?? '')
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function buildAttrString(el, extraAttrs = {}) {
    if (!keepAttributes || !el) {
      const keys = Object.keys(extraAttrs);
      if (!keys.length) return '';
      return (
        ' ' +
        keys
          .map((k) => `${k}="${escapeAttr(extraAttrs[k])}"`)
          .join(' ')
      );
    }

    const attrs = {};

    // First: preserved attrs from DOM element
    for (const attr of KEEP_ATTRIBUTES) {
      if (el.hasAttribute?.(attr)) {
        const v = el.getAttribute(attr);
        if (v !== null) attrs[attr] = v;
      }
    }

    // Second: explicit attrs from emitter (e.g., img alt)
    for (const [k, v] of Object.entries(extraAttrs)) {
      attrs[k] = v;
    }

    const keys = Object.keys(attrs);
    if (!keys.length) return '';
    return (
      ' ' +
      keys
        .map((k) => `${k}="${escapeAttr(attrs[k])}"`)
        .join(' ')
    );
  }

  // Step 1: atoms
  function extractAtoms(r) {
    const atoms = [];

    function walk(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const t = normalizeWhitespace(node.textContent || '');
        if (t) atoms.push({ type: 'text', content: t, node });
        return;
      }

      if (node.nodeType !== Node.ELEMENT_NODE) return;
      const tag = getTagName(node);

      if (shouldSkip(node)) return;

      if (tag === 'svg') {
        atoms.push({ type: 'svg', node });
        return;
      }

      if (tag === 'img') {
        const alt = node.getAttribute('alt');
        if (alt !== null) atoms.push({ type: 'img', alt, node });
        return;
      }

      if (isPlaceholder(node)) {
        atoms.push({ type: 'placeholder', tag, node });
        return;
      }

      for (const child of node.childNodes) walk(child);
    }

    walk(r);
    return atoms;
  }

  // Step 2: blocks
  function findSemanticOwner(node) {
    let current = node.parentElement;
    while (current) {
      if (isSemanticOwner(current)) return current;
      if (isGrouping(current)) return null;
      current = current.parentElement;
    }
    return null;
  }

  function findSmallestContainer(node) {
    let current = node.parentElement;
    while (current && current !== document.body) {
      const tag = getTagName(current);
      if (STYLING_ELEMENTS.has(tag)) {
        current = current.parentElement;
        continue;
      }
      return current;
    }
    return document.body;
  }

  function buildBlocks(atoms) {
    const blockMap = new Map(); // semantic owner -> block
    const orphanMap = new Map(); // container -> orphan block

    function ensureSemantic(owner) {
      if (!blockMap.has(owner)) {
        blockMap.set(owner, { type: 'semantic', tag: getTagName(owner), owner, contents: [] });
      }
      return blockMap.get(owner);
    }

    function ensureOrphan(container) {
      if (!orphanMap.has(container)) {
        const tag = getTagName(container);
        orphanMap.set(container, {
          type: 'orphan',
          tag: (tag === 'div' || tag === 'span' || !tag) ? 'div' : tag,
          owner: container,
          contents: [],
        });
      }
      return orphanMap.get(container);
    }

    for (const atom of atoms) {
      if (atom.type === 'placeholder') {
        orphanMap.set(atom.node, { type: 'placeholder', tag: atom.tag, owner: atom.node });
        continue;
      }

      if (atom.type === 'svg') {
        const owner = findSemanticOwner(atom.node);
        if (owner) ensureSemantic(owner).contents.push({ type: 'svg' });
        else ensureOrphan(findSmallestContainer(atom.node)).contents.push({ type: 'svg' });
        continue;
      }

      if (atom.type === 'img') {
        const owner = findSemanticOwner(atom.node);
        if (owner) ensureSemantic(owner).contents.push({ type: 'img', alt: atom.alt, el: atom.node });
        else orphanMap.set(Symbol('img'), { type: 'orphan-img', tag: 'img', alt: atom.alt, owner: atom.node });
        continue;
      }

      // text
      const owner = findSemanticOwner(atom.node);
      if (owner) ensureSemantic(owner).contents.push({ type: 'text', content: atom.content });
      else ensureOrphan(findSmallestContainer(atom.node)).contents.push({ type: 'text', content: atom.content });
    }

    const blocks = [...blockMap.values(), ...orphanMap.values()];

    for (const b of blocks) {
      if (!b.contents) continue;
      b.mergedText = normalizeWhitespace(
        b.contents
          .filter((c) => c.type === 'text')
          .map((c) => c.content)
          .join(' ')
      );
      b.hasSvg = b.contents.some((c) => c.type === 'svg');
      b.images = b.contents.filter((c) => c.type === 'img');
    }

    return blocks.filter((b) => {
      if (b.type === 'placeholder' || b.type === 'orphan-img') return true;
      return b.mergedText || b.hasSvg || (b.images && b.images.length > 0);
    });
  }

  // Step 3: groups
  function findGroupingAncestor(el) {
    let current = el?.parentElement;
    while (current) {
      if (isGrouping(current)) return current;
      current = current.parentElement;
    }
    return null;
  }

  function buildGroups(blocks) {
    const groupMap = new Map(); // element -> group
    const rootBlocks = [];

    for (const block of blocks) {
      const g = findGroupingAncestor(block.owner);
      if (!g) {
        rootBlocks.push(block);
        continue;
      }

      if (!groupMap.has(g)) {
        groupMap.set(g, {
          element: g,
          tag: getTagName(g),
          children: [],
          parentGroup: findGroupingAncestor(g),
        });
      }
      groupMap.get(g).children.push(block);
    }

    const rootGroups = [];
    for (const [, group] of groupMap) {
      if (group.parentGroup && groupMap.has(group.parentGroup)) {
        const parent = groupMap.get(group.parentGroup);
        if (!parent.nestedGroups) parent.nestedGroups = [];
        parent.nestedGroups.push(group);
      } else {
        rootGroups.push(group);
      }
    }

    return { rootGroups, rootBlocks };
  }

  // order
  const docOrderCache = new WeakMap();
  function getDocOrder(el) {
    if (!el) return 0;
    if (docOrderCache.has(el)) return docOrderCache.get(el);
    const all = document.body.getElementsByTagName('*');
    for (let i = 0; i < all.length; i++) {
      if (!docOrderCache.has(all[i])) docOrderCache.set(all[i], i);
    }
    return docOrderCache.get(el) || 0;
  }

  // Step 4: emit
  function emitBlock(block, indent = '') {
    if (block.type === 'placeholder') {
      const attrs = buildAttrString(block.owner);
      return `${indent}<${block.tag}${attrs}/>`;
    }

    if (block.type === 'orphan-img') {
      const attrs = buildAttrString(block.owner, { alt: block.alt || '' });
      return `${indent}<img${attrs}/>`;
    }

    const parts = [];
    if (block.hasSvg) parts.push('<svg/>');

    if (block.images) {
      for (const img of block.images) {
        const attrs = buildAttrString(img.el, { alt: img.alt || '' });
        parts.push(`<img${attrs}/>`);
      }
    }

    if (block.mergedText) parts.push(escapeHtml(block.mergedText));

    const content = parts.join(' ');
    if (!content) return '';

    const attrs = buildAttrString(block.owner);
    return `${indent}<${block.tag}${attrs}>${content}</${block.tag}>`;
  }

  function emitGroup(group, indent = '') {
    const attrs = buildAttrString(group.element);
    const lines = [`${indent}<${group.tag}${attrs}>`];

    const allItems = [];
    for (const child of group.children) {
      allItems.push({ type: 'block', data: child, order: getDocOrder(child.owner) });
    }
    if (group.nestedGroups) {
      for (const nested of group.nestedGroups) {
        allItems.push({ type: 'group', data: nested, order: getDocOrder(nested.element) });
      }
    }

    allItems.sort((a, b) => a.order - b.order);

    for (const item of allItems) {
      if (item.type === 'block') {
        const out = emitBlock(item.data, indent + '  ');
        if (out) lines.push(out);
      } else {
        lines.push(emitGroup(item.data, indent + '  '));
      }
    }

    lines.push(`${indent}</${group.tag}>`);
    return lines.join('\n');
  }

  const atoms = extractAtoms(root);
  const blocks = buildBlocks(atoms);
  const { rootGroups, rootBlocks } = buildGroups(blocks);

  const allRootItems = [];
  for (const b of rootBlocks) allRootItems.push({ type: 'block', data: b, order: getDocOrder(b.owner) });
  for (const g of rootGroups) allRootItems.push({ type: 'group', data: g, order: getDocOrder(g.element) });
  allRootItems.sort((a, b) => a.order - b.order);

  const out = [];
  for (const item of allRootItems) {
    if (item.type === 'block') {
      const s = emitBlock(item.data);
      if (s) out.push(s);
    } else {
      out.push(emitGroup(item.data));
    }
  }

  return out.join('\n');
}

// Backwards-compatible default execution if you just paste the file contents:
try {
  const result = flattenDOM();
  // eslint-disable-next-line no-console
  console.log(result);
  result;
} catch (e) {
  // eslint-disable-next-line no-console
  console.error(e);
}
