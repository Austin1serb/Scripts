// scripts/unused-media.mjs - Find media files that are not being used
import { readFile } from "node:fs/promises"
import fastGlob from "fast-glob"
import { basename, extname, dirname, join } from "node:path"

console.log("🖼️  Scanning for unused media files...")

// Media file extensions to check
const mediaExtensions = [
  // Images
  "jpg",
  "jpeg",
  "png",
  "gif",
  "webp",
  "svg",
  "ico",
  "bmp",
  "tiff",
  "tif",
  "avif",
  // Videos
  "mp4",
  "avi",
  "mov",
  "wmv",
  "flv",
  "webm",
  "mkv",
  "m4v",
  "3gp",
  "ogv",
  // Audio
  "mp3",
  "wav",
  "ogg",
  "m4a",
  "aac",
  "flac",
  "wma",
  "opus",
  // Documents/Fonts (sometimes considered media)
  "pdf",
  "woff",
  "woff2",
  "ttf",
  "otf",
  "eot",
  // Other
  "json",
  "xml",
  "txt",
  "md", // Config/data files that might be imported
]

// Get media files and source files
const mediaFiles = await fastGlob(
  [`**/*.{${mediaExtensions.join(",")}}`, "!**/node_modules/**", "!**/.next/**", "!**/dist/**", "!**/build/**", "!**/coverage/**", "!**/package-lock.json"],
  { gitignore: true }
)

const sourceFiles = await fastGlob(
  ["**/*.{js,jsx,ts,tsx,css,scss,sass,less,html,vue,svelte,mdx}", "!**/node_modules/**", "!**/.next/**", "!**/dist/**", "!**/build/**"],
  { gitignore: true }
)

console.log(`📁 Found ${mediaFiles.length} media files and ${sourceFiles.length} source files`)

// Track used media files
const usedMediaFiles = new Set()
const mediaFileMap = new Map() // filename -> full paths (for files with same name)

// Create a map of media files by their basename for easier matching
for (const file of mediaFiles) {
  const name = basename(file)
  const nameWithoutExt = basename(file, extname(file))

  if (!mediaFileMap.has(name)) {
    mediaFileMap.set(name, [])
  }
  if (!mediaFileMap.has(nameWithoutExt)) {
    mediaFileMap.set(nameWithoutExt, [])
  }

  mediaFileMap.get(name).push(file)
  mediaFileMap.get(nameWithoutExt).push(file)
}

// Patterns to find media file usage
const mediaUsagePatterns = [
  // ES6 imports: import image from './image.png'
  /import\s+[\w$]+\s+from\s*["']([^"']+)["']/g,
  // Dynamic imports: import('./image.png')
  /import\s*\(\s*["']([^"']+)["']\s*\)/g,
  // Require: require('./image.png')
  /require\s*\(\s*["']([^"']+)["']\s*\)/g,
  // Next.js Image src: src="/image.png" or src={image}
  /src\s*=\s*["']([^"']+)["']/g,
  // Background images: url('./image.png')
  /url\s*\(\s*["']?([^"')]+)["']?\s*\)/g,
  // HTML img tags: <img src="image.png"
  /<img[^>]+src\s*=\s*["']([^"']+)["']/g,
  // Video/audio sources: <video src="video.mp4"
  /<(?:video|audio)[^>]+src\s*=\s*["']([^"']+)["']/g,
  // Source tags: <source src="video.mp4"
  /<source[^>]+src\s*=\s*["']([^"']+)["']/g,
  // Href attributes (for downloads, etc.): href="file.pdf"
  /href\s*=\s*["']([^"']+\.[a-zA-Z0-9]+)["']/g,
  // Object property values: img: "/path/image.png"
  /(?:img|image|src|href|url|path|file|asset|photo|video|audio|document|icon|logo|banner|thumbnail|avatar|background|bg)\s*:\s*["']([^"']+)["']/g,
  // Any string that looks like a media file path (more aggressive)
  /["'`]([^"'`]*(?:\/[^"'`\s]*)?\.(?:jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|avif|mp4|avi|mov|wmv|flv|webm|mkv|m4v|3gp|ogv|mp3|wav|ogg|m4a|aac|flac|wma|opus|pdf|woff|woff2|ttf|otf|eot))["'`]/g,
  // Template literal usage: `${baseUrl}/image.png`
  /`[^`]*([^`]*\.(?:jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|avif|mp4|avi|mov|wmv|flv|webm|mkv|m4v|3gp|ogv|mp3|wav|ogg|m4a|aac|flac|wma|opus|pdf|woff|woff2|ttf|otf|eot))[^`]*`/g,
  // String concatenation or interpolation
  /["']([^"']*\.(?:jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|avif|mp4|avi|mov|wmv|flv|webm|mkv|m4v|3gp|ogv|mp3|wav|ogg|m4a|aac|flac|wma|opus|pdf|woff|woff2|ttf|otf|eot))["']/g,
  // Variable assignments that look like file paths
  /=\s*["']([^"']*\.(?:jpg|jpeg|png|gif|webp|svg|ico|bmp|tiff|tif|avif|mp4|avi|mov|wmv|flv|webm|mkv|m4v|3gp|ogv|mp3|wav|ogg|m4a|aac|flac|wma|opus|pdf|woff|woff2|ttf|otf|eot))["']/g,
]

// Function to normalize and resolve file paths
function resolveMediaPath(referencedPath, sourceFile) {
  // Handle absolute paths from public directory
  if (referencedPath.startsWith("/")) {
    const publicPath = `public${referencedPath}`
    if (mediaFiles.includes(publicPath)) {
      return publicPath
    }
  }

  // Handle relative paths
  if (referencedPath.startsWith("./") || referencedPath.startsWith("../")) {
    const sourceDir = dirname(sourceFile)
    const resolvedPath = join(sourceDir, referencedPath).replace(/\\/g, "/")
    if (mediaFiles.includes(resolvedPath)) {
      return resolvedPath
    }
  }

  // Handle bare filenames (look for matches in mediaFileMap)
  const filename = basename(referencedPath)
  const filenameWithoutExt = basename(referencedPath, extname(referencedPath))

  if (mediaFileMap.has(filename)) {
    return mediaFileMap.get(filename)
  }

  if (mediaFileMap.has(filenameWithoutExt)) {
    return mediaFileMap.get(filenameWithoutExt)
  }

  // Direct match
  if (mediaFiles.includes(referencedPath)) {
    return referencedPath
  }

  return null
}

// Scan source files for media usage
console.log("🔍 Scanning for media file usage...")

for (const file of sourceFiles) {
  const content = await readFile(file, "utf8")

  for (const pattern of mediaUsagePatterns) {
    let match
    while ((match = pattern.exec(content))) {
      const referencedPath = match[1]
      if (!referencedPath) continue

      // Skip external URLs
      if (referencedPath.startsWith("http://") || referencedPath.startsWith("https://") || referencedPath.startsWith("//")) {
        continue
      }

      // Skip data URLs
      if (referencedPath.startsWith("data:")) {
        continue
      }

      const resolvedPaths = resolveMediaPath(referencedPath, file)
      if (resolvedPaths) {
        if (Array.isArray(resolvedPaths)) {
          resolvedPaths.forEach((path) => usedMediaFiles.add(path))
        } else {
          usedMediaFiles.add(resolvedPaths)
        }
      }
    }
  }
}

console.log(`📥 Found ${usedMediaFiles.size} used media file references`)

// Find unused media files
const unusedMediaFiles = mediaFiles.filter((file) => !usedMediaFiles.has(file))

// Sort by file type and name
unusedMediaFiles.sort((a, b) => {
  const extA = extname(a).toLowerCase()
  const extB = extname(b).toLowerCase()
  if (extA !== extB) return extA.localeCompare(extB)
  return a.localeCompare(b)
})

console.log(`\n🗑️  Unused media files found (${unusedMediaFiles.length} total):\n`)

if (unusedMediaFiles.length === 0) {
  console.log("✨ No unused media files found! All your assets are being used.")
} else {
  // Group by directory and file type
  const groupedByDir = unusedMediaFiles.reduce((acc, file) => {
    const dir = dirname(file)
    if (!acc[dir]) acc[dir] = []
    acc[dir].push(file)
    return acc
  }, {})

  for (const [dir, files] of Object.entries(groupedByDir)) {
    console.log(`📁 ${dir}/`)
    files.forEach((file) => {
      const name = basename(file)
      const ext = extname(file).toLowerCase()
      const size = getFileTypeIcon(ext)
      console.log(`  ${size} ${name}`)
    })
    console.log()
  }
}

// Helper function to get file type icon
function getFileTypeIcon(ext) {
  const icons = {
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".png": "🖼️",
    ".gif": "🖼️",
    ".webp": "🖼️",
    ".svg": "🖼️",
    ".ico": "🖼️",
    ".mp4": "🎥",
    ".avi": "🎥",
    ".mov": "🎥",
    ".webm": "🎥",
    ".mkv": "🎥",
    ".mp3": "🎵",
    ".wav": "🎵",
    ".ogg": "🎵",
    ".m4a": "🎵",
    ".pdf": "📄",
    ".woff": "🔤",
    ".woff2": "🔤",
    ".ttf": "🔤",
    ".otf": "🔤",
    ".json": "⚙️",
    ".xml": "⚙️",
    ".txt": "📝",
    ".md": "📝",
  }
  return icons[ext] || "📄"
}

// Show statistics
const totalMediaFiles = mediaFiles.length
const usageRate = totalMediaFiles > 0 ? (((totalMediaFiles - unusedMediaFiles.length) / totalMediaFiles) * 100).toFixed(1) : 0

console.log(`📊 Statistics:`)
console.log(`- Total media files: ${totalMediaFiles}`)
console.log(`- Used media files: ${usedMediaFiles.size}`)
console.log(`- Unused media files: ${unusedMediaFiles.length}`)
console.log(`- Usage rate: ${usageRate}%`)

// Show breakdown by file type
const typeBreakdown = unusedMediaFiles.reduce((acc, file) => {
  const ext = extname(file).toLowerCase()
  acc[ext] = (acc[ext] || 0) + 1
  return acc
}, {})

const sortedTypes = Object.entries(typeBreakdown)
  .sort(([, a], [, b]) => b - a)
  .slice(0, 10)

if (sortedTypes.length > 0) {
  console.log(`\n🗂️  Unused files by type:`)
  sortedTypes.forEach(([ext, count]) => {
    const icon = getFileTypeIcon(ext)
    console.log(`  ${icon} ${ext}: ${count} files`)
  })
}

// Show largest directories with unused files
const dirStats = Object.entries(groupedByDir || {})
  .map(([dir, files]) => ({ dir, count: files.length }))
  .sort((a, b) => b.count - a.count)
  .slice(0, 5)

if (dirStats.length > 0) {
  console.log(`\n📁 Directories with most unused files:`)
  dirStats.forEach(({ dir, count }) => {
    console.log(`  ${dir}: ${count} unused files`)
  })
}

// Estimate potential savings
const estimatedSavings = unusedMediaFiles.length * 50 // Rough estimate of 50KB average per file
if (estimatedSavings > 1024) {
  console.log(`\n💾 Estimated space savings: ~${(estimatedSavings / 1024).toFixed(1)}MB`)
} else if (estimatedSavings > 0) {
  console.log(`\n💾 Estimated space savings: ~${estimatedSavings}KB`)
}
