// src/lib/newsletter.ts
// Temas de suscripción del boletín ("te aviso de X"). Fuente única de verdad:
// el formulario, la API y el saneado la comparten.
export type TemaNewsletter = { slug: string; label: string };

export const TEMAS_NEWSLETTER: TemaNewsletter[] = [
  { slug: 'linux', label: 'Linux y escritorio' },
  { slug: 'terminal-y-cli', label: 'Terminal y CLI' },
  { slug: 'automatizacion', label: 'Automatización' },
  { slug: 'self-hosting', label: 'Self-hosting' },
  { slug: 'homelab', label: 'Homelab' },
  { slug: 'software-indie', label: 'Software indie' },
];

export const TEMAS_SLUGS = new Set(TEMAS_NEWSLETTER.map((t) => t.slug));

export function sanearTemas(input: unknown): string[] {
  if (!Array.isArray(input)) return [];
  return [
    ...new Set(
      input
        .map((x) => String(x).trim().toLowerCase())
        .filter((s) => TEMAS_SLUGS.has(s))
    ),
  ];
}
