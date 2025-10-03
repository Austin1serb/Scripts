#!/usr/bin/env python3
import sys
import csv
import gzip
import urllib.request
import urllib.error
from xml.etree import ElementTree as ET
from urllib.parse import urlparse
import re
import time


def strip_ns(tag):
    """Remove namespace from XML tag"""
    return re.sub(r"^\{.*\}", "", tag)


def fetch_sitemap(url):
    """Fetch and parse sitemap content"""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            # Check if it's gzipped
            if url.endswith(".gz") or response.headers.get(
                "Content-Type", ""
            ).startswith("application/x-gzip"):
                data = gzip.decompress(data)
            return data.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return None


def extract_urls_from_sitemap(sitemap_content):
    """Extract URLs from sitemap XML"""
    urls = []
    try:
        root = ET.fromstring(sitemap_content)

        # Look for URL elements in sitemap
        for url_elem in root.findall(
            ".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"
        ):
            loc_elem = url_elem.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            lastmod_elem = url_elem.find(
                "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
            )

            if loc_elem is not None and loc_elem.text:
                url = loc_elem.text.strip()
                lastmod = (
                    lastmod_elem.text.strip()
                    if lastmod_elem is not None and lastmod_elem.text
                    else ""
                )
                urls.append((url, lastmod))

        # Also try without namespace (fallback)
        if not urls:
            for url_elem in root.findall(".//url"):
                loc_elem = url_elem.find("loc")
                lastmod_elem = url_elem.find("lastmod")

                if loc_elem is not None and loc_elem.text:
                    url = loc_elem.text.strip()
                    lastmod = (
                        lastmod_elem.text.strip()
                        if lastmod_elem is not None and lastmod_elem.text
                        else ""
                    )
                    urls.append((url, lastmod))

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    return urls


def check_url_status(url):
    """Check the HTTP status code of a URL"""
    try:
        # Try HEAD request first (faster)
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "sitemap-checker/1.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode(), response.geturl()
    except urllib.error.HTTPError as e:
        return e.code, url
    except urllib.error.URLError:
        # Try GET request if HEAD fails
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "sitemap-checker/1.0")

            with urllib.request.urlopen(req, timeout=10) as response:
                return response.getcode(), response.geturl()
        except urllib.error.HTTPError as e:
            return e.code, url
        except Exception as e:
            return f"Error: {str(e)}", url
    except Exception as e:
        return f"Error: {str(e)}", url


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 simple_sitemap_checker.py <sitemap_url_or_file> [output.csv]"
        )
        print("Example: python3 simple_sitemap_checker.py sitemap.xml")
        print(
            "Example: python3 simple_sitemap_checker.py https://example.com/sitemap.xml"
        )
        sys.exit(1)

    sitemap_input = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "sitemap_status_report.csv"

    # Read sitemap content
    if sitemap_input.startswith("http"):
        print(f"Fetching sitemap from: {sitemap_input}")
        sitemap_content = fetch_sitemap(sitemap_input)
    else:
        print(f"Reading sitemap from file: {sitemap_input}")
        try:
            with open(sitemap_input, "r", encoding="utf-8") as f:
                sitemap_content = f.read()
        except FileNotFoundError:
            print(f"File not found: {sitemap_input}")
            sys.exit(1)

    if not sitemap_content:
        print("Failed to read sitemap content")
        sys.exit(1)

    # Extract URLs
    print("Extracting URLs from sitemap...")
    urls = extract_urls_from_sitemap(sitemap_content)
    print(f"Found {len(urls)} URLs to check")

    if not urls:
        print("No URLs found in sitemap")
        sys.exit(1)

    # Check each URL
    results = []
    for i, (url, lastmod) in enumerate(urls, 1):
        print(f"Checking {i}/{len(urls)}: {url}")
        status_code, final_url = check_url_status(url)
        results.append(
            {
                "url": url,
                "status_code": status_code,
                "final_url": final_url,
                "lastmod": lastmod,
            }
        )
        # Small delay to be respectful
        time.sleep(0.1)

    # Write results to CSV
    print(f"\nWriting results to: {output_file}")
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["url", "status_code", "final_url", "lastmod"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    status_counts = {}
    for result in results:
        status = str(result["status_code"])
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"\nSummary:")
    print(f"Total URLs checked: {len(results)}")
    for status, count in sorted(status_counts.items()):
        print(f"Status {status}: {count} URLs")


if __name__ == "__main__":
    main()
