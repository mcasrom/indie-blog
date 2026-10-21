// src/lib/api.ts
// Helpers para endpoints API: rate-limit simple por IP y respuestas JSON.
import type { APIContext } from 'astro';

const hits = new Map<string, { n: number; reset: number }>();

export function rateLimit(ip: string, max = 30, windowMs = 10 * 60 * 1000): boolean {
  const now = Date.now();
  const e = hits.get(ip) || { n: 0, reset: now + windowMs };
  if (now > e.reset) { e.n = 0; e.reset = now + windowMs; }
  e.n += 1;
  hits.set(ip, e);
  return e.n > max;
}

export function clientIp(context: APIContext): string {
  const fwd = context.request.headers.get('x-forwarded-for');
  if (fwd) return fwd.split(',')[0].trim();
  return context.clientAddress || 'unknown';
}

export function jsonError(context: APIContext, status: number, error: string, message: string) {
  return new Response(JSON.stringify({ error, message }), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
}
