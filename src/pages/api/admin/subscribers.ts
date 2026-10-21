// src/pages/api/admin/subscribers.ts
// GET — lista de suscriptores de newsletter. Protegido por ADMIN_SECRET.
import type { APIRoute } from 'astro';
import { listSubscribers, countSubscribers } from '../../../lib/subscribers';
import { jsonError } from '../../../lib/api';

export const prerender = false;

const ADMIN_SECRET = process.env.ADMIN_SECRET || '';

function auth(request: Request): boolean {
  if (!ADMIN_SECRET) return false;
  return request.headers.get('x-admin-secret') === ADMIN_SECRET;
}

export const GET: APIRoute = ({ request }) => {
  if (!auth(request)) return jsonError({ request } as any, 401, 'no_autorizado', 'Secret incorrecto.');
  return new Response(JSON.stringify({ ok: true, total: countSubscribers(), suscriptores: listSubscribers() }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
