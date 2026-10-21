// src/pages/api/comment/[slug].ts
import type { APIRoute } from 'astro';
import { addComment, listComments } from '../../../lib/db';
import { clientIp, jsonError, rateLimit } from '../../../lib/api';

export const prerender = false;

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export const POST: APIRoute = async ({ params, request }) => {
  const slug = params.slug || '';
  if (!slug) return jsonError({ request, params, props: {} } as any, 400, 'bad_slug', 'Falta el slug del post.');
  const ip = clientIp({ request, params, props: {} } as any);
  if (rateLimit(ip, 10, 10 * 60 * 1000)) return jsonError({ request, params, props: {} } as any, 429, 'rate_limit', 'Demasiados comentarios. Inténtalo más tarde.');

  let body: { autor?: string; texto?: string };
  try {
    body = await request.json();
  } catch {
    return jsonError({ request, params, props: {} } as any, 400, 'bad_json', 'JSON inválido.');
  }
  const autor = (body.autor || '').trim().slice(0, 80);
  const texto = (body.texto || '').trim().slice(0, 2000);
  if (!autor || !texto) return jsonError({ request, params, props: {} } as any, 400, 'campos_incompletos', 'Autor y texto son obligatorios.');
  // Escapar HTML para prevenir XSS en renderizado.
  const { id, fecha } = addComment(slug, esc(autor), esc(texto));
  return new Response(JSON.stringify({ ok: true, id, fecha, pendiente: true }), {
    status: 201,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};

export const GET: APIRoute = ({ params }) => {
  const slug = params.slug || '';
  const comments = listComments(slug);
  return new Response(JSON.stringify({ ok: true, comments }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
