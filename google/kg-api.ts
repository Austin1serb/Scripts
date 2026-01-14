import { config as dotenvConfig } from "dotenv"
import { join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

dotenvConfig({
  path: join(resolve(fileURLToPath(import.meta.url), ".."), ".env"),
})

const KG_ENDPOINT = "https://kgsearch.googleapis.com/v1/entities:search"

type KgEntity = {
  "@id"?: string
  "@type"?: string[]
  name?: string
  description?: string
  url?: string
  detailedDescription?: {
    articleBody?: string
    url?: string
  }
  sameAs?: string[]
}

export async function searchKg(
  query: string,
  apiKey: string,
  limit = 5,
  types?: string[]
) {
  const params = new URLSearchParams({
    query,
    key: apiKey,
    limit: String(limit),
    indent: "true",
  })

  if (types && types.length > 0) {
    types.forEach((t) => params.append("types", t))
  }

  const res = await fetch(`${KG_ENDPOINT}?${params.toString()}`)

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`KG API error: ${res.status} ${res.statusText} - ${text}`)
  }

  const json = await res.json()

  const items: KgEntity[] =
    json.itemListElement?.map((el: any) => el.result as KgEntity) ?? []

  return items
}

export async function getKgById(id: string, apiKey: string) {
  const params = new URLSearchParams({
    ids: id,
    key: apiKey,
    indent: "true",
  })

  const res = await fetch(`${KG_ENDPOINT}?${params.toString()}`)

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`KG API error: ${res.status} ${res.statusText} - ${text}`)
  }

  const json = await res.json()

  const items: KgEntity[] =
    json.itemListElement?.map((el: any) => el.result as KgEntity) ?? []

  return items
}

async function main() {
  const apiKey = process.env.GOOGLE_KG_API_KEY
  if (!apiKey) throw new Error("GOOGLE_KG_API_KEY is not set")

  const entities = await searchKg("austin serb", apiKey, 50,["Person"])
  console.log(entities)
}

const isMain =
  typeof process.argv[1] === "string" &&
  resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))

if (isMain) {
  main().catch((err) => {
    console.error(err)
    process.exitCode = 1
  })
}

// // usage:
// const entitiesID = await getKgById(
//   "/g/11f9w2sjzj",
//   process.env.GOOGLE_KG_API_KEY!
// )

// console.log(entitiesID)
