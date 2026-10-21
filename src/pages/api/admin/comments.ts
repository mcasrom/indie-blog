// src/pages/api/admin/comments.ts
// Endpoints de moderación: listar pendientes, aprobar/rechazar.
// Protegido por header X-Admin-Secret (ADMIN_SECRET env).
import type { APIRoute } from 'astro';
import { listPendingComments, setCommentState } from '../../../lib/db';
import { jsonError } from '../../../lib/api';

export const prerender = false;

const ADMIN_SECRET = process.env.ADMIN_SECRET || '';

function auth(request: Request): boolean {
  if (!ADMIN_SECRET) return false;
  return request.headers.get('x-admin-secret') === ADMIN_SECRET;
}

export const GET: APIRoute = ({ request }) => {
  if (!auth(request)) return jsonError({ request } as any, 401, 'no_autorizado', 'Secret incorrecto.');
  return new Response(JSON.stringify({ ok: true, pendientes: listPendingComments() }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};

export const POST: APIRoute = async ({ request }) => {
  if (!auth(request)) return jsonError({ request } as any, 401, 'no_autorizado', 'Secret incorrecto.');
  let body: { id?: string; accion?: string };
  try {
    body = await request.json();
  } catch {
    return jsonError({ request } as any, 400, 'bad_json', 'JSON inválido.');
  }
  const { id, accion } = body;
  if (!id || (accion !== 'aprobado' && accion !== 'rechazado')) {
    return jsonError({ request } as any, 400, 'bad_params', 'id y accion (aprobado/rechazado) obligatorios.');
  }
  const ok = setCommentState(id, accion);
  if (!ok) return jsonError({ request } as any, 404, 'no_encontrado', 'Comentario no encontrado.');
  return new Response(JSON.stringify({ ok: true, id, estado: accion }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
