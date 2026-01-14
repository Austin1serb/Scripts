import fs from "node:fs"
import path from "node:path"
import crypto from "node:crypto"

export function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"))
}

export function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n", "utf8")
}

export function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true })
}

export function sha1(input) {
  return crypto.createHash("sha1").update(input).digest("hex")
}

export function slugifyForFilename(input, { maxLen = 48 } = {}) {
  const s = String(input ?? "")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")

  const out = s || "unknown"
  return out.length > maxLen ? out.slice(0, maxLen).replace(/-+$/g, "") : out
}

export function normalizeUrlForId(url) {
  const u = new URL(url)
  u.hash = ""
  u.search = ""
  return u.toString()
}

export function repairDoubleProtocolUrl(url) {
  // Fix bad strings like:
  // "https://scontent.fsea1-1.https://scontent-sea1-1.xx.fbcdn.net/..."
  // by taking the LAST http(s):// occurrence.
  const s = String(url || "").trim()
  const matches = [...s.matchAll(/https?:\/\//gi)]
  if (matches.length >= 2) {
    const lastIdx = matches[matches.length - 1].index
    if (typeof lastIdx === "number") return s.slice(lastIdx)
  }
  return s
}

export function guessExtFromUrl(url) {
  try {
    const u = new URL(url)
    const ext = path.extname(u.pathname)
    if (ext && ext.length <= 6) return ext.toLowerCase()
  } catch {
    // ignore
  }
  return ""
}

export function guessExtFromContentType(contentType) {
  const ct = String(contentType || "").toLowerCase()
  if (ct.includes("image/jpeg")) return ".jpg"
  if (ct.includes("image/jpg")) return ".jpg"
  if (ct.includes("image/png")) return ".png"
  if (ct.includes("image/webp")) return ".webp"
  if (ct.includes("image/gif")) return ".gif"
  return ""
}

export async function fetchWithRetry(url, { retries = 2, timeoutMs = 45000 } = {}) {
  let lastErr
  for (let attempt = 0; attempt <= retries; attempt++) {
    const ac = new AbortController()
    const t = setTimeout(() => ac.abort(), timeoutMs)
    try {
      const res = await fetch(url, { signal: ac.signal, redirect: "follow" })
      clearTimeout(t)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res
    } catch (e) {
      clearTimeout(t)
      lastErr = new Error(`fetch failed for ${url}: ${String(e?.message ?? e)}`)
      await new Promise((r) => setTimeout(r, 800 * (attempt + 1)))
    }
  }
  throw lastErr
}

export async function downloadImageToPublic({ url, publicRootAbs, publicSubdir, filenamePrefix, nameHint, cache }) {
  if (!url || typeof url !== "string") return null
  if (url.startsWith("/")) return url

  url = repairDoubleProtocolUrl(url)

  let normalized
  try {
    normalized = normalizeUrlForId(url)
  } catch {
    return null
  }

  const cached = cache.get(normalized)
  if (cached) return cached

  const dirAbs = path.join(publicRootAbs, publicSubdir)
  ensureDir(dirAbs)

  const extFromUrl = guessExtFromUrl(url)
  const slug = nameHint ? slugifyForFilename(nameHint, { maxLen: 48 }) : ""
  const base = `${filenamePrefix}${slug ? `-${slug}` : ""}-${sha1(normalized).slice(0, 16)}`
  let fileName = base + (extFromUrl || "")
  let fileAbs = path.join(dirAbs, fileName)

  if (!fs.existsSync(fileAbs)) {
    try {
      const res = await fetchWithRetry(url)
      const ct = res.headers.get("content-type")
      const extFromCt = guessExtFromContentType(ct)

      if (!extFromUrl && extFromCt) {
        fileName = base + extFromCt
        fileAbs = path.join(dirAbs, fileName)
      }

      const buf = Buffer.from(await res.arrayBuffer())
      fs.writeFileSync(fileAbs, buf)
    } catch {
      // Don't crash the whole run for one bad/blocked URL.
      return null
    }
  }

  const publicPath = `/${publicSubdir}/${fileName}`.replaceAll("\\\\", "/")
  cache.set(normalized, publicPath)
  return publicPath
}
