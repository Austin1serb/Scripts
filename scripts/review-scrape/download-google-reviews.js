(async function scrapeSearchReviews() {
	function sleep(ms) {
		return new Promise((resolve) => setTimeout(resolve, ms));
	}

	function parseRelativeDate(dateStr) {
		const date = new Date();
		const lowerStr = (dateStr || "").toLowerCase().trim();

		if (!lowerStr.includes("ago")) {
			return date.toISOString().split("T")[0];
		}

		let num = 1;
		const numMatch = lowerStr.match(/\d+/);
		if (numMatch) num = parseInt(numMatch[0], 10);

		if (lowerStr.includes("day")) {
			date.setDate(date.getDate() - num);
		} else if (lowerStr.includes("week")) {
			date.setDate(date.getDate() - num * 7);
		} else if (lowerStr.includes("month")) {
			date.setMonth(date.getMonth() - num);
		} else if (lowerStr.includes("year")) {
			date.setFullYear(date.getFullYear() - num);
		}

		return date.toISOString().split("T")[0];
	}

	function getReviewContent(article) {
		function cleanTextFromElement(el) {
			if (!el) return "";

			const clone = el.cloneNode(true);

			clone.querySelectorAll("br").forEach((br) => {
				br.replaceWith("\n");
			});

			const text = (clone.textContent || "")
				.replace(/\bView full review\b/i, "")
				.replace(/\s+\.\.\.\s*$/, "")
				.replace(/\n\s*\n\s*\n+/g, "\n\n")
				.replace(/[ \t]+\n/g, "\n")
				.replace(/\n[ \t]+/g, "\n")
				.replace(/[ \t]{2,}/g, " ")
				.trim();

			return text;
		}

		// 1. Expanded full review
		const fullEl = article.querySelector('div[jsname="PBWx0c"]');
		const fullText = cleanTextFromElement(fullEl);
		if (fullText) return fullText;

		// 2. Truncated review
		const shortEl = article.querySelector('div[jsname="lvvS4b"]');
		const shortText = cleanTextFromElement(shortEl);
		if (shortText) return shortText;

		// 3. Plain review block variant, common when owner response exists
		const directTextCandidates = Array.from(article.querySelectorAll("#TBiyHc .gyKkFe.JhRJje.Fv38Af, span#TBiyHc div.gyKkFe.JhRJje.Fv38Af"))
			.map((el) => cleanTextFromElement(el))
			.filter(Boolean)
			.filter((text) => !/^owner$/i.test(text))
			.filter((text) => !/^reply$/i.test(text));

		if (directTextCandidates.length) {
			return directTextCandidates.sort((a, b) => b.length - a.length)[0];
		}

		return "";
	}

	function expandAllReviews() {
		const buttons = Array.from(document.querySelectorAll('a[aria-label*="View full review"], a[jsname="ix0Hvc"], div[role="button"], span[role="button"]'));

		const expanders = buttons.filter((el) => {
			const text = (el.innerText || el.textContent || "").trim().toLowerCase();
			const aria = (el.getAttribute("aria-label") || "").toLowerCase();
			return text.includes("view full review") || aria.includes("view full review") || text === "more";
		});

		expanders.forEach((btn) => {
			try {
				btn.click();
			} catch (_) {}
		});
	}

	console.log("Expanding long reviews...");
	expandAllReviews();
	await sleep(1200);

	const reviewArticles = Array.from(document.querySelectorAll("article.VaHEVc"));
	const reviews = [];

	reviewArticles.forEach((article) => {
		// Reviewer name + profile
		const nameEl = article.querySelector(".N0c6q a.PskQHd") || article.querySelector('a[aria-label*="Link to reviewer profile"]') || article.querySelector("a");

		const reviewer = nameEl?.innerText?.trim() || "Anonymous";
		const profileUrl = nameEl?.href || "";

		// Profile image
		const profileImgEl = article.querySelector('img.ooGZkf, img[src*="googleusercontent.com/a/"]');
		const profileImage = profileImgEl?.src || "";

		// Rating
		const starEl = article.querySelector('span[role="img"][aria-label*="out of 5 stars"]');
		const ratingMatch = starEl?.getAttribute("aria-label")?.match(/\d+(\.\d+)?/);
		const rating = ratingMatch ? parseFloat(ratingMatch[0]) : 0;

		// Date
		const rawDateStr = article.querySelector(".KEfuhb")?.textContent?.trim() || "";
		const date = parseRelativeDate(rawDateStr);

		// Content
		const content = getReviewContent(article);

		// Review images
		const images = [];
		const seenImageUrls = new Set();

		article.querySelectorAll("img.T3g1hc, img.IOhUcc").forEach((img) => {
			const src = img.currentSrc || img.src || "";
			if (!src) return;

			// Skip profile avatar images
			if (src.includes("googleusercontent.com/a/")) return;
			if (seenImageUrls.has(src)) return;

			seenImageUrls.add(src);
			images.push({
				url: src,
				description: img.alt?.trim() || "Review photo",
			});
		});

		// Skip clearly broken items
		if (!reviewer && !content) return;

		reviews.push({
			reviewer,
			profileUrl,
			profileImage,
			rating,
			date,
			content,
			images,
			reviewPlatform: "google",
		});
	});

	console.log(`Successfully scraped ${reviews.length} reviews.`);
	console.log(reviews);

	const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reviews, null, 2));

	const downloadAnchorNode = document.createElement("a");
	downloadAnchorNode.setAttribute("href", dataStr);
	downloadAnchorNode.setAttribute("download", "Google_Search_reviews.json");
	document.body.appendChild(downloadAnchorNode);
	downloadAnchorNode.click();
	downloadAnchorNode.remove();
})();
