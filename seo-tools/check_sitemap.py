#!/usr/bin/env python3
import asyncio, aiohttp, gzip, io, csv, sys, re
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

CONCURRENCY = 30
TIMEOUT = aiohttp.ClientTimeout(total=20)
HEADERS = {"User-Agent": "sitemap-auditor/1.0"}


def strip_ns(tag):  # "{ns}tag" -> "tag"
    return re.sub(r"^\{.*\}", "", tag)


async def fetch_bytes(session, url):
    async with session.get(url, headers=HEADERS) as r:
        data = await r.read()
        return r.status, r.headers, data


async def fetch_text_xml(session, url):
    status, headers, data = await fetch_bytes(session, url)
    if url.endswith(".gz") or headers.get("Content-Type", "").startswith(
        "application/x-gzip"
    ):
        data = gzip.decompress(data)
    return status, data.decode("utf-8", errors="ignore")


async def expand_sitemap(session, sitemap_url, seen=None, urls=None):
    if seen is None:
        seen = set()
    if urls is None:
        urls = []
    if sitemap_url in seen:
        return urls
    seen.add(sitemap_url)
    status, text = await fetch_text_xml(session, sitemap_url)
    if status != 200:
        return urls
    root = ET.fromstring(text)
    tag = strip_ns(root.tag).lower()
    if tag == "sitemapindex":
        for sm in root.findall(".//*"):
            if strip_ns(sm.tag).lower() == "loc":
                child = sm.text.strip()
                if child:
                    await expand_sitemap(session, child, seen, urls)
    elif tag == "urlset":
        for url_el in root.findall(".//*"):
            if strip_ns(url_el.tag).lower() == "url":
                loc = url_el.find("./*[{local-name()}='loc']")
                lastmod = url_el.find("./*[{local-name()}='lastmod']")
                if loc is not None and loc.text:
                    urls.append(
                        (
                            loc.text.strip(),
                            (
                                lastmod.text.strip()
                                if lastmod is not None and lastmod.text
                                else ""
                            ),
                        )
                    )
    return urls


async def probe(session, url):
    # Try HEAD first; fall back to GET
    try:
        async with session.head(url, allow_redirects=True, headers=HEADERS) as r:
            return url, r.status, str(r.url)
    except:
        try:
            async with session.get(url, allow_redirects=True, headers=HEADERS) as r:
                return url, r.status, str(r.url)
        except Exception as e:
            return url, "error", repr(e)


async def main(sitemap_url, out_csv="sitemap_report.csv"):
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        url_rows = await expand_sitemap(session, sitemap_url)
        sem = asyncio.Semaphore(CONCURRENCY)

        async def bound(u):
            async with sem:
                return await probe(session, u[0])

        results = await asyncio.gather(*[bound(u) for u in url_rows])
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url", "status", "final_url", "lastmod"])
        for (u, lastmod), (_, status, final_url) in zip(url_rows, results):
            w.writerow([u, status, final_url, lastmod])


if __name__ == "__main__":
    sm = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "sitemap_report.csv"
    asyncio.run(main(sm, out))
