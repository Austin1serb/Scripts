#!/usr/bin/env node

import fs from "fs"
import path from "path"

/**
 * Script to remove data-start={***} and data-end={***} attributes from MDX files
 * Usage: node scripts/remove-data-attributes.mjs <file-path>
 * Example: node scripts/remove-data-attributes.mjs blog/posts/paint-protection-film-ppf-washington.mdx
 */

function removeDataAttributes(content) {
  // Remove data-start={number} attributes
  content = content.replace(/\s*data-start=\{\d+\}/g, "")

  // Remove data-end={number} attributes
  content = content.replace(/\s*data-end=\{\d+\}/g, "")

  return content
}

function processFile(filePath) {
  try {
    // Read the file
    const content = fs.readFileSync(filePath, "utf8")

    // Remove data attributes
    const cleanedContent = removeDataAttributes(content)

    // Check if any changes were made
    if (content === cleanedContent) {
      console.log(`No data attributes found in: ${filePath}`)
      return
    }

    // Write the cleaned content back to the file
    fs.writeFileSync(filePath, cleanedContent, "utf8")

    console.log(`✅ Successfully removed data attributes from: ${filePath}`)

    // Count how many attributes were removed
    const startMatches = content.match(/data-start=\{\d+\}/g) || []
    const endMatches = content.match(/data-end=\{\d+\}/g) || []
    const totalRemoved = startMatches.length + endMatches.length

    console.log(`   Removed ${totalRemoved} data attributes (${startMatches.length} data-start, ${endMatches.length} data-end)`)
  } catch (error) {
    console.error(`❌ Error processing file: ${filePath}`)
    console.error(error.message)
    process.exit(1)
  }
}

function main() {
  const args = process.argv.slice(2)

  if (args.length === 0) {
    console.log("Usage: node scripts/remove-data-attributes.mjs <file-path>")
    console.log("Example: node scripts/remove-data-attributes.mjs blog/posts/paint-protection-film-ppf-washington.mdx")
    process.exit(1)
  }

  const filePath = args[0]

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    console.error(`❌ File not found: ${filePath}`)
    process.exit(1)
  }

  // Check if it's an MDX file
  if (!filePath.endsWith(".mdx") && !filePath.endsWith(".md")) {
    console.warn(`⚠️  Warning: ${filePath} is not an MDX/MD file. Continuing anyway...`)
  }

  console.log(`Processing: ${filePath}`)
  processFile(filePath)
}

main()
