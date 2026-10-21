// src/lib/readingTime.ts
// Tiempo de lectura por post: cuenta palabras del body markdown (sin
// frontmatter) y lo convierte a minutos (~200 palabras/min). Sin dependencias
// externas: es solo un cálculo de longitud, no un render.

const WPM = 200;

/** Palabras aproximadas de un body markdown (quita markdown pesado y código) */
export function countWords(body: string): number {
  const text = body
    .replace(/```[\s\S]*?```/g, " ") // bloques de código
    .replace(/`[^`]*`/g, " ") // inline code
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ") // imágenes
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // enlaces: solo el texto
    .replace(/[#>*|~_{}[\]<>]+/g, " ") // sintaxis markdown
    .replace(/[-–—]/g, " "); // guiones
  return text.split(/\s+/).filter(Boolean).length;
}

/** Minutos de lectura (mínimo 1). Toma opcionalmente el body markdown crudo. */
export function readingTime(body: string): number {
  const w = countWords(body);
  return Math.max(1, Math.round(w / WPM));
}

/** Formatea 'X min de lectura' con la palabra en plural/singular correcta. */
export function readingTimeLabel(body: string): string {
  const min = readingTime(body);
  return min === 1 ? "1 min de lectura" : `${min} min de lectura`;
}