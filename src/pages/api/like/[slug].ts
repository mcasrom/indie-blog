// src/pages/api/like/[slug].ts
import type { APIRoute } from 'astro';
import { addLike, getLikes } from '../../../lib/db';
import { clientIp, jsonError, rateLimit } from '../../../lib/api';

export const prerender = false;

export const GET: APIRoute = ({ params, request }) => {
  const slug = params.slug || '';
  if (!slug) return jsonError({ request, params, props: {} } as any, 400, 'bad_slug', 'Falta el slug del post.');
  const count = getLikes(slug);
  return new Response(JSON.stringify({ ok: true, slug, count }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};

export const POST: APIRoute = ({ params, request }) => {
  const slug = params.slug || '';
  if (!slug) return jsonError({ request, params, props: {} } as any, 400, 'bad_slug', 'Falta el slug del post.');
  const ip = clientIp({ request, params, props: {} } as any);
  if (rateLimit(ip)) return jsonError({ request, params, props: {} } as any, 429, 'rate_limit', 'Demasiadas peticiones. Inténtalo más tarde.');
  const count = addLike(slug);
  return new Response(JSON.stringify({ ok: true, slug, count }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
