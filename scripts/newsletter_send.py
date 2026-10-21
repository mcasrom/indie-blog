#!/usr/bin/env python3
"""newsletter_send.py — envía el boletín del blog a los suscriptores CONFIRMADOS.

Lee los posts recientes del RSS del blog, monta un correo HTML y lo envía por
Resend (clave en /home/deploy/newsletter/.env). Cada envío lleva enlace de baja.

Uso:
    python3 scripts/newsletter_send.py            # envía a los confirmados
    python3 scripts/newsletter_send.py --dry      # no envía, imprime el resumen
    python3 scripts/newsletter_send.py --test tu@email.com   # un solo envío
    python3 scripts/newsletter_send.py --dias 31 --max 8

Cron sugerido: 0 8 1 * *  (el día 1 de cada mes)
"""
from __future__ import annotations
import html
import json
import sqlite3
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

DB = "/home/deploy/analisis-pruebapublica/data/analisis.db"
ENV = "/home/deploy/newsletter/.env"
RSS = "https://analisis.pruebapublica.com/rss.xml"
BASE = "https://analisis.pruebapublica.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120"
SUBJECT = "Análisis — lo último que he publicado"

ARGS = sys.argv[1:]
DRY = "--dry" in ARGS
TEST = ARGS[ARGS.index("--test") + 1] if "--test" in ARGS else None
DIAS = int(ARGS[ARGS.index("--dias") + 1]) if "--dias" in ARGS else 31
MAX = int(ARGS[ARGS.index("--max") + 1]) if "--max" in ARGS else 8


def env():
    out = {}
    for ln in open(ENV, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def posts():
    req = urllib.request.Request(RSS, headers={"User-Agent": UA})
    xml = urllib.request.urlopen(req, timeout=30).read()
    root = ET.fromstring(xml)
    out = []
    for it in root.iter():
        if it.tag.split("}")[-1] != "item":
            continue
        g = {}
        for ch in it:
            g[ch.tag.split("}")[-1]] = (ch.text or "").strip()
        link = g.get("link", "")
        if not link:
            continue
        out.append({"title": g.get("title", ""), "link": link,
                    "desc": g.get("description", "")})
        if len(out) >= MAX:
            break
    return out


def correo(ps, sid):
    items = "".join(
        f'<li style="margin:0 0 16px"><a href="{html.escape(p["link"])}?utm_source=newsletter&utm_medium=email" '
        f'style="font-size:17px;font-weight:700;color:#0f766e;text-decoration:none">{html.escape(p["title"])}</a>'
        f'<br><span style="color:#475569;font-size:14px">{html.escape(p["desc"])}</span></li>'
        for p in ps)
    baja = f"{BASE}/api/unsubscribe?id={sid}"
    return f"""<!doctype html><html lang="es"><body style="margin:0;background:#f8fafc">
<div style="max-width:600px;margin:0 auto;padding:28px 22px;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1e293b">
<p style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#0f766e;font-weight:700;margin:0 0 6px">Análisis</p>
<h1 style="font-size:22px;margin:0 0 4px">Geopolítica desde España, sin agenda</h1>
<p style="color:#475569;margin:0 0 22px">Esto es lo que he publicado últimamente:</p>
<ul style="list-style:none;padding:0;margin:0">{items}</ul>
<hr style="border:none;border-top:1px solid #e2e8f0;margin:22px 0">
<p style="font-size:12px;color:#94a3b8;line-height:1.6">Recibes este correo porque te suscribiste en
<a href="{BASE}" style="color:#0f766e">analisis.pruebapublica.com</a>.<br>
<a href="{baja}" style="color:#94a3b8">Darse de baja</a>.</p>
</div></body></html>"""


def send(to, html_body, cfg):
    data = json.dumps({"from": cfg["RESEND_FROM"], "to": [to],
                       "subject": SUBJECT, "html": html_body}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=data,
                                 headers={"Authorization": "Bearer " + cfg["RESEND_API_KEY"],
                                          "Content-Type": "application/json",
                                          "User-Agent": "analisis-newsletter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def main():
    cfg = env()
    if not cfg.get("RESEND_API_KEY"):
        print("[newsletter] sin RESEND_API_KEY", file=sys.stderr)
        return 1
    ps = posts()
    print(f"[newsletter] {len(ps)} posts en el boletín")
    con = sqlite3.connect(DB)
    if TEST:
        subs = [(TEST, "test")]
    else:
        subs = con.execute("SELECT email, id FROM subscribers WHERE confirmado=1 AND (temas IS NULL OR temas='')").fetchall()
    print(f"[newsletter] {len(subs)} destinatario(s) confirmado(s)")
    if DRY:
        prev = "/home/deploy/analisis-pruebapublica/scripts/newsletter_preview.html"
        with open(prev, "w", encoding="utf-8") as f:
            f.write(correo(ps, "PREVIEW"))
        print(f"[newsletter] preview -> {prev}")
        for p in ps:
            print("  -", p["title"])
        return 0
    envios = 0
    for email, sid in subs:
        try:
            st = send(email, correo(ps, sid), cfg)
            print(f"[newsletter] {email}: {st}")
            if st == 200:
                envios += 1
        except Exception as e:  # noqa: BLE001
            print(f"[newsletter] {email}: ERROR {e}", file=sys.stderr)
    print(f"[newsletter] enviados {envios}/{len(subs)} · {datetime.now(timezone.utc):%F %T}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
