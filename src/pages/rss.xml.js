// src/pages/rss.xml.js — Feed RSS completo del blog
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { isIndiePost } from '../lib/indie';

export async function GET(context) {
  const posts = (await getCollection('posts')).filter(isIndiePost)
    .filter((p) => !p.data.draft)
    .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return rss({
    title: 'indie — Linux, self-hosting y software hecho a mano',
    description: 'Linux, self-hosting, homelab y software indie: artículos prácticos y sin ruido.',
    site: "https://analisis.pruebapublica.com",
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.pubDate,
      link: `/posts/${post.slug}/`,
      categories: post.data.tags,
    })),
    customData: '<language>es</language>',
  });
}
