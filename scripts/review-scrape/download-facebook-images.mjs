import path from "node:path"
import { readJson, writeJson, downloadImageToPublic } from "./review-image-downloader.mjs"

export async function downloadFacebookReviewImages({
  jsonPath = path.resolve(process.cwd(), "data/facebook-reviews.json"),
  publicRootAbs = path.resolve(process.cwd(), "public"),
  publicSubdir = "facebook",
} = {}) {
  const data = readJson(jsonPath)
  if (!Array.isArray(data)) throw new Error("facebook-reviews.json must be an array")

  const cache = new Map()
  let changed = 0

  for (const review of data) {
    if (!review || typeof review !== "object") continue
    const reviewerName = typeof review.reviewer === "string" ? review.reviewer : "unknown"

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

    if (Array.isArray(review.images)) {
      for (let idx = 0; idx < review.images.length; idx++) {
        const img = review.images[idx]
        if (!img) continue

        // facebook/yelp: { url, description }
        if (typeof img === "object" && typeof img.url === "string") {
          try {
            const next = await downloadImageToPublic({
              url: img.url,
              publicRootAbs,
              publicSubdir,
              filenamePrefix: `img-${idx + 1}`,
              nameHint: reviewerName,
              cache,
            })
            if (next && img.url !== next) {
              img.url = next
              changed++
            }
          } catch {
            // skip
          }
        }
      }
    }
  }

  if (changed) writeJson(jsonPath, data)
  return { changed, count: data.length, jsonPath, publicSubdir }
}

downloadFacebookReviewImages()
