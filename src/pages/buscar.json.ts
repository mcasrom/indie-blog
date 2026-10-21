// src/pages/buscar.json.ts
// Índice de búsqueda generado en build-time (estático, sin backend ni servicios externos).
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const prerender = true;

// Convierte el markdown en texto plano para poder buscar dentro del cuerpo.
function limpiar(md: string): string {
  return (md || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[#>*_`~|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export const GET: APIRoute = async () => {
  const posts = (await getCollection('posts')).filter((p) => !p.data.draft).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  const index = posts.map((p) => ({
    slug: p.slug,
    title: p.data.title,
    description: p.data.description || '',
    tags: p.data.tags || [],
    categoria: p.data.categoria,
    date: p.data.pubDate.toISOString().slice(0, 10),
    url: `/posts/${p.slug}/`,
    body: limpiar(p.body).slice(0, 3000),
  }));

  return new Response(JSON.stringify(index), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
