import { getCollection } from 'astro:content';

function limparMarkdown(texto) {
	return texto
		.replace(/```[\s\S]*?```/g, ' ')
		.replace(/<[^>]+>/g, ' ')
		.replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
		.replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
		.replace(/[#>*_`|]/g, ' ')
		.replace(/\s+/g, ' ')
		.trim();
}

export async function GET() {
	const posts = (await getCollection('blog')).sort(
		(a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf(),
	);
	const itens = posts.map((post) => ({
		t: post.data.title,
		d: post.data.description,
		c: post.data.category,
		u: `/blog/${post.id}/`,
		b: limparMarkdown(post.body ?? ''),
	}));
	return new Response(JSON.stringify(itens), {
		headers: { 'Content-Type': 'application/json; charset=utf-8' },
	});
}
