// scripts/tw-usage.mjs - Find Tailwind classes used only once
import { readFile } from "node:fs/promises"
import { execSync } from "node:child_process"
import fastGlob from "fast-glob"

console.log("🔍 Scanning for Tailwind classes...")

// Get all source files
const files = await fastGlob(["**/*.{js,jsx,ts,tsx,mdx,css}", "!**/node_modules/**", "!**/.next/**"], { gitignore: true })

// Extract all potential class candidates from files
const allCandidates = new Set()
const classPatterns = [
  // className attributes and variations
  /class(?:Name)?\s*=\s*["'`]([^"'`]+)["'`]/g,
  /class(?:Name)?\s*=\s*{[^}]*?["'`]([^"'`]+)["'`][^}]*?}/g,
  // clsx, cn, classnames calls
  /(?:clsx|cn|classnames)\s*\([^)]*?["'`]([^"'`]+)["'`][^)]*?\)/g,
  // CSS @apply
  /@apply\s+([^;]+);/g,
  // Any string that looks like it contains CSS classes
  /["'`]([^"'`]*(?:\b(?:flex|grid|bg-|text-|border-|p-|m-|w-|h-|rounded|shadow)\b)[^"'`]*)["'`]/g,
]

for (const file of files) {
  const content = await readFile(file, "utf8")

  for (const pattern of classPatterns) {
    let match
    while ((match = pattern.exec(content))) {
      const classString = match[1]
      // Split by whitespace and filter out empty strings
      const classes = classString.split(/\s+/).filter(Boolean)
      classes.forEach((cls) => allCandidates.add(cls))
    }
  }
}

console.log(`📝 Found ${allCandidates.size} potential class candidates`)

// Use Tailwind CSS to validate which candidates are actual Tailwind classes
console.log("🎨 Validating classes with Tailwind CSS...")

// Create a temporary CSS file with all candidates for Tailwind to process
const candidateList = Array.from(allCandidates)
const tempCSS = `
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Test classes */
.test { @apply ${candidateList.join(" ")}; }
`

// Write temp files
await import("node:fs/promises").then((fs) => fs.writeFile("temp-test.css", tempCSS))
await import("node:fs/promises").then((fs) => fs.writeFile("temp-test.html", `<div class="${candidateList.join(" ")}"></div>`))

let validTailwindClasses = new Set()

try {
  // Try to build CSS with Tailwind - valid classes will be included
  const result = execSync("npx tailwindcss -i temp-test.css -o temp-output.css --content temp-test.html", {
    encoding: "utf8",
    stdio: "pipe",
  })

  // Read the output CSS to see which classes were actually generated
  const outputCSS = await readFile("temp-output.css", "utf8")

  // Extract utility classes that were actually generated
  // This is a simple approach - look for class selectors in the output
  const generatedClasses = outputCSS.match(/\.([a-zA-Z0-9_-]+(?:\\[:\[\]\/\.%])*[a-zA-Z0-9_-]*)/g) || []

  generatedClasses.forEach((cls) => {
    // Remove the leading dot and handle escaped characters
    const cleanClass = cls.slice(1).replace(/\\/g, "")
    if (allCandidates.has(cleanClass)) {
      validTailwindClasses.add(cleanClass)
    }
  })
} catch (error) {
  console.warn("⚠️  Could not validate with Tailwind CSS, falling back to pattern matching")

  // Fallback: use basic pattern matching for common Tailwind patterns
  const tailwindPattern =
    /^(?:[a-z]+:)*(?:(?:bg|text|border|ring|shadow|outline)-|(?:p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb|ml|mr|w|h|min-w|max-w|min-h|max-h|top|right|bottom|left|inset|z|opacity|scale|rotate|translate|skew|gap|space)-|(?:flex|grid|block|inline|hidden|relative|absolute|fixed|sticky|static|overflow|rounded|cursor|select|pointer-events|resize|font|text|leading|tracking|whitespace|break|truncate|list|appearance|outline|transition|duration|ease|delay|animate)(?:-|$))/

  candidateList.forEach((cls) => {
    if (tailwindPattern.test(cls) || ["flex", "grid", "block", "inline", "hidden", "relative", "absolute", "fixed", "sticky", "static"].includes(cls)) {
      validTailwindClasses.add(cls)
    }
  })
}

// Clean up temp files
try {
  await Promise.all([
    import("node:fs/promises").then((fs) => fs.unlink("temp-test.css").catch(() => {})),
    import("node:fs/promises").then((fs) => fs.unlink("temp-test.html").catch(() => {})),
    import("node:fs/promises").then((fs) => fs.unlink("temp-output.css").catch(() => {})),
  ])
} catch {}

console.log(`✅ Validated ${validTailwindClasses.size} Tailwind classes`)

// Now count actual usage of valid Tailwind classes
const counts = new Map()

for (const file of files) {
  const content = await readFile(file, "utf8")

  for (const pattern of classPatterns) {
    let match
    while ((match = pattern.exec(content))) {
      const classString = match[1]
      const classes = classString.split(/\s+/).filter(Boolean)

      for (const cls of classes) {
        if (validTailwindClasses.has(cls)) {
          counts.set(cls, (counts.get(cls) ?? 0) + 1)
        }
      }
    }
  }
}

// Find single-use classes
const singles = [...counts]
  .filter(([, n]) => n === 1)
  .map(([cls]) => cls)
  .sort()

console.log(`\n🎯 One-off Tailwind classes (${singles.length} total):`)
console.log(singles.join("\n"))

// Show statistics
const total = [...counts].reduce((sum, [, count]) => sum + count, 0)
const unique = counts.size

console.log(`\n📊 Statistics:`)
console.log(`- Total class usage: ${total}`)
console.log(`- Unique classes: ${unique}`)
console.log(`- Single-use classes: ${singles.length} (${((singles.length / unique) * 100).toFixed(1)}%)`)

// Show most used classes
const mostUsed = [...counts].sort(([, a], [, b]) => b - a).slice(0, 10)
console.log(`\n🔥 Most used classes:`)
mostUsed.forEach(([cls, count]) => console.log(`  ${cls}: ${count} times`))
