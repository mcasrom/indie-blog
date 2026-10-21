// src/lib/resend.ts
// Envío de email vía Resend (reutiliza las claves de /home/deploy/newsletter/.env).
import fs from 'node:fs';

const ENV = '/home/deploy/newsletter/.env';

export function resendCfg(): { key: string; from: string } {
  const out = { key: '', from: 'newsletter@viajeinteligencia.com' };
  try {
    for (const line of fs.readFileSync(ENV, 'utf8').split('\n')) {
      const s = line.trim();
      if (!s || s.startsWith('#') || !s.includes('=')) continue;
      const i = s.indexOf('=');
      const k = s.slice(0, i).trim();
      const val = s.slice(i + 1).trim().replace(/^["']|["']$/g, '');
      if (k === 'RESEND_API_KEY' && val) out.key = val;
      if (k === 'RESEND_FROM' && val) out.from = val;
    }
  } catch {
    // sin fichero: quedará vacío y sendEmail devolverá false
  }
  return out;
}

export async function sendEmail(to: string, subject: string, html: string): Promise<boolean> {
  const { key, from } = resendCfg();
  if (!key) return false;
  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: [to], subject, html }),
    });
    return res.ok;
  } catch {
    return false;
  }
}
