# Semantic DOM Flattener

In one sentence:
> Lossless compression of HTML meaning into a flat, token-efficient format for LLM consumption.

short version: Converts HTML into minimal, token-efficient text for LLM consumption.

long version: Convert arbitrary HTML into the smallest possible text representation that still preserves all human-meaningful content for LLM reasoning.

## What it does

```
Raw HTML → Semantic snapshot
```

**Keeps:** headings, paragraphs, links, buttons, lists, regions, images (alt), inputs (title), aria-labels

**Discards:** styling wrappers, SVG, scripts, styles, duplicate text

## Usage

Run in browser console on any page:

```javascript
// Paste html-flatten.js contents, or:
const result = window.__flattenDOM(document.body);
```

## Output

```html
<nav>
  <h5>Company</h5>
  <ul>
    <li><a>Home</a></li>
    <li><a>About</a></li>
  </ul>
</nav>
```

## Tests

Open `test/test-runner.html` in browser.
