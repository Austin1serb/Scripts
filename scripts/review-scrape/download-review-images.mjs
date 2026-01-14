import path from "node:path"
import { readJson, writeJson, downloadImageToPublic } from "./review-image-downloader.mjs"

export async function downloadGoogleReviewImages({
  jsonPath = path.resolve(process.cwd(), "data/google-review-data.json"),
  publicRootAbs = path.resolve(process.cwd(), "public"),
  publicSubdir = "google",
} = {}) {
  const data = readJson(jsonPath)
  if (!Array.isArray(data)) throw new Error("google-review-data.json must be an array")

  const cache = new Map()
  let changed = 0

  for (const review of data) {
    if (!review || typeof review !== "object") continue
    const reviewerName = typeof review.reviewer === "string" ? review.reviewer : "unknown"

    // profileImage: string URL
    try {
      const nextProfile = await downloadImageToPublic({
        url: review.profileImage,
        publicRootAbs,
        publicSubdir,
        filenamePrefix: "profile",
        nameHint: reviewerName,
        cache,
      })
      if (nextProfile && review.profileImage !== nextProfile) {
        review.profileImage = nextProfile
        changed++
      }
    } catch {
      // skip
    }

    // images: string[]
    if (Array.isArray(review.images)) {
      for (let idx = 0; idx < review.images.length; idx++) {
        const url = review.images[idx]
        if (typeof url !== "string") continue
        try {
          const next = await downloadImageToPublic({
            url,
            publicRootAbs,
            publicSubdir,
            filenamePrefix: `img-${idx + 1}`,
            nameHint: reviewerName,
            cache,
          })
          if (next && url !== next) {
            review.images[idx] = next
            changed++
          }
        } catch {
          // skip
        }
      }
    }
  }

  if (changed) writeJson(jsonPath, data)
  return { changed, count: data.length, jsonPath, publicSubdir }
}

downloadGoogleReviewImages()
