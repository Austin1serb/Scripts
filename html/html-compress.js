(function condenseHTML() {
	// Remove all <script> elements
	document.querySelectorAll("script").forEach((script) => script.remove());
	// document.querySelectorAll("svg").forEach((script) => script.remove());
	// document.querySelectorAll("footer").forEach((footer) => footer.remove());
	// document.querySelectorAll("nav").forEach((footer) => footer.remove());
	// document.querySelectorAll("p").forEach((footer) => footer.remove());
	// document.querySelectorAll("ol").forEach((footer) => footer.remove());
	// document.querySelectorAll("ul").forEach((footer) => footer.remove());
	// document.querySelectorAll("image").forEach((footer) => footer.remove());

	// Remove all style attributes and classes from elements
	document.querySelectorAll("*").forEach((node) => {
		node.removeAttribute("*");
		node.removeAttribute("class");
		// node.removeAttribute("id");
		node.removeAttribute("srcset");
		node.removeAttribute("href");
		node.removeAttribute("src");
		node.removeAttribute("href");
		node.removeAttribute("sizes");
		node.removeAttribute("title");
		node.removeAttribute("alt");
		// node.removeAttribute("data-src");
		// node.removeAttribute("data-src-set");
		// node.removeAttribute("data-src-set");
		// Remove any other style-related attributes
		const attrs = Array.from(node.attributes);
		console.log("attrs: ", attrs);
		// attrs.forEach((attr) => {
		// 	if (attr.name.startsWith("data-") || attr.name.includes("style")) {
		// 		node.removeAttribute(attr.name);
		// 	}
		// });
	});

	// Remove all comments
	const removeComments = (node) => {
		const childNodes = Array.from(node.childNodes);
		childNodes.forEach((child) => {
			if (child.nodeType === Node.COMMENT_NODE) {
				node.removeChild(child);
			} else if (child.nodeType === Node.ELEMENT_NODE) {
				removeComments(child);
			}
		});
	};
	removeComments(document.documentElement);

	// // Clear all SVG elements but keep the tags
	// document.querySelectorAll("image").forEach((svg) => {
	// 	while (svg.firstChild) {
	// 		svg.remove;
	// 	}
	// });

	console.log("HTML has been condensed. Only element tags and text content remain.");
})();
