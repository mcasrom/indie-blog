#!/usr/bin/env python3
"""blog_watchdog_distribucion.py — avisa si un post reciente del blog no se difundió.

Motivo (regla 24): la difusión depende del dueño y el silencio es indistinguible del
fallo. Un post publicado que no se comparte en Mastodon/Bluesky pierde su única vía
de alcance medida. Este watchdog lo detecta y avisa por Telegram.

Cómo: lee los posts de `src/content/posts/*.md` (draft=false) publicados en los
últimos DIAS; para cada uno comprueba si su slug/URL aparece en los últimos estados
de Mastodon (@viajeinteligencia) o en el feed de Bluesky. Si no aparece y ya pasó la
gracia, avisa UNA vez por post (estado en `.blog_watchdog_state.json`).

Uso: python3 scripts/blog_watchdog_distribucion.py [--dry] [--list]
Cron sugerido: 0 9,18 * * *  (dos veces al día; cubre publicaciones de mañana/tarde)
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BLOG = "/home/deploy/analisis-pruebapublica"
POSTS = os.path.join(BLOG, "src", "content", "posts")
SP_ENV = "/home/deploy/social-poster/.env"            # Mastodon + Bluesky
FIMI_ENV = "/home/deploy/hybrid-fimi-radar/.env"      # Telegram
STATE = "/home/deploy/scripts/.blog_watchdog_state.json"
BASE_URL = "https://analisis-pruebapublica.com/posts/"
DIAS = 7          # ventana de posts a vigilar
GRACIA_H = 12     # horas mínimas desde la publicación antes de avisar
UA = "Mozilla/5.0 (compatible; blog-watchdog/1.0)"
DRY = "--dry" in sys.argv
LIST = "--list" in sys.argv


def _env(path):
    out = {}
    try:
        for ln in open(path, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                v = v.strip()
                if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                    v = v[1:-1]
                out[k.strip()] = v
    except OSError:
        pass
    return out


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def posts_recientes():
    ahora = datetime.now(timezone.utc)
    out = []
    for fn in sorted(os.listdir(POSTS)):
        if not fn.endswith(".md"):
            continue
        txt = open(os.path.join(POSTS, fn), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", txt, re.S)
        fm = m.group(1) if m else ""

        def f(k):
            mm = re.search(rf"^{k}:\s*(.+)$", fm, re.M)
            return mm.group(1).strip().strip('"').strip("'") if mm else None

        if (f("draft") or "false").lower() == "true":
            continue
        pub = f("pubDate")
        if not pub:
            continue
        try:
            dt = datetime.strptime(pub[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        edad_h = (ahora - dt).total_seconds() / 3600
        if 0 <= edad_h <= DIAS * 24:
            out.append({"slug": fn[:-3], "title": f("title") or fn[:-3],
                        "pubDate": pub[:10], "edad_h": edad_h})
    return out


def mastodon_textos():
    env = _env(SP_ENV)
    inst = env.get("MASTODON_INSTANCE", "https://mastodon.social").rstrip("/")
    tok = env.get("MASTODON_TOKEN", "")
    if not tok:
        return ""
    h = {"Authorization": "Bearer " + tok, "User-Agent": UA}
    acc = _get(inst + "/api/v1/accounts/verify_credentials", h)
    st = _get(inst + f"/api/v1/accounts/{acc['id']}/statuses?limit=40&exclude_replies=true", h)
    return " ".join((s.get("content") or "") for s in st)


def bluesky_textos():
    env = _env(SP_ENV)
    handle = env.get("BSKY_USER", "")
    if not handle:
        return ""
    feed = _get("https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
                f"?actor={urllib.parse.quote(handle)}&limit=50")
    out = []
    for it in feed.get("feed", []):
        rec = (it.get("post") or {}).get("record") or {}
        out.append(rec.get("text") or "")
    return " ".join(out)


def telegram(msg):
    env = _env(FIMI_ENV)
    tok = env.get("FIMI_TELEGRAM_BOT_TOKEN", "")
    chat = env.get("FIMI_OWNER_CHAT") or env.get("FIMI_TELEGRAM_CHAT_ID", "")
    if not tok or not chat:
        print("[watchdog] sin token/chat Telegram", file=sys.stderr)
        return False
    data = json.dumps({"chat_id": chat, "text": msg, "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/sendMessage",
                                 data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception as e:  # noqa: BLE001
        print(f"[watchdog] Telegram fallo: {e}", file=sys.stderr)
        return False


def main():
    try:
        masto = mastodon_textos()
    except Exception as e:  # noqa: BLE001
        masto = ""
        print(f"[watchdog] Mastodon no leíble: {e}", file=sys.stderr)
    try:
        bsky = bluesky_textos()
    except Exception as e:  # noqa: BLE001
        bsky = ""
        print(f"[watchdog] Bluesky no leíble: {e}", file=sys.stderr)

    if not masto and not bsky:
        print("[watchdog] no se pudo leer ninguna red; no se avisa (evita falso positivo)",
              file=sys.stderr)
        return 0

    posts = posts_recientes()
    if LIST:
        for p in posts:
            seen = p["slug"] in masto or p["slug"] in bsky
            print(f"{p['pubDate']}  edad {p['edad_h']:5.1f} h  "
                  f"{'DIFUNDIDO' if seen else 'SIN DIFUNDIR'}  {p['slug']}")
        return 0

    try:
        estado = json.load(open(STATE, encoding="utf-8"))
    except (OSError, ValueError):
        estado = {}
    alertados = estado.get("alertados", {})
    nuevos = []
    for p in posts:
        if p["slug"] in alertados:
            continue
        if p["edad_h"] < GRACIA_H:
            continue
        if p["slug"] in masto or p["slug"] in bsky:
            continue
        nuevos.append(p)

    if not nuevos:
        print(f"[watchdog] ok · {len(posts)} posts en ventana, todos difundidos o en gracia")
        return 0

    lineas = ["⚠️ Blog: post(s) sin difundir en Mastodon/Bluesky (pasada la gracia):", ""]
    for p in nuevos:
        lineas.append(f"· {p['title']} ({p['pubDate']}, {p['edad_h']:.0f} h)")
        lineas.append(f"  {BASE_URL}{p['slug']}/")
        alertados[p["slug"]] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    msg = "\n".join(lineas)
    print(msg)
    if not DRY and telegram(msg):
        estado["alertados"] = alertados
        tmp = STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(estado, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, STATE)
        print(f"[watchdog] avisado Telegram ({len(nuevos)} post/s)")
    elif DRY:
        print("[watchdog] --dry: no se envía ni se marca estado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
