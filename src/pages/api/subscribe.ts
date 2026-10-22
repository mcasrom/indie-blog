// src/pages/api/subscribe.ts
// POST /api/subscribe — alta de newsletter con DOBLE OPT-IN.
// Guarda el email (confirmado=0) y envía un correo de confirmación.
import type { APIRoute } from 'astro';
import { addSubscriber } from '../../lib/subscribers';
import { sanearTemas } from '../../lib/newsletter';
import { clientIp, jsonError, rateLimit } from '../../lib/api';
import { sendEmail } from '../../lib/resend';

export const prerender = false;

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const BASE = 'https://indie.pruebapublica.com';

function confirmHtml(link: string): string {
  return `<div style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;max-width:520px;margin:0 auto;color:#1e293b;line-height:1.6">
<h2>Confirma tu suscripción</h2>
<p>Para activar tu suscripción al boletín de <b>indie</b>, pulsa el botón:</p>
<p><a href="${link}" style="display:inline-block;background:#1e293b;color:#fff;padding:11px 20px;border-radius:9px;text-decoration:none;font-weight:700">Confirmar suscripción</a></p>
<p style="color:#64748b;font-size:.9rem">Qué recibirás: <b>1 correo al mes</b> con lo que merece la pena (y nada más). Sin spam; baja en un clic.</p>
<p style="color:#94a3b8;font-size:.8rem">Si no fuiste tú, ignora este mensaje.</p>
<p style="color:#94a3b8;font-size:.8rem">O copia este enlace: ${link}</p></div>`;
}

export const POST: APIRoute = async ({ request }) => {
  const ip = clientIp({ request } as any);
  if (rateLimit(ip, 10, 10 * 60 * 1000)) return jsonError({ request } as any, 429, 'rate_limit', 'Demasiadas peticiones. Inténtalo más tarde.');

  let body: { email?: string; temas?: unknown };
  try {
    body = await request.json();
  } catch {
    return jsonError({ request } as any, 400, 'bad_json', 'JSON inválido.');
  }
  const email = (body.email || '').trim().toLowerCase().slice(0, 200);
  if (!email || /[<>"']/.test(email) || !EMAIL_RE.test(email)) {
    return jsonError({ request } as any, 400, 'email_invalido', 'Introduce un email válido.');
  }
  const temas = sanearTemas(body.temas);
  const { id, existia } = addSubscriber(email, ip, temas);
  const link = `${BASE}/api/confirm?id=${id}`;
  const enviado = await sendEmail(email, 'Confirma tu suscripción — indie', confirmHtml(link));
  return new Response(JSON.stringify({ ok: true, existia, confirmacion_enviada: enviado }), {
    status: 201,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
