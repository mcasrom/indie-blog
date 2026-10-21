// src/content.config.ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    abstract_en: z.string().optional(),
    resumen: z.array(z.string()).optional(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    image: z.string().optional(),
    categoria: z.string().default('análisis'),
    faq: z.array(z.object({ q: z.string(), a: z.string() })).optional(),
    serie: z.string().optional(),
    serie_numero: z.number().int().positive().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
