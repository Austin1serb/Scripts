(async () => {
	const allReviews = new Map();
	let hasNextPage = true;
	let pageCount = 1;

	console.log("🚀 Starting multi-page scrape...");

	while (hasNextPage) {
		console.log(`📄 Scraping page ${pageCount}...`);

		// 1. Scrape the current view
		const reviewItems = document.querySelectorAll("li.y-css-1sqelp2");

		reviewItems.forEach((item) => {
			const nameLinkEl = item.querySelector("a.y-css-12f4fi2");
			const name = nameLinkEl ? nameLinkEl.innerText.trim() : "Unknown";
			const profileUrl = nameLinkEl ? `https://www.yelp.com${nameLinkEl.getAttribute("href")}` : "";

			const dateEl = item.querySelector("span.y-css-1vi7y4e");
			let formattedDate = "";
			if (dateEl) {
				const dateObj = new Date(dateEl.innerText.trim());
				if (!isNaN(dateObj)) {
					const year = dateObj.getFullYear();
					const month = String(dateObj.getMonth() + 1).padStart(2, "0");
					const day = String(dateObj.getDate()).padStart(2, "0");
					formattedDate = `${year}-${month}-${day}`;
				}
			}

			const ratingEl = item.querySelector('div[role="img"][aria-label*="star rating"]');
			const numericRating = ratingEl ? parseInt(ratingEl.getAttribute("aria-label").match(/\d+/)[0]) : null;

			const contentEl = item.querySelector('p[class*="comment"] span.raw__09f24__PkHSg');
			const content = contentEl ? contentEl.innerText.trim() : "";

			const images = Array.from(item.querySelectorAll("img.y-css-1lq2n1z"))
				.filter((img) => img.src && !img.src.includes("60s.jpg"))
				.map((img) => ({
					url: img.src,
					description: img.alt || img.title || "",
				}));

			const profileImgEl = item.querySelector("img.y-css-1lq2n1z");
			const profileImage = profileImgEl ? profileImgEl.src : "";

			const uniqueKey = `${name}-${content.substring(0, 50)}`.toLowerCase();

			if (content && !allReviews.has(uniqueKey)) {
				allReviews.set(uniqueKey, {
					reviewer: name,
					profileUrl: profileUrl,
					profileImage: profileImage,
					rating: numericRating,
					date: formattedDate,
					content: content,
					images: images,
					reviewUrl: window.location.href,
				});
			}
		});

		// 2. Look for the "Next" button
		const nextButton = document.querySelector("a.next-link");

		if (nextButton) {
			console.log("➡️ Moving to next page...");
			nextButton.click();
			pageCount++;

			// Wait for new content to load
			await new Promise((resolve) => setTimeout(resolve, 4000));
		} else {
			hasNextPage = false;
			console.log("✅ No more pages found.");
		}
	}

	// 3. Final Export: Trigger File Download
	const finalData = Array.from(allReviews.values());
	const blob = new Blob([JSON.stringify(finalData, null, 2)], { type: "application/json" });
	const url = URL.createObjectURL(blob);
	const link = document.createElement("a");

	link.href = url;
	link.download = "yelp_reviews.json";
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
	URL.revokeObjectURL(url);

	console.log(`🎉 DONE! ${finalData.length} reviews collected and file downloaded.`);
	console.table(finalData);
})();
