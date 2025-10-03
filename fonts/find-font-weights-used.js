// Analyze all fonts actually used on the visible page content
const allElements = document.querySelectorAll("body *");
const fontUsage = new Map();

// Helper function to check if an element is actually visible and rendered
function isElementVisible(element) {
	// Skip non-content elements
	const skipTags = ["script", "style", "noscript", "template", "meta", "link", "head", "title"];
	if (skipTags.includes(element.tagName.toLowerCase())) {
		return false;
	}

	const styles = window.getComputedStyle(element);

	// Skip if display: none or visibility: hidden
	if (styles.display === "none" || styles.visibility === "hidden") {
		return false;
	}

	// Skip if opacity is 0
	if (parseFloat(styles.opacity) === 0) {
		return false;
	}

	// Skip if element has no dimensions (width and height both 0)
	const rect = element.getBoundingClientRect();
	if (rect.width === 0 && rect.height === 0) {
		return false;
	}

	// Skip elements that are positioned way off screen
	if (rect.left < -10000 || rect.top < -10000) {
		return false;
	}

	return true;
}

// Helper function to generate a useful CSS selector for an element
function getElementSelector(element) {
	// Get tag name
	let selector = element.tagName.toLowerCase();

	// Add ID if present
	if (element.id) {
		selector += `#${element.id}`;
	}

	// Add classes if present
	if (element.classList.length > 0) {
		selector += "." + Array.from(element.classList).join(".");
	}

	// Add data attributes for more context
	const dataAttrs = Array.from(element.attributes)
		.filter((attr) => attr.name.startsWith("data-"))
		.slice(0, 2) // Limit to first 2 data attributes
		.map((attr) => `[${attr.name}="${attr.value}"]`)
		.join("");

	if (dataAttrs) {
		selector += dataAttrs;
	}

	return selector;
}

// Helper function to get element text content preview
function getElementPreview(element) {
	const text = element.textContent?.trim() || "";
	if (text.length > 50) {
		return text.substring(0, 47) + "...";
	}
	return text || "[no text content]";
}

// Filter to only visible elements
const visibleElements = Array.from(allElements).filter(isElementVisible);

console.log(`📊 Analyzing ${visibleElements.length} visible elements (filtered from ${allElements.length} total elements)`);

visibleElements.forEach((element, index) => {
	const styles = window.getComputedStyle(element);
	const fontFamily = styles.fontFamily.split(",")[0].trim().replace(/['"]/g, ""); // Get first font and remove quotes
	const fontWeight = styles.fontWeight;

	if (!fontUsage.has(fontFamily)) {
		fontUsage.set(fontFamily, {
			weights: new Map(),
			totalCount: 0,
		});
	}

	const fontData = fontUsage.get(fontFamily);
	fontData.totalCount++;

	// Track weight usage with location information
	if (!fontData.weights.has(fontWeight)) {
		fontData.weights.set(fontWeight, {
			count: 0,
			locations: [],
		});
	}

	const weightData = fontData.weights.get(fontWeight);
	weightData.count++;

	// Store location info (limit to first 10 locations per weight to avoid too much data)
	if (weightData.locations.length < 10) {
		weightData.locations.push({
			selector: getElementSelector(element),
			preview: getElementPreview(element),
			elementIndex: index,
		});
	}
});

// Convert to desired format
const results = Array.from(fontUsage.entries())
	.map(([family, data]) => {
		const weights = Array.from(data.weights.keys())
			.map((w) => parseInt(w))
			.sort((a, b) => a - b);

		return {
			"font-family": family,
			weights: weights,
			times: data.totalCount,
			weightData: data.weights, // Keep the full weight data for location info
		};
	})
	.sort((a, b) => b.times - a.times); // Sort by most used

console.log("🎯 FONTS ACTUALLY USED ON VISIBLE PAGE CONTENT:");
results.forEach((font) => {
	console.log(`font-family: ${font["font-family"]}, weights: [${font.weights.join(", ")}], times: ${font.times}`);
});

// Also show detailed weight usage with locations
console.log("\n📍 DETAILED WEIGHT USAGE WITH LOCATIONS:");
results.forEach((font) => {
	console.log(`\n📝 ${font["font-family"]}:`);
	font.weightData.forEach((data, weight) => {
		console.log(`  ⚖️  Weight ${weight}: used ${data.count} times`);

		if (data.locations.length > 0) {
			console.log(`     📍 Found in:`);
			data.locations.forEach((location, idx) => {
				console.log(`       ${idx + 1}. ${location.selector}`);
				if (location.preview && location.preview !== "[no text content]") {
					console.log(`          📄 "${location.preview}"`);
				}
			});

			if (data.count > data.locations.length) {
				const remaining = data.count - data.locations.length;
				console.log(`       ... and ${remaining} more location${remaining > 1 ? "s" : ""}`);
			}
		}
		console.log(""); // Empty line for readability
	});
});

// Helper function to highlight elements using a specific font/weight combination (only visible elements)
function highlightFontUsage(fontFamily, fontWeight = null) {
	// Remove any existing highlights
	document.querySelectorAll(".font-highlight").forEach((el) => {
		el.classList.remove("font-highlight");
		el.style.removeProperty("outline");
		el.style.removeProperty("background-color");
	});

	let count = 0;
	visibleElements.forEach((element) => {
		const styles = window.getComputedStyle(element);
		const elFontFamily = styles.fontFamily.split(",")[0].trim().replace(/['"]/g, "");
		const elFontWeight = styles.fontWeight;

		const familyMatches = elFontFamily === fontFamily;
		const weightMatches = fontWeight === null || elFontWeight === fontWeight.toString();

		if (familyMatches && weightMatches) {
			element.classList.add("font-highlight");
			element.style.outline = "2px solid red";
			element.style.backgroundColor = "rgba(255, 255, 0, 0.3)";
			count++;
		}
	});

	console.log(`🎯 Highlighted ${count} visible elements using font "${fontFamily}"${fontWeight ? ` with weight ${fontWeight}` : ""}`);
	console.log('💡 To remove highlights, run: highlightFontUsage("clear")');
}

// Function to clear all highlights
function clearHighlights() {
	document.querySelectorAll(".font-highlight").forEach((el) => {
		el.classList.remove("font-highlight");
		el.style.removeProperty("outline");
		el.style.removeProperty("background-color");
	});
	console.log("✨ All highlights cleared");
}

// Make functions available globally for easy use in console
window.highlightFontUsage = function (fontFamily, fontWeight = null) {
	if (fontFamily === "clear") {
		clearHighlights();
		return;
	}
	highlightFontUsage(fontFamily, fontWeight);
};

console.log("\n🔍 DEBUGGING TOOLS:");
console.log("To highlight visible elements using a specific font:");
console.log('  highlightFontUsage("HelveticaNowText")');
console.log("To highlight visible elements using a specific font and weight:");
console.log('  highlightFontUsage("HelveticaNowText", 700)');
console.log("To clear all highlights:");
console.log('  highlightFontUsage("clear")');

// // Table view
// console.table(results);
