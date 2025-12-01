const KG_ENDPOINT = "https://kgsearch.googleapis.com/v1/entities:search"

if (!process.env.GOOGLE_KG_API_KEY) {
  throw new Error("GOOGLE_KG_API_KEY is not set")
}

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

const entities = await searchKg(
  "Elon Musk",
    process.env.GOOGLE_KG_API_KEY!,
    50,
   
  )
  console.log(entities)

// // usage:
// const entitiesID = await getKgById(
//   "/g/11vf3xhd8w",
//   process.env.GOOGLE_KG_API_KEY!
// )

// console.log(entitiesID)
