#!/usr/bin/env python3
"""gen_rey_illus.py — ilustración de la 5.ª fábula: «El trono y la casa».
Un trono (poder personal) sobre una casa sostenida por columnas (instituciones).
Estilo de la casa: navy + naranja.
Uso: /usr/bin/python3 gen_rey_illus.py --out public/rey-instituciones-fabula.png
"""
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.font_manager import FontProperties

NAVY = "#0f172a"
ORANGE = "#F97316"
BLUE = "#38bdf8"
GRAY = "#94a3b8"
SERIF = FontProperties(family="DejaVu Serif", weight="bold")
SANS = FontProperties(family="DejaVu Sans")
SANS_B = FontProperties(family="DejaVu Sans", weight="bold")

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()

fig = plt.figure(figsize=(12, 6.3), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.set_xlim(0, 12); ax.set_ylim(0, 6.3)
fig.patch.set_facecolor(NAVY)

# título
ax.text(0.5, 5.85, "El trono y la casa", color="#fff", fontproperties=SERIF, fontsize=30)
ax.text(0.5, 5.42, "El problema no es quién ocupa el trono, sino qué puede hacer quien se sienta en él.",
        color=GRAY, fontproperties=SANS, fontsize=13)

# columnas (instituciones)
cols = ["LEYES", "TRIBUNALES", "PRENSA", "ELECCIONES"]
x0, w, gap = 2.0, 1.3, 0.5
base_y, col_h = 1.15, 2.15
for i, lab in enumerate(cols):
    x = x0 + i * (w + gap)
    ax.add_patch(Rectangle((x, base_y), w, col_h, facecolor="#334155", edgecolor=BLUE, lw=1.5))
    # capitel y basa
    ax.add_patch(Rectangle((x - 0.12, base_y + col_h), w + 0.24, 0.16, facecolor=BLUE))
    ax.add_patch(Rectangle((x - 0.12, base_y - 0.16), w + 0.24, 0.16, facecolor=BLUE))
    ax.text(x + w / 2, base_y - 0.5, lab, color=GRAY, fontproperties=SANS_B, fontsize=11, ha="center")

# dintel + tejado
ax.add_patch(Rectangle((1.75, base_y + col_h + 0.16), 6.9, 0.3, facecolor="#475569"))
roof = Polygon([[1.6, base_y + col_h + 0.46], [10.6, base_y + col_h + 0.46], [6.1, base_y + col_h + 1.7]],
               closed=True, facecolor="#1e293b", edgecolor=ORANGE, lw=0)
ax.add_patch(roof)

# corona (poder personal) sobre el tejado
cy = base_y + col_h + 2.0
crown = Polygon([[5.35, cy], [5.35, cy + 0.55], [5.7, cy + 0.3], [6.1, cy + 0.7],
                 [6.5, cy + 0.3], [6.85, cy + 0.55], [6.85, cy]],
                closed=True, facecolor=ORANGE, edgecolor=ORANGE)
ax.add_patch(crown)
ax.add_patch(Rectangle((5.35, cy - 0.12), 1.5, 0.14, facecolor=ORANGE))

# etiqueta corona
ax.text(6.1, cy + 0.95, "PODER", color=ORANGE, fontproperties=SANS_B, fontsize=12, ha="center")
ax.text(6.1, cy - 0.55, "quien manda", color=GRAY, fontproperties=SANS, fontsize=10, ha="center")

# leyenda inferior
ax.text(6.0, 0.45, "Instituciones: lo que permanece cuando cambia quien manda.",
        color="#e2e8f0", fontproperties=SERIF, fontsize=15, ha="center")
fig.savefig(a.out, facecolor=NAVY)
print("OK", a.out)
