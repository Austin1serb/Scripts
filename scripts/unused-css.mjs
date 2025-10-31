// scripts/unused-css.mjs - Find CSS classes that are not being used
import { readFile } from "node:fs/promises"
import fastGlob from "fast-glob"

console.log("🎨 Scanning for unused CSS classes...")

// Get CSS files and source files separately
const cssFiles = await fastGlob(["**/*.{css,scss,sass,less}", "!**/node_modules/**", "!**/.next/**"], { gitignore: true })
const sourceFiles = await fastGlob(["**/*.{js,jsx,ts,tsx,html,vue,svelte}", "!**/node_modules/**", "!**/.next/**"], { gitignore: true })

console.log(`📄 Found ${cssFiles.length} CSS files and ${sourceFiles.length} source files`)

// Extract CSS class definitions
const definedClasses = new Map() // className -> Set of files where it's defined
const usedClasses = new Set() // Set of all used class names

// Patterns to extract CSS class definitions
const cssClassPatterns = [
  // Standard CSS classes: .class-name
  /\.([a-zA-Z_][\w-]*)\s*\{/g,
  // CSS classes with pseudo-selectors: .class-name:hover
  /\.([a-zA-Z_][\w-]*):[\w-]+/g,
  // CSS classes with modifiers: .class-name.modifier
  /\.([a-zA-Z_][\w-]*)\./g,
  // CSS classes in complex selectors: .parent .child
  /\.([a-zA-Z_][\w-]*)\s/g,
]

// Patterns to find class usage in source files
const classUsagePatterns = [
  // className="class-name"
  /class(?:Name)?\s*=\s*["'`]([^"'`]+)["'`]/g,
  // className={`template ${dynamic}`}
  /class(?:Name)?\s*=\s*\{[^}]*?["'`]([^"'`]+)["'`][^}]*?\}/g,
  // clsx/classnames calls
  /(?:clsx|cn|classnames)\s*\([^)]*?["'`]([^"'`]+)["'`][^)]*?\)/g,
  // CSS modules: styles.className
  /styles\.([a-zA-Z_][\w-]*)/g,
  // Direct class references in strings
  /["'`]([^"'`]*\b(?:btn|card|nav|menu|modal|popup|dropdown|tooltip|alert|badge|header|footer|sidebar|container|wrapper|content|main|section|article|aside|form|input|button|link|icon|image|video|audio|table|list|item|row|col|grid|flex|block|inline|hidden|visible|active|disabled|selected|focused|hover|loading|error|success|warning|info|primary|secondary|danger|safe|dark|light|small|large|medium|xs|sm|md|lg|xl|xxl)\b[^"'`]*)["'`]/g,
]

// Step 1: Extract all CSS class definitions
console.log("🔍 Extracting CSS class definitions...")

for (const file of cssFiles) {
  const content = await readFile(file, "utf8")

  // Remove comments to avoid false positives
  const cleanContent = content
    .replace(/\/\*[\s\S]*?\*\//g, "") // Remove /* */ comments
    .replace(/\/\/.*$/gm, "") // Remove // comments

  for (const pattern of cssClassPatterns) {
    let match
    while ((match = pattern.exec(cleanContent))) {
      const className = match[1]
      if (className && className.length > 1) {
        // Skip Tailwind-like utility classes and very generic names
        const isTailwindLike =
          /^(bg-|text-|border-|p-|m-|w-|h-|flex|grid|block|inline|hidden|relative|absolute|fixed|sticky|top-|bottom-|left-|right-|rounded|shadow|opacity-|z-|transition|transform|hover:|focus:|active:|md:|lg:|xl:|sm:)/.test(
            className
          )
        const isGeneric =
          /^(a|p|h[1-6]|div|span|img|ul|ol|li|table|tr|td|th|form|input|button|select|textarea|label|nav|header|footer|main|section|article|aside)$/.test(
            className
          )

        if (!isTailwindLike && !isGeneric) {
          if (!definedClasses.has(className)) {
            definedClasses.set(className, new Set())
          }
          definedClasses.get(className).add(file)
        }
      }
    }
  }
}

console.log(`📝 Found ${definedClasses.size} CSS class definitions`)

// Step 2: Find class usage in source files
console.log("🔍 Finding class usage in source files...")

for (const file of sourceFiles) {
  const content = await readFile(file, "utf8")

  for (const pattern of classUsagePatterns) {
    let match
    while ((match = pattern.exec(content))) {
      const classString = match[1]
      if (classString) {
        // Split by whitespace to get individual classes
        const classes = classString.split(/\s+/).filter(Boolean)
        classes.forEach((cls) => {
          // Clean up class names (remove trailing punctuation, etc.)
          const cleanClass = cls.replace(/[^\w-]/g, "").trim()
          if (cleanClass) {
            usedClasses.add(cleanClass)
          }
        })
      }
    }
  }
}

console.log(`📥 Found ${usedClasses.size} unique class usages`)

// Step 3: Find unused classes
const unusedClasses = []

for (const [className, definedInFiles] of definedClasses) {
  if (!usedClasses.has(className)) {
    unusedClasses.push({
      className,
      definedIn: Array.from(definedInFiles),
    })
  }
}

// Sort by class name for better readability
unusedClasses.sort((a, b) => a.className.localeCompare(b.className))

console.log(`\n🗑️  Unused CSS classes found (${unusedClasses.length} total):\n`)

// Group by file for better organization (always create this for later use)
const groupedByFile = unusedClasses.reduce((acc, item) => {
  item.definedIn.forEach((file) => {
    if (!acc[file]) acc[file] = []
    acc[file].push(item.className)
  })
  return acc
}, {})

if (unusedClasses.length === 0) {
  console.log("✨ No unused CSS classes found! Your styles are clean.")
} else {
  for (const [file, classes] of Object.entries(groupedByFile)) {
    console.log(`📄 ${file}`)
    classes.forEach((className) => {
      console.log(`  ❌ .${className}`)
    })
    console.log()
  }
}

// Show statistics
const totalDefinedClasses = definedClasses.size
console.log(`📊 Statistics:`)
console.log(`- Total CSS classes defined: ${totalDefinedClasses}`)
console.log(`- Unused CSS classes: ${unusedClasses.length}`)
console.log(`- Usage rate: ${totalDefinedClasses > 0 ? (((totalDefinedClasses - unusedClasses.length) / totalDefinedClasses) * 100).toFixed(1) : 0}%`)

// Show most common used class patterns
const usedClassPatterns = Array.from(usedClasses)
  .filter((cls) => definedClasses.has(cls))
  .reduce((acc, cls) => {
    const prefix = cls.split("-")[0]
    acc[prefix] = (acc[prefix] || 0) + 1
    return acc
  }, {})

const topPatterns = Object.entries(usedClassPatterns)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 5)

if (topPatterns.length > 0) {
  console.log(`\n🔥 Most used class prefixes:`)
  topPatterns.forEach(([prefix, count]) => {
    console.log(`  ${prefix}-*: ${count} classes`)
  })
}

// Show files with most unused classes
const fileStats = Object.entries(groupedByFile || {})
  .map(([file, classes]) => ({ file, count: classes.length }))
  .sort((a, b) => b.count - a.count)
  .slice(0, 5)

if (fileStats.length > 0) {
  console.log(`\n📁 Files with most unused classes:`)
  fileStats.forEach(({ file, count }) => {
    console.log(`  ${file}: ${count} unused classes`)
  })
}
