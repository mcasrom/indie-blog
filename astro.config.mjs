// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import fs from 'node:fs';
import path from 'node:path';

// Mapa slug -> pubDate (para lastmod real en el sitemap).
// Se lee el frontmatter de cada post en build-time (sin dependencias extra).
const postsDir = path.resolve('./src/content/posts');
const lastmodPorSlug = {};
try {
  for (const f of fs.readdirSync(postsDir)) {
    const full = path.join(postsDir, f);
    let file = null;
    let slug = null;
    if (f.endsWith('.md')) {
      file = full;
      slug = f.replace(/\.md$/, '');
    } else if (fs.statSync(full).isDirectory()) {
      const idx = path.join(full, 'index.md');
      if (fs.existsSync(idx)) {
        file = idx;
        slug = f;
      }
    }
    if (!file || !slug) continue;
    const src = fs.readFileSync(file, 'utf8');
    const m = src.match(/^pubDate:\s*["']?([0-9]{4}-[0-9]{2}-[0-9]{2})/m);
    if (m) lastmodPorSlug[slug] = m[1];
  }
} catch (e) {
  // si falla, el sitemap se genera sin lastmod
}

// https://astro.build/config
export default defineConfig({
  site: 'https://indie.pruebapublica.com',
  output: 'static',
  adapter: node({ mode: 'standalone' }),
  integrations: [
    sitemap({
      filter: (page) => !page.includes('/admin/'),
      serialize(item) {
        const m = item.url.match(/\/posts\/([^/]+)\/?$/);
        if (m && lastmodPorSlug[m[1]]) {
          item.lastmod = new Date(lastmodPorSlug[m[1]]).toISOString();
        }
        return item;
      },
    }),
  ],
  markdown: {
    // CTA de newsletter a mitad de cada artículo (tras el 2º <h2>).
  },
  vite: { plugins: [tailwindcss()] },
});
