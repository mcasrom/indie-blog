// src/pages/api/confirm.ts
// GET /api/confirm?id=<token> — confirma la suscripción (doble opt-in).
import type { APIRoute } from 'astro';
import { confirmSubscriber } from '../../lib/subscribers';

export const prerender = false;

function page(ok: boolean): string {
  const t = ok ? 'Suscripción confirmada' : 'Enlace no válido';
  const p = ok
    ? 'Listo. Ya estás suscrito: recibirás el boletín en tu correo.'
    : 'Este enlace ya se usó o no es válido. Si crees que es un error, vuelve a suscribirte.';
  const accent = ok ? '#059669' : '#b91c1c';
  return `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${t} — Análisis</title><meta name="robots" content="noindex">
<style>body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
background:#f8fafc;color:#1e293b;display:flex;min-height:100vh;align-items:center;justify-content:center}
.c{max-width:520px;padding:32px;text-align:center}.i{font-size:2.4rem}
h1{font-size:1.3rem;margin:12px 0 6px}p{color:#475569;line-height:1.6}
a{display:inline-block;margin-top:18px;color:#fff;background:${accent};padding:10px 18px;
border-radius:9px;text-decoration:none;font-weight:700}</style></head>
<body><div class="c"><div class="i">${ok ? '✅' : '⚠️'}</div>
<h1 style="color:${accent}">${t}</h1><p>${p}</p>
<a href="https://indie.pruebapublica.com/">Volver al blog</a></div></body></html>`;
}

export const GET: APIRoute = async ({ request }) => {
  const id = new URL(request.url).searchParams.get('id') || '';
  const ok = id ? confirmSubscriber(id) : false;
  return new Response(page(ok), {
    status: ok ? 200 : 400,
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
};
