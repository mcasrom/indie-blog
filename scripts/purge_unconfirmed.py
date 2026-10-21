#!/usr/bin/env python3
"""Purga de suscriptores NO confirmados (doble opt-in incompleto) tras N días.
Uso: python3 scripts/purge_unconfirmed.py [--dias 30] [--dry]
RGPD: no se conserva un email sin consentimiento confirmado más de lo necesario.
"""
import sqlite3, sys
from datetime import datetime, timedelta, timezone

DB = "/home/deploy/analisis-pruebapublica/data/analisis.db"
DIAS = 30
if "--dias" in sys.argv:
    DIAS = int(sys.argv[sys.argv.index("--dias") + 1])
DRY = "--dry" in sys.argv

cutoff = (datetime.now(timezone.utc) - timedelta(days=DIAS)).isoformat()
con = sqlite3.connect(DB)
con.execute("PRAGMA busy_timeout=5000")
n = con.execute("SELECT COUNT(*) FROM subscribers WHERE confirmado=0 AND fecha < ?", (cutoff,)).fetchone()[0]

if DRY:
    print(f"[dry] borraría {n} no confirmados con fecha < {cutoff[:10]} (> {DIAS} d)")
    sys.exit(0)

con.execute("DELETE FROM subscribers WHERE confirmado=0 AND fecha < ?", (cutoff,))
con.commit()
resto = con.execute("SELECT COUNT(*) FROM subscribers WHERE confirmado=0").fetchone()[0]
print(f"[{datetime.now(timezone.utc):%Y-%m-%d %H:%M}] purga: {n} no confirmados > {DIAS} d eliminados · quedan {resto} sin confirmar")
