#!/usr/bin/env -S node --no-warnings
// scripts/generate-md.ts
import fs from "node:fs/promises"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { ALL_PAGES } from "../config/site"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, "..")
const PUBLIC_DIR = path.join(ROOT, "public")

// ========== CONFIGURATION ==========
// Set to true to crawl live production site, false to use localhost
const CRAWL_LIVE_SITE = false

// Where to fetch pages from during generation
const GEN_BASE = CRAWL_LIVE_SITE ? "https://www.bespokeauto.org" : "http://localhost:3000"

// Production URL to use in generated markdown files (always use production URL in output)
const PRODUCTION_URL = "https://www.bespokeauto.org"

// Pages to skip during generation (e.g., pages with Cloudflare Turnstile or other client-side dependencies)
// Note: Only needed when CRAWL_LIVE_SITE = true
const SKIP_PAGES = CRAWL_LIVE_SITE ? ["/contact"] : []
// 1) Normalize: drop #anchors, dedupe, trim trailing slashes (except "/")
const SLUGS = Array.from(
  new Set(
    ALL_PAGES.map((s) => (s || "/").split("#")[0]) // drop anchors
      .map((s) => s || "/") // keep trailing slash as-is
      .filter((s) => !SKIP_PAGES.includes(s)) // skip problematic pages
  )
)
function outPathFor(slug: string) {
  if (slug === "/") return path.join(PUBLIC_DIR, "index.html.md")
  console.log("PUBLIC_DIR: ", PUBLIC_DIR)

  // remove leading slash so path.join doesn’t reset to root
  const rel = slug.replace(/^\/+/, "") // "gallery/page/1" or "blog" or "blog/"

  // Directory flavor when slug ends with "/"
  if (slug.endsWith("/")) {
    return path.join(PUBLIC_DIR, rel, "index.html.md")
  }

  // default file flavor
  return path.join(PUBLIC_DIR, rel + ".md")
}
function encodeForRoute(slug: string) {
  if (slug === "/") return ""
  // Encode each segment for the catch-all param
  return slug.split("/").filter(Boolean).map(encodeURIComponent).join("/")
}

async function fetchMD(slug: string) {
  const encoded = encodeForRoute(slug) // "" or "gallery/page/1"
  const url = `${GEN_BASE}/api/markdown/${encoded}?productionUrl=${encodeURIComponent(PRODUCTION_URL)}` // root will be .../api/markdown/
  console.log("GEN_BASE: ", GEN_BASE)
  const res = await fetch(url, { headers: { "user-agent": "generate-md" } })
  if (!res.ok) throw new Error(`Fetch failed ${res.status} ${url}`)
  return res.text()
}

async function main() {
  console.log(`Generating .md twins for ${SLUGS.length} routes via ${GEN_BASE} …`)
  for (const slug of SLUGS) {
    try {
      const md = await fetchMD(slug)
      const out = outPathFor(slug)
      await fs.mkdir(path.dirname(out), { recursive: true })
      await fs.writeFile(out, md, "utf8")
      console.log(`✓ ${slug}  →  ${path.relative(ROOT, out)}`)
    } catch (error) {
      console.error(`✗ ${slug}  →  FAILED:`, error instanceof Error ? error.message : error)
      // Continue with next slug instead of failing completely
    }
  }
}
main().catch((e) => {
  console.error(e)
  process.exit(1)
})
