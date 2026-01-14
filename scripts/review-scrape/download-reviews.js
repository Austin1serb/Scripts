// This script finds all links with the label "View full review" and clicks them
const reviewButtons = document.querySelectorAll('a[aria-label="View full review"]');

reviewButtons.forEach(button => {
    button.click();
});

console.log(`Expanded ${reviewButtons.length} reviews.`);

(function scrapeGoogleReviewsWithProfilePics() {
  const reviews = [];
  const reviewElements = document.querySelectorAll('article.VaHEVc');

  reviewElements.forEach(el => {
      // 1. Reviewer Name and Profile Link
      const nameEl = el.querySelector('a[jsname="xs1xe"]');
      const reviewer = nameEl ? nameEl.innerText.trim() : 'Anonymous';
      const profileUrl = nameEl ? nameEl.href : '';

      // 2. Profile Image URL
      const profileImgEl = el.querySelector('.PidtNe img');
      const profileImage = profileImgEl ? profileImgEl.src : '';

      // 3. Rating
      const ratingEl = el.querySelector('span[role="img"][aria-label*="star"]');
      const rating = ratingEl ? ratingEl.getAttribute('aria-label') : 'No rating';

      // 4. Date
      const dateEl = el.querySelector('.KEfuhb');
      const date = dateEl ? dateEl.innerText.trim() : '';

      // 5. Content (Full text)
      const fullTextEl = el.querySelector('[jsname="PBWx0c"]');
      let content = '';
      if (fullTextEl && fullTextEl.innerText.trim().length > 0) {
          content = fullTextEl.innerText.trim();
      } else {
          const shortTextEl = el.querySelector('.gyKkFe.JhRJje.Fv38Af');
          content = shortTextEl ? shortTextEl.innerText.trim() : '';
      }

      // 6. Review Images (Photos of the work)
      const images = [];
      const mediaContainer = el.querySelector('.Jj4RKe');
      if (mediaContainer) {
          const imgTags = mediaContainer.querySelectorAll('img');
          imgTags.forEach(img => {
              // Only collect if it's not a tiny thumbnail or profile placeholder
              if (img.src && !img.src.includes('profile/picture')) {
                  images.push(img.src);
              }
          });
      }

      reviews.push({
          reviewer,
          profileUrl,
          profileImage,
          rating,
          date,
          content,
          images
      });
  });

  console.log(`Scraped ${reviews.length} reviews with profile images.`);
  
  // Create and trigger download of the JSON file
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reviews, null, 2));
  const downloadAnchorNode = document.createElement('a');
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", "bespoke_reviews_full.json");
  document.body.appendChild(downloadAnchorNode); 
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
})();
