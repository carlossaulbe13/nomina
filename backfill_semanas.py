"""
Script de una sola vez: construye el nodo /semanas a partir de los registros
que ya existen en la base.

A partir de ahora create_registro mantiene ese índice solo, pero los registros
creados antes de ese cambio no están reflejados ahí. Sin este backfill el
selector de semanas de la pantalla de nómina saldría vacío para el historial.

Uso: python backfill_semanas.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

import firebase_admin
from firebase_admin import credentials, db
from datetime import date, timedelta

cred = credentials.Certificate(os.environ.get('FIREBASE_CREDENTIALS', 'serviceAccountKey.json'))
firebase_admin.initialize_app(cred, {
    'databaseURL': os.environ.get(
        'FIREBASE_DATABASE_URL',
        'https://nomina-790b9-default-rtdb.firebaseio.com',
    )
})


def _semana(fecha_str):
    # Misma lógica que registros_service._semana (sáb→vie)
    d = date.fromisoformat(fecha_str)
    shifted = d + timedelta(days=2)
    iso = shifted.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


if __name__ == '__main__':
    print("\n=== Backfill del índice /semanas ===\n")

    registros = db.reference('registros').get() or {}
    print(f"  Registros leídos: {len(registros)}")

    semanas = {}
    sin_fecha = 0
    for reg in registros.values():
        fecha = reg.get('fecha')
        if not fecha:
            sin_fecha += 1
            continue
        semanas[_semana(fecha)] = True

    if sin_fecha:
        print(f"  Avisos: {sin_fecha} registro(s) sin campo 'fecha', omitidos")

    if not semanas:
        print("  No hay semanas que escribir. Nada que hacer.\n")
        raise SystemExit(0)

    existentes = db.reference('semanas').get() or {}
    nuevas = sorted(s for s in semanas if s not in existentes)

    print(f"  Semanas encontradas: {len(semanas)}")
    print(f"  Ya en el índice: {len(existentes)}")
    print(f"  Por agregar: {len(nuevas)}")
    if nuevas:
        print("    " + ", ".join(nuevas))
    print()

    if input("  ¿Escribir el índice? (s/n): ").strip().lower() != 's':
        print("\n  Cancelado.\n")
        raise SystemExit(0)

    # update() en vez de set() para no borrar semanas ya presentes.
    db.reference('semanas').update(semanas)
    # Sin caracteres fuera de cp1252: la consola de Windows no los codifica.
    print(f"\n  OK - Indice actualizado con {len(semanas)} semana(s)\n")
