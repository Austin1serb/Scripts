// scripts/unused-exports.mjs - Find exported functions/components that are unused
import { readFile } from "node:fs/promises"
import fastGlob from "fast-glob"

console.log("🔍 Scanning for unused exports...")

// Get all source files
const files = await fastGlob(["**/*.{js,jsx,ts,tsx}", "!**/node_modules/**", "!**/.next/**", "!**/dist/**"], { gitignore: true })

console.log(`📁 Found ${files.length} files to analyze`)

// Map to store all exports: filename -> Set of export names
const exports = new Map()
// Map to store all imports: Set of imported names
const imports = new Set()
// Map to store file dependencies for context
const fileDependencies = new Map()

// Regex patterns for finding exports and imports
const exportPatterns = [
  // export function/const/let/var/class
  /export\s+(?:async\s+)?(?:function|const|let|var|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)/g,
  // export { name1, name2 }
  /export\s*\{\s*([^}]+)\s*\}/g,
  // export default
  /export\s+default\s+(?:(?:async\s+)?(?:function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)|([A-Za-z_$][A-Za-z0-9_$]*))/g,
  // export const Component = () => {}
  /export\s+const\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=\s*(?:\([^)]*\)\s*=>|\([^)]*\)\s*:\s*[^=]+\s*=>)/g,
]

const importPatterns = [
  // import { name1, name2 } from 'module'
  /import\s*\{\s*([^}]+)\s*\}\s*from\s*["']([^"']+)["']/g,
  // import name from 'module'
  /import\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*from\s*["']([^"']+)["']/g,
  // import * as name from 'module'
  /import\s*\*\s*as\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*from\s*["']([^"']+)["']/g,
  // dynamic imports
  /import\s*\(\s*["']([^"']+)["']\s*\)/g,
]

// Usage patterns (beyond imports)
const usagePatterns = [
  // JSX components <ComponentName
  /<([A-Z][A-Za-z0-9_$]*)/g,
  // Function calls in code
  /\b([A-Za-z_$][A-Za-z0-9_$]*)\s*\(/g,
  // Property access
  /\.([A-Za-z_$][A-Za-z0-9_$]*)/g,
  // Object destructuring
  /\{\s*([A-Za-z_$][A-Za-z0-9_$]*(?:\s*,\s*[A-Za-z_$][A-Za-z0-9_$]*)*)\s*\}/g,
]

// Step 1: Extract all exports
for (const file of files) {
  const content = await readFile(file, "utf8")
  const fileExports = new Set()

  for (const pattern of exportPatterns) {
    let match
    while ((match = pattern.exec(content))) {
      if (match[1]) {
        // Handle single export
        const exportName = match[1].trim()
        if (exportName && exportName !== "default") {
          fileExports.add(exportName)
        }
      } else if (match[0].includes("{")) {
        // Handle export { name1, name2 }
        const exportList = match[1]
        const names = exportList
          .split(",")
          .map((name) => name.trim().split(" as ")[0].trim())
          .filter(Boolean)
        names.forEach((name) => {
          if (name !== "default") {
            fileExports.add(name)
          }
        })
      }
    }
  }

  // Handle default exports separately
  const defaultExportMatch = content.match(/export\s+default\s+([A-Za-z_$][A-Za-z0-9_$]*)/)
  if (defaultExportMatch) {
    fileExports.add("default")
  }

  if (fileExports.size > 0) {
    exports.set(file, fileExports)
  }
}

console.log(`📤 Found exports in ${exports.size} files`)

// Step 2: Extract all imports and usage
for (const file of files) {
  const content = await readFile(file, "utf8")
  const fileDeps = new Set()

  // Find imports
  for (const pattern of importPatterns) {
    let match
    while ((match = pattern.exec(content))) {
      if (pattern.source.includes("\\{")) {
        // Named imports
        const importList = match[1]
        const names = importList
          .split(",")
          .map((name) => name.trim().split(" as ").pop().trim())
          .filter(Boolean)
        names.forEach((name) => {
          imports.add(name)
          fileDeps.add(name)
        })
      } else if (match[1]) {
        // Default or namespace imports
        const importName = match[1].trim()
        imports.add(importName)
        fileDeps.add(importName)
      }
    }
  }

  // Find general usage patterns (function calls, JSX components, etc.)
  for (const pattern of usagePatterns) {
    let match
    while ((match = pattern.exec(content))) {
      const name = match[1]
      if (name && /^[A-Z]/.test(name)) {
        // Likely a component
        imports.add(name)
        fileDeps.add(name)
      } else if (name && name.length > 1) {
        // Likely a function or variable
        imports.add(name)
        fileDeps.add(name)
      }
    }
  }

  fileDependencies.set(file, fileDeps)
}

console.log(`📥 Found ${imports.size} unique imported/used identifiers`)

// Step 3: Find unused exports
const unusedExports = []

for (const [file, fileExports] of exports) {
  for (const exportName of fileExports) {
    if (!imports.has(exportName)) {
      // Special case: ignore some common patterns that might be used externally
      const shouldIgnore = [
        exportName === "default" && file.includes("page."), // Next.js pages
        file.includes("layout."), // Next.js layouts
        file.includes(".config."), // Config files
        file.includes("/api/"), // API routes
        exportName.toLowerCase().includes("config"),
        exportName.toLowerCase().includes("metadata"),
        exportName === "generateStaticParams",
        exportName === "generateMetadata",
      ].some(Boolean)

      if (!shouldIgnore) {
        unusedExports.push({
          file,
          exportName,
          isDefault: exportName === "default",
        })
      }
    }
  }
}

// Sort by file for better readability
unusedExports.sort((a, b) => a.file.localeCompare(b.file))

console.log(`\n🗑️  Unused exports found (${unusedExports.length} total):\n`)

// Group by file (always create this for later use)
const groupedByFile = unusedExports.reduce((acc, item) => {
  if (!acc[item.file]) acc[item.file] = []
  acc[item.file].push(item)
  return acc
}, {})

if (unusedExports.length === 0) {
  console.log("✨ No unused exports found! Your codebase is clean.")
} else {
  for (const [file, unused] of Object.entries(groupedByFile)) {
    console.log(`📄 ${file}`)
    unused.forEach(({ exportName, isDefault }) => {
      if (isDefault) {
        console.log(`  ❌ default export`)
      } else {
        console.log(`  ❌ ${exportName}`)
      }
    })
    console.log()
  }
}

// Show statistics
const totalExports = [...exports.values()].reduce((sum, set) => sum + set.size, 0)
console.log(`📊 Statistics:`)
console.log(`- Total exports: ${totalExports}`)
console.log(`- Unused exports: ${unusedExports.length}`)
console.log(`- Usage rate: ${(((totalExports - unusedExports.length) / totalExports) * 100).toFixed(1)}%`)

// Show files with most unused exports
const fileStats = Object.entries(groupedByFile)
  .map(([file, unused]) => ({ file, count: unused.length }))
  .sort((a, b) => b.count - a.count)
  .slice(0, 5)

if (fileStats.length > 0) {
  console.log(`\n🔥 Files with most unused exports:`)
  fileStats.forEach(({ file, count }) => {
    console.log(`  ${file}: ${count} unused exports`)
  })
}
