// Universal Character Scanner - Works on ANY site
(async function () {
  const characters = new Set();
  const decoder = new TextDecoder();

  console.log('🔍 Starting deep character scan...');

  // 1. Scan ALL current DOM text
  function extractFromNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      [...(node.textContent || '')].forEach(c => characters.add(c));
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Get attributes
      [...node.attributes || []].forEach(attr => {
        [...(attr.value || '')].forEach(c => characters.add(c));
      });
      // Get shadow DOM
      if (node.shadowRoot) {
        extractFromNode(node.shadowRoot);
      }
      // Recurse children
      [...node.childNodes].forEach(child => extractFromNode(child));
    }
  }

  // 2. Extract from ALL scripts (inline and external)
  const allScripts = document.querySelectorAll('script');
  for (const script of allScripts) {
    // Inline scripts
    if (script.textContent) {
      // Extract ALL quoted strings
      const matches = script.textContent.matchAll(/["'`]([^"'`\\]|\\.|\\u[0-9a-fA-F]{4})*["'`]/g);
      for (const match of matches) {
        try {
          // Try to parse as JSON to handle escape sequences
          const cleaned = match[0].slice(1, -1);
          const decoded = JSON.parse('"' + cleaned + '"');
          [...decoded].forEach(c => characters.add(c));
        } catch {
          [...match[0]].forEach(c => characters.add(c));
        }
      }
    }

    // External scripts
    if (script.src && script.src.includes(window.location.hostname)) {
      try {
        const response = await fetch(script.src);
        const text = await response.text();
        // Same string extraction
        const matches = text.matchAll(/["'`]([^"'`\\]|\\.|\\u[0-9a-fA-F]{4})*["'`]/g);
        for (const match of matches) {
          try {
            const cleaned = match[0].slice(1, -1);
            const decoded = JSON.parse('"' + cleaned + '"');
            [...decoded].forEach(c => characters.add(c));
          } catch {
            [...match[0]].forEach(c => characters.add(c));
          }
        }
      } catch (e) {
        console.warn(`Couldn't fetch ${script.src}`);
      }
    }
  }

  // 3. Extract from ALL stylesheets
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules || []) {
        if (rule.cssText) {
          // Get content from ::before, ::after
          const contentMatches = rule.cssText.matchAll(/content:\s*["']([^"']+)["']/g);
          for (const match of contentMatches) {
            [...match[1]].forEach(c => characters.add(c));
          }
        }
      }
    } catch (e) {
      // Cross-origin stylesheets
    }
  }

  // 4. Scan localStorage/sessionStorage
  [localStorage, sessionStorage].forEach(storage => {
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      const value = storage.getItem(key);
      [...(key || '')].forEach(c => characters.add(c));
      [...(value || '')].forEach(c => characters.add(c));
    }
  });

  // 5. Scan ALL window properties for strings
  const scannedObjects = new WeakSet();
  function scanObject(obj, depth = 0) {
    if (depth > 3 || !obj || scannedObjects.has(obj)) return;
    scannedObjects.add(obj);

    try {
      if (typeof obj === 'string') {
        [...obj].forEach(c => characters.add(c));
      } else if (Array.isArray(obj)) {
        obj.forEach(item => scanObject(item, depth + 1));
      } else if (typeof obj === 'object') {
        Object.values(obj).forEach(val => scanObject(val, depth + 1));
      }
    } catch (e) {
      // Ignore errors from accessing restricted properties
    }
  }

  // Scan common global data stores
  ['__NEXT_DATA__', '__nuxt__', '__INITIAL_STATE__', '_app', 'app'].forEach(prop => {
    if (window[prop]) scanObject(window[prop]);
  });

  // Start DOM extraction
  extractFromNode(document);

  // Clean up results
  characters.delete(''); // Remove empty string
  characters.delete('\0'); // Remove null character

  // Results
  const charArray = Array.from(characters).sort();
  const result = {
    total: charArray.length,
    characters: charArray.join(''),
    byCategory: {
      basic: charArray.filter(c => /[a-zA-Z0-9 .,!?;:\-'"]/.test(c)).join(''),
      extended: charArray.filter(c => !/[a-zA-Z0-9 .,!?;:\-'"]/.test(c)).join('')
    }
  };
  const fullResults = { "chars": result.characters }

  console.log(`✅ Found ${result.total} unique characters`);
  console.log('Basic:', result.byCategory.basic);
  console.log('Extended:', result.byCategory.extended);
  console.log('\nFull character set: ', fullResults);

  `!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_\`abcdefghijklmnopqrstuvwxyz{|}~©«®»—’℠─★`
  // Save to window for access
  window.__extractedCharacters = result;

  return result;
})();