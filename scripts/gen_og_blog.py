#!/usr/bin/env python3
"""gen_og_blog.py — tarjeta Open Graph (1200x630) para un post del blog.

Estilo de la casa: fondo navy, barra naranja arriba, kicker naranja,
titulo serif (1a linea blanca, resto azul), subtitulo gris, palabras
clave en blanco y pie con dominio + fecha.

Uso:
  /usr/bin/python3 scripts/gen_og_blog.py \
      --out public/mi-post-og.png \
      --kicker "CEUTA 2026 · 4/5" \
      --title "Titulo del post" \
      --subtitle "Subtitulo" \
      --keywords "a · b · c" \
      --date 2026-09-02
"""
import argparse
import textwrap
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties

NAVY = "#0f172a"
ORANGE = "#F97316"
BLUE = "#38bdf8"
GRAY = "#94a3b8"
FAINT = "#64748b"

SERIF = FontProperties(family="DejaVu Serif", weight="bold")
SANS = FontProperties(family="DejaVu Sans")
SANS_B = FontProperties(family="DejaVu Sans", weight="bold")

W, H, DPI = 1200, 630, 100
MARGIN = 0.055


def title_fs(title: str) -> int:
    n = len(title)
    if n <= 30:
        return 44
    if n <= 50:
        return 40
    if n <= 75:
        return 33
    if n <= 110:
        return 27
    return 23


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--kicker", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--keywords", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--site", default="analisis.pruebapublica.com")
    a = ap.parse_args()

    fs = title_fs(a.title)
    wrap_w = min(34, max(16, int((W * (1 - 2 * MARGIN)) / (fs * 0.56))))
    title_lines = textwrap.wrap(a.title, width=wrap_w)
    lh = fs * 1.32 / H

    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # barra naranja superior
    ax.add_patch(Rectangle((0, 0.972), 1, 0.028, color=ORANGE, transform=ax.transAxes))

    y = 0.85
    if a.kicker:
        ax.text(MARGIN, y, a.kicker.upper(), fontproperties=SANS_B, color=ORANGE, fontsize=15, va="top")
        y -= 0.10

    for i, ln in enumerate(title_lines):
        color = "#ffffff" if i == 0 else BLUE
        ax.text(MARGIN, y, ln, fontproperties=SERIF, color=color, fontsize=fs, va="top")
        y -= lh

    if a.subtitle:
        y -= 0.035
        for ln in textwrap.wrap(a.subtitle, width=64):
            ax.text(MARGIN, y, ln, fontproperties=SANS, color=GRAY, fontsize=17, va="top")
            y -= 0.052

    if a.keywords:
        y -= 0.03
        ax.text(MARGIN, y, a.keywords, fontproperties=SANS_B, color="#ffffff", fontsize=16, va="top")

    pie = a.site + (f" · {a.date}" if a.date else "")
    ax.text(MARGIN, 0.06, pie, fontproperties=SANS, color=FAINT, fontsize=13, va="center")

    fig.savefig(a.out, facecolor=NAVY)
    print("escrito:", a.out)


if __name__ == "__main__":
    main()
