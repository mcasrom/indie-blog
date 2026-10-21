// src/lib/db.ts
// Conexión better-sqlite3 + inicialización de tablas.
// Tablas: likes (post_slug, count) y comments (id, post_slug, autor, texto,
// estado ['pendiente','aprobado','rechazado'], fecha).
// Un único archivo .db local. NADA de servicios externos.
import Database from 'better-sqlite3';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
import crypto from 'node:crypto';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// La BD vive en el raíz del proyecto (data/), fuera de src y de public.
// NOTA: se ancla a process.cwd() (el repo) para que sobreviva a los builds
// (el chunk compilado vive en dist/server/chunks y un path relativo a él
//  resolvería a dist/data, que astro build regenera vacío).
const DATA_DIR = process.env.DATA_DIR || path.resolve(process.cwd(), 'data');
const DB_PATH = path.join(DATA_DIR, 'analisis.db');

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (db) return db;
  fs.mkdirSync(DATA_DIR, { recursive: true });
  db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  db.exec(`
    CREATE TABLE IF NOT EXISTS likes (
      post_slug TEXT PRIMARY KEY,
      count INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS comments (
      id TEXT PRIMARY KEY,
      post_slug TEXT NOT NULL,
      autor TEXT NOT NULL,
      texto TEXT NOT NULL,
      estado TEXT NOT NULL DEFAULT 'pendiente',
      fecha TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_slug, estado);
  `);
  return db;
}

export function getLikes(slug: string): number {
  const row = getDb().prepare('SELECT count FROM likes WHERE post_slug = ?').get(slug) as { count: number } | undefined;
  return row ? row.count : 0;
}

export function addLike(slug: string): number {
  getDb()
    .prepare('INSERT INTO likes (post_slug, count) VALUES (?, 1) ON CONFLICT(post_slug) DO UPDATE SET count = count + 1')
    .run(slug);
  return getLikes(slug);
}

export function addComment(slug: string, autor: string, texto: string): { id: string; fecha: string } {
  const id = crypto.randomUUID();
  const fecha = new Date().toISOString();
  getDb()
    .prepare('INSERT INTO comments (id, post_slug, autor, texto, estado, fecha) VALUES (?,?,?,?,?,?)')
    .run(id, slug, autor, texto, 'pendiente', fecha);
  return { id, fecha };
}

export function listComments(slug: string): Array<{ id: string; autor: string; texto: string; fecha: string }> {
  return getDb()
    .prepare("SELECT id, autor, texto, fecha FROM comments WHERE post_slug = ? AND estado = 'aprobado' ORDER BY fecha ASC")
    .all(slug) as Array<{ id: string; autor: string; texto: string; fecha: string }>;
}

export function listPendingComments(): Array<{ id: string; post_slug: string; autor: string; texto: string; fecha: string }> {
  return getDb()
    .prepare("SELECT id, post_slug, autor, texto, fecha FROM comments WHERE estado = 'pendiente' ORDER BY fecha ASC")
    .all() as Array<{ id: string; post_slug: string; autor: string; texto: string; fecha: string }>;
}

export function setCommentState(id: string, estado: 'aprobado' | 'rechazado'): boolean {
  const r = getDb().prepare('UPDATE comments SET estado = ? WHERE id = ?').run(estado, id);
  return r.changes > 0;
}

export { DB_PATH };
