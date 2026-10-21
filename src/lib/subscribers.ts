// src/lib/subscribers.ts
// Newsletter: suscripciones por email almacenadas localmente (SQLite).
// Sin servicios externos. Tabla: subscribers (id, email, ip, confirmado,
// temas, fecha). Doble opt-in: alta con confirmado=0; se confirma vía
// /api/confirm. `temas` = CSV de slugs de los temas elegidos ("" = todos).
import { getDb } from './db';
import crypto from 'node:crypto';

getDb().exec(`
  CREATE TABLE IF NOT EXISTS subscribers (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    ip TEXT,
    confirmado INTEGER NOT NULL DEFAULT 0,
    temas TEXT NOT NULL DEFAULT '',
    fecha TEXT NOT NULL
  );
`);

// Migración idempotente (regla 27: un esquema nuevo necesita su paso propio):
// instalaciones antiguas no tienen la columna `temas`.
const _cols = (getDb().prepare('PRAGMA table_info(subscribers)').all() as Array<{ name: string }>).map((c) => c.name);
if (!_cols.includes('temas')) {
  getDb().exec("ALTER TABLE subscribers ADD COLUMN temas TEXT NOT NULL DEFAULT ''");
}

export function addSubscriber(
  email: string,
  ip: string,
  temas: string[] = []
): { id: string; fecha: string; existia: boolean } {
  const fecha = new Date().toISOString();
  const normalized = email.toLowerCase();
  const exists = getDb().prepare('SELECT id, temas FROM subscribers WHERE email = ?').get(normalized) as
    | { id: string; temas: string | null }
    | undefined;
  if (exists) {
    if (temas.length) {
      const prev = (exists.temas || '').split(',').filter(Boolean);
      const merged = [...new Set([...prev, ...temas])].join(',');
      getDb().prepare('UPDATE subscribers SET temas = ? WHERE id = ?').run(merged, exists.id);
    }
    return { id: exists.id, fecha, existia: true };
  }
  const id = crypto.randomUUID();
  getDb()
    .prepare('INSERT INTO subscribers (id, email, ip, confirmado, temas, fecha) VALUES (?,?,?,0,?,?)')
    .run(id, normalized, ip || null, temas.join(','), fecha);
  return { id, fecha, existia: false };
}

export function confirmSubscriber(id: string): boolean {
  const r = getDb().prepare('UPDATE subscribers SET confirmado = 1 WHERE id = ?').run(id);
  return r.changes > 0;
}

export function unsubscribeSubscriber(id: string): boolean {
  const r = getDb().prepare('UPDATE subscribers SET confirmado = 0 WHERE id = ?').run(id);
  return r.changes > 0;
}

export function listSubscribers(): Array<{ id: string; email: string; ip: string | null; confirmado: number; temas: string; fecha: string }> {
  return getDb()
    .prepare('SELECT id, email, ip, confirmado, temas, fecha FROM subscribers ORDER BY fecha DESC')
    .all() as Array<{ id: string; email: string; ip: string | null; confirmado: number; temas: string; fecha: string }>;
}

export function countSubscribers(): number {
  const row = getDb().prepare('SELECT COUNT(*) AS n FROM subscribers').get() as { n: number };
  return row.n;
}
