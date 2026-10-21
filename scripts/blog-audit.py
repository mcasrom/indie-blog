#!/usr/bin/env python3
"""Auditoría editorial del blog: scoring por post sobre 100 puntos y reporte Markdown.

Uso:
    python3 scripts/blog-audit.py                    # reporte por stdout
    python3 scripts/blog-audit.py --salida blog-audit.md
    python3 scripts/blog-audit.py --json
"""

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata

try:
    import yaml
except ImportError:
    sys.exit("Falta pyyaml. Instala con: pip install pyyaml")

POSTS_DIR = "src/content/posts"
PUBLIC_DIRS = ("dist/client", "public")
SITIO = "analisis.pruebapublica.com"

RUBRICA = [
    ("titulo", 4),
    ("description<=155", 8),
    ("pubDate", 3),
    ("autor", 4),
    ("tags>=2", 6),
    ("og-image", 8),
    ("draft:false", 3),
    ("assisted", 4),
    ("serie+numero", 8),
    ("serie-consistente", 6),
    ("enlace-radar-fimi", 8),
    ("enlace-interno-post", 14),
    ("fuentes-enlazadas>=2", 12),
    ("palabras>=600", 12),
]

SIN_TILDE = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")


def sin_tilde(s):
    return s.translate(SIN_TILDE)


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not m:
        return None, content
    raw = m.group(1)
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        sys.exit(f"YAML inválido en {path}: {exc}")
    return fm, m.group(2)


def og_existe(img):
    if not img:
        return False
    if str(img).startswith(("http://", "https://")):
        return True
    for base in PUBLIC_DIRS:
        if os.path.exists(os.path.join(base, str(img).lstrip("/"))):
            return True
    return False


def enlaces(body):
    return re.findall(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", body)


def es_enlace_post(href):
    return "/posts/" in href


def es_enlace_fimi(href):
    return "fimi.viajeinteligencia.com" in href


def es_fuente_externa(href):
    if not href.startswith(("http://", "https://")):
        return False
    if SITIO in href:
        return False
    if any(d in href for d in ("mastodon.social", "bsky.app", "twitter.com", "x.com", "ko-fi.com", "linkedin.com")):
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Auditoría editorial del blog")
    ap.add_argument("--salida", help="escribe el reporte Markdown en ese archivo")
    ap.add_argument("--json", action="store_true", help="salida JSON en vez de Markdown")
    args = ap.parse_args()

    if not os.path.isdir(POSTS_DIR):
        sys.exit(f"No existe {POSTS_DIR}. Ejecuta desde la raíz del repo.")

    posts = []
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, fname)
        fm, body = parse_frontmatter(path)
        if fm is None:
            sys.exit(f"{path}: sin frontmatter")
        posts.append({"slug": fname[:-3], "fm": fm, "body": body})

    series = {}
    for p in posts:
        nombre = p["fm"].get("serie")
        if nombre:
            series.setdefault(str(nombre), []).append(p)

    series_consistente = set()
    for nombre, items in series.items():
        numeros = sorted(i["fm"].get("serie_numero") for i in items if isinstance(i["fm"].get("serie_numero"), int))
        if len(numeros) == len(items) and numeros == list(range(1, len(items) + 1)):
            series_consistente.add(nombre)

    lineas = []
    for p in posts:
        fm, body = p["fm"], p["body"]
        desc = str(fm.get("description") or "")
        tags = fm.get("tags") or []
        serie = fm.get("serie")
        hrefs = enlaces(body)
        fuentes = {h for h in hrefs if es_fuente_externa(h)}
        palabras = len(re.sub(r"[#*_>`\[\]()]", " ", body).split())

        checks = {
            "titulo": bool(fm.get("title")),
            "description<=155": bool(desc) and len(desc) <= 155,
            "pubDate": bool(fm.get("pubDate")),
            "autor": bool(fm.get("author")),
            "tags>=2": len(tags) >= 2,
            "og-image": og_existe(fm.get("image")),
            "draft:false": fm.get("draft") is False,
            "assisted": bool(fm.get("assisted")),
            "serie+numero": bool(serie) and isinstance(fm.get("serie_numero"), int),
            "serie-consistente": bool(serie) and str(serie) in series_consistente,
            "enlace-radar-fimi": any(es_enlace_fimi(h) for h in hrefs),
            "enlace-interno-post": any(es_enlace_post(h) for h in hrefs),
            "fuentes-enlazadas>=2": len(fuentes) >= 2,
            "palabras>=600": palabras >= 600,
        }
        faltan = [k for k, _ in RUBRICA if not checks[k]]
        score = sum(pts for k, pts in RUBRICA if checks[k])

        p.update(
            {
                "title": str(fm.get("title") or ""),
                "score": score,
                "checks": checks,
                "faltan": faltan,
                "categoria": str(fm.get("categoria") or ""),
                "desc_len": len(desc),
                "tags_n": len(tags),
                "palabras": palabras,
                "fuentes_n": len(fuentes),
                "serie": str(serie) if serie else "",
                "serie_num": fm.get("serie_numero"),
            }
        )
        lineas.append(p)

    lineas.sort(key=lambda x: (-x["score"], x["title"]))
    total = len(lineas)
    media = sum(p["score"] for p in lineas) / total if total else 0
    maximo = max((p["score"] for p in lineas), default=0)
    minimo = min((p["score"] for p in lineas), default=0)
    hoy = datetime.date.today().isoformat()
    etiquetas = {t for p in lineas for t in (p["fm"].get("tags") or [])}

    if args.json:
        salida = {
            "posts": total,
            "media": round(media, 1),
            "max": maximo,
            "min": minimo,
            "rubrica": dict(RUBRICA),
            "series": {k: len(v) for k, v in series.items()},
            "detalle": lineas,
        }
        texto = json.dumps(salida, ensure_ascii=False, indent=2, default=str)
    else:
        L = []
        L.append("# Auditoría editorial del blog\n")
        L.append(f"Generado por `scripts/blog-audit.py` el {hoy}. {total} artículos publicados.\n")
        L.append("## Nota global\n")
        L.append("| Métrica | Valor |")
        L.append("| --- | --- |")
        L.append(f"| Media | {media:.1f}/100 |")
        L.append(f"| Máxima | {maximo}/100 |")
        L.append(f"| Mínima | {minimo}/100 |")
        L.append(f"| Artículos con serie | {sum(1 for p in lineas if p['serie'])}/{total} |")
        L.append(f"| Tags distintos | {len(etiquetas)} |")
        L.append(f"| Enlaces internos entre posts | {sum(1 for p in lineas if p['checks']['enlace-interno-post'])}/{total} |")
        L.append(f"| Enlaces al Radar FIMI | {sum(1 for p in lineas if p['checks']['enlace-radar-fimi'])}/{total} |")
        L.append(f"| Con ≥2 fuentes externas enlazadas | {sum(1 for p in lineas if p['checks']['fuentes-enlazadas>=2'])}/{total} |")
        L.append(f"| Categoría declarada | {sum(1 for p in lineas if p['categoria'])}/{total} (género por diseño, no puntúa) |\n")
        L.append("## Rúbrica (100 puntos)\n")
        L.append("| Criterio | Puntos |")
        L.append("| --- | --- |")
        for k, pts in RUBRICA:
            ok = sum(1 for p in lineas if p["checks"][k])
            L.append(f"| {k} | {pts} |")
        L.append("")
        L.append("## Series\n")
        if series:
            L.append("| Serie | Partes | Numeración |")
            L.append("| --- | --- | --- |")
            for nombre, items in sorted(series.items()):
                marca = "correcta" if nombre in series_consistente else "revisar"
                L.append(f"| {nombre} | {len(items)} | {marca} |")
        else:
            L.append("Ninguna serie declarada.")
        L.append("")
        L.append("## Ranking\n")
        L.append("| # | Puntos | Título | Serie | Palabras | Fuentes | Faltan |")
        L.append("| --- | --- | --- | --- | --- | --- | --- |")
        for i, p in enumerate(lineas, 1):
            serie_txt = f"{p['serie']} {p['serie_num']}/{len(series[p['serie']])}" if p["serie"] else "—"
            faltan = ", ".join(p["faltan"]) if p["faltan"] else "—"
            L.append(
                f"| {i} | {p['score']} | [{p['title']}](/posts/{p['slug']}/) | {serie_txt} | "
                f"{p['palabras']} | {p['fuentes_n']} | {faltan} |"
            )
        L.append("")
        L.append("## Detalle por artículo\n")
        for p in lineas:
            L.append(f"### {p['score']}/100 · {p['title']}\n")
            L.append(f"- slug: `{p['slug']}`")
            L.append(f"- description: {p['desc_len']} car. | tags: {p['tags_n']} | palabras: {p['palabras']} | fuentes enlazadas: {p['fuentes_n']}")
            L.append(f"- cumple: {', '.join(k for k, _ in RUBRICA if p['checks'][k]) or '—'}")
            L.append(f"- falta: {', '.join(p['faltan']) or '—'}\n")
        texto = "\n".join(L)

    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as fh:
            fh.write(texto + "\n")
        print(f"Reporte escrito en {args.salida} ({total} artículos, media {media:.1f}/100)")
    else:
        print(texto)


if __name__ == "__main__":
    main()
