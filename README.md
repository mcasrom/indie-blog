# indie — Linux, self-hosting y software hecho a mano

Blog sobre herramientas que resuelven problemas sin ruido: software pequeño,
hecho con intención, que puedes entender, probar y modificar.

**Sitio:** https://indie.pruebapublica.com

## Entradas publicadas

- [¿Qué significa «indie» en el mundo Linux?](https://indie.pruebapublica.com/posts/que-significa-indie-en-linux/)
- [Cómo decido si una herramienta indie merece la pena: 6 filtros](https://indie.pruebapublica.com/posts/como-evaluar-herramienta-indie-6-filtros/)
- [Mantener un observatorio indie en un VPS de 4 GB](https://indie.pruebapublica.com/posts/mantener-observatorio-indie-vps-4gb/)

## Stack

- **Astro** (SSG) + **TailwindCSS v4**. Sin frameworks pesados.
- **Nginx** sirviendo `dist/client/` + **proxy `/api/` y `/admin/`** a un proceso
  Node (adapter `@astrojs/node`, PM2 `indie-blog`, `127.0.0.1:3020`).
- **SQLite** local (`better-sqlite3`) en `data/` (likes, comentarios, suscriptores),
  **fuera de `dist/`** para que el build no lo borre.
- Endpoints: `GET/POST /api/like/:slug`, `GET/POST /api/comment/:slug`,
  `GET /api/comments/:slug`, `POST /api/subscribe`, `GET /api/confirm`,
  `/api/unsubscribe`, `/admin/*`.
- **Búsqueda estática**: `src/pages/buscar.json.ts` → `/buscar.json`.
- **Sitemap** (`@astrojs/sitemap`), `robots.txt`, `llms.txt`, RSS en `/rss.xml`.

## Estructura

```
src/
  components/     Header, Footer, Sidebar, PostCard, NewsletterForm, LikeButton…
  content/posts/  un directorio por post (index.md + imagen opcional)
  layouts/        Layout.astro (SEO, OG, JSON-LD, tema claro/oscuro)
  lib/            db, resend, subscribers, newsletter, indie
  pages/          index, archivo, tags, categorias, buscar, sobre, api/*
public/           favicon, iconos, og-indie.png, robots.txt, llms.txt
data/             SQLite (no versionado)
```

## Desarrollo

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # genera dist/
```

## Despliegue

```bash
npm run build
rsync -a --delete dist/client/ /var/www/indie/
pm2 restart indie-blog      # solo si cambian endpoints o assets de /public
```

Tras desplegar: purgar caché de Cloudflare (`pruebapublica`) y, si hay páginas
nuevas, enviar `/sitemap-0.xml` a IndexNow.

## Añadir un post

Crear `src/content/posts/<slug>/index.md` con el frontmatter del esquema
(`src/content.config.ts`): `title`, `description`, `pubDate`, `tags`, `categoria`,
`image`, `draft`. Las etiquetas válidas del blog están en `src/lib/indie.ts`.

## Cross-promo

Los enlaces a otros proyectos del ecosistema (FIMI, vivienda, municipal, NearMe,
29N, agenda) llevan `utm_source=indie&utm_medium=crosspromo`. El blog de análisis
usa `utm_source=analisis`; no mezclar.

## Licencia

AGPL-3.0 (ver `LICENSE`).
