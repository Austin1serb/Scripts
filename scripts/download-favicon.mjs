import { writeFile } from "node:fs/promises";

const TARGET_URL = "https://www.angi.com";
const OUTPUT_FILE = "favicon.png";

if (TARGET_URL === "https://example.com") {
	throw new Error("Set TARGET_URL in this file before running it.");
}

const faviconUrl = `https://www.google.com/s2/favicons?sz=256&domain_url=${encodeURIComponent(TARGET_URL)}`;

const response = await fetch(faviconUrl);

if (!response.ok) {
	throw new Error(`Failed to download favicon: ${response.status} ${response.statusText}`);
}

await writeFile(new URL(`./${OUTPUT_FILE}`, import.meta.url), Buffer.from(await response.arrayBuffer()));

console.log(`Saved ${OUTPUT_FILE} for ${TARGET_URL}`);
