"""
00_explorar_datos.py
---------------------
Script de EXPLORACIÓN inicial. No modifica nada: solo carga el Excel en crudo
y muestra un resumen de cada hoja (tabla) para conocer los datos antes de
empezar a limpiarlos.

Uso:
    source .venv/bin/activate
    python scripts/00_explorar_datos.py
"""

from pathlib import Path

import pandas as pd

# Rutas del proyecto (relativas a la raíz del repo)
RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_CRUDO = RAIZ / "data" / "bronze" / "raw_tables.xlsx"


def explorar():
    print(f"Leyendo: {ARCHIVO_CRUDO}\n")
    libro = pd.ExcelFile(ARCHIVO_CRUDO)

    print(f"El libro tiene {len(libro.sheet_names)} hojas:\n")
    for nombre in libro.sheet_names:
        df = pd.read_excel(libro, nombre)
        nulos = int(df.isna().sum().sum())
        print(f"• {nombre:<20} {df.shape[0]:>4} filas x {df.shape[1]:>2} cols"
              f"  | nulos: {nulos}")


if __name__ == "__main__":
    explorar()
