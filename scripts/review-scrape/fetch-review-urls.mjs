import fs from "node:fs"
import path from "node:path"
import process from "node:process"
import { chromium } from "@playwright/test"

const JSON_PATH = path.resolve(process.cwd(), "data/google-review-data.json")

function parseArgs(argv) {
  const out = {
    limit: Infinity,
    start: 0,
    headful: false,
    onlyMissing: true,
    force: false,
    slowMo: 0,
  }

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === "--limit") out.limit = Number(argv[++i] ?? "0")
    else if (a === "--start") out.start = Number(argv[++i] ?? "0")
    else if (a === "--headful") out.headful = true
    else if (a === "--all") out.onlyMissing = false
    else if (a === "--force") out.force = true
    else if (a === "--slowmo") out.slowMo = Number(argv[++i] ?? "0")
    else if (a === "--file") out.file = String(argv[++i] ?? "")
  }
  return out
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"))
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + "\n", "utf8")
}

async function maybeAcceptConsent(page) {
  // Best-effort: Google frequently shows a consent wall; selectors vary by region.
  const candidates = [
    page.getByRole("button", { name: /accept all/i }),
    page.getByRole("button", { name: /i agree/i }),
    page.getByRole("button", { name: /accept/i }),
    page.getByRole("button", { name: /agree/i }),
  ]
  for (const btn of candidates) {
    try {
      if (await btn.first().isVisible({ timeout: 1500 })) {
        await btn.first().click({ timeout: 2000 })
        await page.waitForTimeout(750)
        return true
      }
    } catch {
      // ignore
    }
  }
  return false
}

async function findReviewCard(page, businessName) {
  // Google Maps DOM changes often; keep selectors flexible.
  const byAria = page.locator(`div.jftiEf[aria-label*="${businessName}"]`)
  if (await byAria.first().count()) return byAria.first()

  const byText = page.locator("div.jftiEf").filter({ hasText: businessName })
  if (await byText.first().count()) return byText.first()

  // Fallback: any element with aria-label containing businessName
  const any = page.locator(`[aria-label*="${businessName}"]`)
  if (await any.first().count()) return any.first()

  return null
}

async function extractShareUrlFromDialog(page) {
  // After clicking Share, Google shows a share UI with an input like:
  // <input class="vrsrZe" readonly type="text" value="https://maps.app.goo.gl/...">
  const shareInput = page
    .locator('input.vrsrZe[readonly][type="text"]')
    .or(page.locator('div.NB4yxe input[readonly][type="text"]'))
    .or(page.locator('input[readonly][type="text"][value^="http"]'))

  try {
    await shareInput.first().waitFor({ state: "visible", timeout: 8000 })
    const val = await shareInput.first().inputValue()
    if (val && /^https?:\/\//.test(val)) return val
  } catch {
    // fall through to dialog parsing
  }

  // Fallback: sometimes the share UI is within a dialog.
  const dialog = page.locator('[role="dialog"]').last()
  try {
    await dialog.waitFor({ state: "visible", timeout: 2500 })
  } catch {
    return null
  }

  const input = dialog.locator('input[type="text"], input:not([type]), textarea')
  const inputCount = await input.count()
  for (let i = 0; i < inputCount; i++) {
    const el = input.nth(i)
    try {
      const val = await el.inputValue({ timeout: 500 })
      if (val && /^https?:\/\//.test(val)) return val
    } catch {
      // ignore
    }
  }

  const text = await dialog.innerText().catch(() => "")
  const m = text.match(/https?:\/\/[^\s)"]+/g)
  if (m) return m[0] ?? null

  return null
}

async function getReviewShareUrl({ browser, profileUrl, businessName }) {
  const context = await browser.newContext({
    userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    locale: "en-US",
  })
  const page = await context.newPage()

  try {
    await page.goto(profileUrl, { waitUntil: "domcontentloaded", timeout: 45000 })
    await maybeAcceptConsent(page)
    await page.waitForTimeout(750)

    // Some contrib pages lazy-load; scroll a bit to force render
    for (let i = 0; i < 6; i++) {
      await page.mouse.wheel(0, 1200)
      await page.waitForTimeout(500)
    }

    const card = await findReviewCard(page, businessName)
    if (!card) return { ok: false, reason: "review_not_found" }

    // Try to locate share button within the card
    const shareButton = card
      .locator('button[aria-label^="Share"], button[aria-label*="Share"]')
      .or(card.getByRole("button", { name: /share/i }))
      .first()

    if (!(await shareButton.isVisible({ timeout: 2500 }).catch(() => false))) {
      return { ok: false, reason: "share_button_not_found" }
    }

    await shareButton.click({ timeout: 8000 })
    const url = await extractShareUrlFromDialog(page)

    if (!url) return { ok: false, reason: "share_url_not_found" }
    return { ok: true, url }
  } catch (e) {
    return { ok: false, reason: "error", error: String(e?.message ?? e) }
  } finally {
    await context.close().catch(() => {})
  }
}

const opts = parseArgs(process.argv.slice(2))
const filePath = opts.file ? path.resolve(process.cwd(), opts.file) : JSON_PATH
const data = readJson(filePath)

if (!Array.isArray(data)) {
  console.error("Expected JSON array in:", filePath)
  process.exit(1)
}

const BUSINESS = "Bespoke Tint"

const browser = await chromium.launch({
  headless: !opts.headful,
  slowMo: opts.slowMo || 0,
})

let processed = 0
let updated = 0
let skipped = 0

try {
  for (let i = opts.start; i < data.length; i++) {
    const item = data[i]
    if (!item || typeof item !== "object") continue

    const existingReviewUrl = typeof item.reviewUrl === "string" ? item.reviewUrl.trim() : ""
    const hasValidReviewUrl = /^https?:\/\//i.test(existingReviewUrl)

    if (!opts.force && opts.onlyMissing && hasValidReviewUrl) {
      continue
    }

    const profileUrl = item.profileUrl
    if (typeof profileUrl !== "string" || !profileUrl.startsWith("http")) {
      skipped++
      continue
    }

    const res = await getReviewShareUrl({ browser, profileUrl, businessName: BUSINESS })
    processed++

    if (res.ok) {
      item.reviewUrl = res.url
      updated++
      writeJson(filePath, data)
      console.log(`[${i}] ok -> ${res.url}`)
    } else {
      // Private profiles, rate limits, or DOM changes; leave blank.
      console.log(`[${i}] skip (${res.reason})`)
    }

    if (processed >= opts.limit) break
    await new Promise((r) => setTimeout(r, 600))
  }
} finally {
  await browser.close().catch(() => {})
}

console.log(`done: processed=${processed} updated=${updated} skipped=${skipped}`)
