// @ts-check

import { readdirSync, readFileSync } from 'node:fs';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig, fontProviders } from 'astro/config';

const blogDir = new URL('./src/content/blog/', import.meta.url);

function readFrontmatterDate(text, key) {
	const match = text.match(new RegExp(`^${key}:\\s*'?([^'\\n]+)'?\\s*$`, 'm'));
	if (!match) return null;
	const date = new Date(match[1].trim());
	return Number.isNaN(date.getTime()) ? null : date;
}

function loadPostDates() {
	const dates = new Map();
	for (const file of readdirSync(blogDir)) {
		if (!/\.(md|mdx)$/.test(file)) continue;
		const text = readFileSync(new URL(file, blogDir), 'utf8');
		const published = readFrontmatterDate(text, 'pubDate');
		const updated = readFrontmatterDate(text, 'updatedDate');
		const best = updated ?? published;
		if (best) dates.set(file.replace(/\.(md|mdx)$/, ''), best);
	}
	return dates;
}

const postDates = loadPostDates();
const latestPostDate = [...postDates.values()].reduce((a, b) => (a > b ? a : b), new Date(0));

export default defineConfig({
	compressHTML: false,
	site: 'https://semnarrativa.com.br',
	integrations: [
		mdx(),
		sitemap({
			serialize(item) {
				const path = new URL(item.url).pathname.replace(/\/$/, '');
				if (path === '' || path === '/blog') {
					return { ...item, lastmod: latestPostDate.toISOString() };
				}
				const match = path.match(/^\/blog\/([^/]+)$/);
				const postDate = match ? postDates.get(match[1]) : undefined;
				return postDate ? { ...item, lastmod: postDate.toISOString() } : item;
			},
		}),
	],
	fonts: [
		{
			provider: fontProviders.google(),
			name: 'Montserrat',
			cssVariable: '--font-montserrat',
		},
	],
});
