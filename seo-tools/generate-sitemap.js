// const fs = require('fs');
// const path = require('path');

// // Recursively fetch all routes from the app directory
// const getAllPages = (dir, prefix = '') => {
//   const files = fs.readdirSync(dir);
//   let paths = [];

//   files.forEach((file) => {
//     const filePath = path.join(dir, file);
//     const stat = fs.statSync(filePath);

//     if (stat.isDirectory()) {
//       paths = [...paths, ...getAllPages(filePath, `${prefix}/${file}`)];
//     } else if (file === 'page.js' || file === 'page.tsx') {
//       // Include only pages
//       const route = prefix || '/';
//       paths.push(route.replace(/\/index$/, '')); // Remove /index for root URLs
//     }
//   });

//   return paths;
// };

// // Generate the sitemap
// const generateSitemap = () => {
//   // Use environment variable or fallback to default
//   const siteUrl = process.env.NEXT_PUBLIC_URL || 'https://www.serbyte.net';
//   const appDir = path.join(process.cwd(), 'app');
//   const allPaths = getAllPages(appDir);

//   // Generate XML content
//   const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
// <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
// ${allPaths
//       .map((route) => {
//         return `
// 	<url>
// 		<loc>${siteUrl}${route}</loc>
// 		<changefreq>daily</changefreq>
// 		<priority>0.7</priority>
// 	</url>`;
//       })
//       .join('\n')}
// </urlset>`;

//   // Save the sitemap to the public directory
//   const sitemapPath = path.join(process.cwd(), 'public', 'sitemap.xml');
//   fs.writeFileSync(sitemapPath, sitemap, 'utf8');
//   console.log(`Sitemap generated at ${sitemapPath}`);
// };

// generateSitemap();