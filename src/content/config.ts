import { z, defineCollection } from 'astro:content';

// Single file per slug, triple fields. Slugs stay English.
// EN required; ES/VI optional -> render EN + banner (no 404).
const pages = defineCollection({
  type: 'content',
  schema: z.object({
    slug_key: z.string().optional().default(''),
    title_en: z.string().max(60),
    title_es: z.string().max(60).optional().default(''),
    title_vi: z.string().max(60).optional().default(''),
    body_es: z.string().optional().default(''),
    body_vi: z.string().optional().default(''),
    updated: z.coerce.date().optional(),
    draft: z.boolean().optional().default(false),
  }),
});

export const collections = { pages };
