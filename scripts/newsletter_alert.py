#!/usr/bin/env python3
"""newsletter_alert.py — digest segmentado por temas ("te aviso de X").

Reparte los suscriptores CONFIRMADOS en dos grupos que no se solapan:
  - con temas elegidos -> UNA sola persona recibe UN solo correo con los posts
    nuevos (ventana --dias) de SUS temas. No un correo por tema: no spam.
  - sin temas (``temas=''``) -> los cubre el resumen mensual (newsletter_send.py).

Silencio informativo: si un suscriptor no tiene posts nuevos de sus temas en la
ventana, no recibe nada.

Uso:
    python3 scripts/newsletter_alert.py                 # 7 días, a los de temas
    python3 scripts/newsletter_alert.py --dias 14
    python3 scripts/newsletter_alert.py --dry           # preview, sin enviar
    python3 scripts/newsletter_alert.py --test tu@email.com

Cron sugerido: 0 8 * * 4  (jueves), o al ritmo que se publique.
"""
from __future__ import annotations
import html
import json
import os
import re
import sqlite3
import sys
import urllib.request
from datetime import datetime, timezone

BLOG = "/home/deploy/analisis-pruebapublica"
POSTS_DIR = os.path.join(BLOG, "src", "content", "posts")
DB = os.path.join(BLOG, "data", "analisis.db")
ENV = "/home/deploy/newsletter/.env"
BASE = "https://analisis.pruebapublica.com"
UA = "Mozilla/5.0 (compatible; analisis-alertas/1.0)"

TEMAS = {
    "fronteras-y-migraciones": ["ceuta", "melilla", "frontera sur", "crisis migratoria",
                                "migraciones", "fronteras", "sáhara occidental", "sahara occidental", "magreb"],
    "defensa": ["defensa", "amenazas híbridas", "otan", "disuasión", "gasto en defensa"],
    "geopolitica-101": [],
    "energia": ["energía", "petróleo", "opep", "oleoductos", "gasoductos", "corredor medio", "transcaspio"],
    "comercio-y-aranceles": ["aranceles", "comercio", "proteccionismo", "economía política",
                             "política económica", "historia económica", "comercio marítimo"],
    "infraestructura-critica": ["cables submarinos", "infraestructura crítica", "infraestructura",
                                "interdependencia", "espacio", "satélites", "pld space"],
    "fimi": ["fimi", "observatorio", "amplificación", "desinformación", "interferencia"],
    "fabulas": [],
}
SERIES = {"Geopolítica 101": "geopolitica-101", "Fábulas del análisis": "fabulas"}
ETIQUETA = {
    "fronteras-y-migraciones": "Ceuta, fronteras y migraciones", "defensa": "Defensa y amenazas híbridas",
    "geopolitica-101": "Geopolítica 101", "energia": "Energía y materias primas",
    "comercio-y-aranceles": "Comercio y aranceles",
    "infraestructura-critica": "Infraestructura crítica", "fimi": "Observatorio FIMI", "fabulas": "Fábulas y método",
}

ARGS = sys.argv[1:]
DRY = "--dry" in ARGS
TEST = ARGS[ARGS.index("--test") + 1] if "--test" in ARGS else None
DIAS = int(ARGS[ARGS.index("--dias") + 1]) if "--dias" in ARGS else 7


def env():
    out = {}
    for ln in open(ENV, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _fm(path):
    txt = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", txt, re.S)
    fm = m.group(1) if m else ""

    def one(k):
        mm = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
        return mm.group(1).strip().strip('"').strip("'") if mm else ""

    def tags():
        mm = re.search(r"^tags:\s*\[(.*?)\]", fm, re.M)
        return [t.strip().strip('"').strip("'").lower() for t in mm.group(1).split(",") if t.strip()] if mm else []

    return {"slug": os.path.basename(path)[:-3], "title": one("title"), "description": one("description"),
            "pubDate": one("pubDate")[:10], "serie": one("serie"), "draft": one("draft").lower() == "true",
            "tags": tags()}


def pertenece(p, tema):
    if p["serie"] and SERIES.get(p["serie"]) == tema:
        return True
    return any(t in TEMAS.get(tema, []) for t in p["tags"])


def posts_recientes(dias):
    ahora = datetime.now(timezone.utc)
    out = []
    for fn in os.listdir(POSTS_DIR):
        if not fn.endswith(".md"):
            continue
        p = _fm(os.path.join(POSTS_DIR, fn))
        if p["draft"] or not p["pubDate"]:
            continue
        try:
            dt = datetime.strptime(p["pubDate"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if (ahora - dt).days <= dias:
            out.append(p)
    return sorted(out, key=lambda x: x["pubDate"], reverse=True)


def correo(ps, sid, temas):
    items = "".join(
        f'<li style="margin:0 0 16px"><a href="{html.escape(BASE)}/posts/{html.escape(p["slug"])}/'
        f'?utm_source=newsletter&utm_medium=email" style="font-size:17px;font-weight:700;color:#0f766e;'
        f'text-decoration:none">{html.escape(p["title"])}</a><br>'
        f'<span style="color:#475569;font-size:14px">{html.escape(p["description"])}</span></li>'
        for p in ps)
    temas_txt = ", ".join(ETIQUETA.get(t, t) for t in temas) if temas else "todos los temas"
    baja = f"{BASE}/api/unsubscribe?id={sid}"
    return f"""<!doctype html><html lang="es"><body style="margin:0;background:#f8fafc">
<div style="max-width:600px;margin:0 auto;padding:28px 22px;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1e293b">
<p style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#0f766e;font-weight:700;margin:0 0 6px">Análisis · tus temas</p>
<h1 style="font-size:22px;margin:0 0 4px">Lo nuevo de lo que sigues</h1>
<p style="color:#475569;margin:0 0 22px">Temas: <b>{html.escape(temas_txt)}</b>.</p>
<ul style="list-style:none;padding:0;margin:0">{items}</ul>
<hr style="border:none;border-top:1px solid #e2e8f0;margin:22px 0">
<p style="font-size:12px;color:#94a3b8;line-height:1.6">Recibes esto porque elegiste estos temas en
<a href="{BASE}" style="color:#0f766e">analisis.pruebapublica.com</a>.<br>
<a href="{baja}" style="color:#94a3b8">Darse de baja</a>.</p>
</div></body></html>"""


def send(to, subject, html_body, cfg):
    data = json.dumps({"from": cfg["RESEND_FROM"], "to": [to], "subject": subject,
                       "html": html_body}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=data,
                                 headers={"Authorization": "Bearer " + cfg["RESEND_API_KEY"],
                                          "Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def main():
    cfg = env()
    if not cfg.get("RESEND_API_KEY"):
        print("[alertas] sin RESEND_API_KEY", file=sys.stderr)
        return 1
    todos = posts_recientes(DIAS)
    print(f"[alertas] {len(todos)} post(s) en {DIAS} d")
    con = sqlite3.connect(DB)
    if TEST:
        subs = [(TEST, "test", "fimi,energia")]
    else:
        subs = con.execute(
            "SELECT email, id, temas FROM subscribers WHERE confirmado=1 AND temas<>''").fetchall()
    print(f"[alertas] {len(subs)} suscriptor(es) con temas")
    enviados = 0
    for email, sid, temas_csv in subs:
        temas = [t for t in (temas_csv or "").split(",") if t]
        ps = [p for p in todos if any(pertenece(p, t) for t in temas)] if temas else todos
        if not ps:
            continue
        asunto = f"Análisis · lo nuevo de tus temas ({len(ps)})"
        if DRY:
            prev = os.path.join(BLOG, "scripts", "newsletter_alert_preview.html")
            with open(prev, "w", encoding="utf-8") as fh:
                fh.write(correo(ps, sid, temas))
            print(f"[alertas] preview ({email}, temas={temas_csv}) -> {prev}")
            for p in ps:
                print("  -", p["title"])
            continue
        try:
            st = send(email, asunto, correo(ps, sid, temas), cfg)
            print(f"[alertas] {email}: {st} ({len(ps)} post/s)")
            if st == 200:
                enviados += 1
        except Exception as e:  # noqa: BLE001
            print(f"[alertas] {email}: ERROR {e}", file=sys.stderr)
    print(f"[alertas] enviados {enviados}/{len(subs)} · {datetime.now(timezone.utc):%F %T}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
